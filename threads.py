import socket
import threading
import queue
import time
from settings import settings
from localdns import localdns
from utility import parser

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(settings.local_host)

post_sockets = []
for post_host in settings.post_host:
    p_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    p_socket.bind(post_host)
    p_socket.connect(settings.remote_host)
    post_sockets.append(p_socket)


class worker:
    '''
    Procedures to handle concurrent queries.
    '''
    def __init__(self, max_queue_size, max_buffer_size, log_level=1):
        self.queue = queue.Queue(max_queue_size)
        self.ID_to_addr = dict()
        self.dict_lock = threading.Lock()
        self.print_lock = threading.Lock()
        self.max_buffer_size = max_buffer_size
        self.log_level = log_level

    def th_print(self, message):
        '''
        In order to maintain thread safe print.
        '''
        if self.log_level != 0:
            self.print_lock.acquire()
            print(message)
            self.print_lock.release()

    def producer(self, request, addr):
        '''
        Try to handle a DNS request with local DNS and decide whether turn to remote DNS for help.
        '''
        t_start = time.time()
        t_end = 0
        parse = parser(request)

        response_found, response = localdns.nslookup(request)
        if response_found:
            parse = parser(response)
            intercept = False
            if parse.RCODE == 0x0003:
                intercept = True

            server_socket.sendto(response, addr)
            t_end = time.time()
            message = '[' + ('intercept' if intercept else 'local resolve')+']\t{}, using {}ms.'.format(parse.QNAME, int((t_end - t_start) * 100000)/100)
            self.th_print(message)
            
        else:
            self.dict_lock.acquire()
            try:
                self.ID_to_addr[parse.ID] = [addr, t_start]
            finally:
                self.dict_lock.release()
            self.queue.put(request)

    def consumer(self, post_socket):
        '''
        Send a request to remote DNS server.
        '''
        while True:
            request = self.queue.get()
            post_socket.send(request)
            
    def receiver(self, post_socket):
        '''
        Receive response from remote DNS server.
        '''
        while True:
            flag = True             # to handle ConnectionResetError:[WinError10054]
            while flag:
                try:
                    response = post_socket.recv(self.max_buffer_size)
                    flag = False
                except:
                    flag = True
            parse = parser(response)
            addr, t_start = self.ID_to_addr[parse.ID]
            server_socket.sendto(response, addr)
            t_end = time.time()

            message = '[Relay]\t{}, using {}ms.'.format(parse.QNAME, int((t_end - t_start) * 100000)/100)
            self.th_print(message)