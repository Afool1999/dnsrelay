import socket
import threading
import queue
import time
from settings import settings
from localdns import localdns
from utility import parser

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(settings.local_host)

post_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
post_socket.bind(settings.post_host)
post_socket.connect(settings.remote_host)

class worker:
    def __init__(self, max_queue_size):
        self.queue = queue.Queue(max_queue_size)
        self.ID_to_addr = dict()
        self.lock_dict = threading.Lock()
        self.max_buffer_size = settings.max_buffer_size

    def producer(self, request, addr):
        t_start = time.time()
        t_end = 0
        parse = parser(request)
        # print(parse.QNAME)
        if parse.QTYPE == 0x1c:     # skip ipv6 request
            # print(parse.QNAME)
            return

        response_found, response = localdns.nslookup(request)
        if response_found:
            print(addr)
            server_socket.sendto(response, addr)
            t_end = time.time()
            print('found {} in local, using {}ms.'.format(parse.QNAME, (t_end - t_start) * 1000))
        else:
            self.lock_dict.acquire()
            try:
                self.ID_to_addr[parse.ID] = [addr, t_start]
            finally:
                # print('producer', request)
                self.lock_dict.release()
            self.queue.put(request)
            


    def consumer(self):
        while True:
            request = self.queue.get()
            # print('consumer:', request)
            # print(settings.remote_host, request)
            post_socket.send(request)
            
    def receiver(self):
        while True:
            response = post_socket.recv(self.max_buffer_size)
            parse = parser(response)
            print('receiver:', parse.QNAME)
            addr, t_start = self.ID_to_addr[parse.ID]
            server_socket.sendto(response, addr)
            t_end = time.time()
            print('found {} in remote, using {}ms.'.format(parse.QNAME, (t_end - t_start) * 1000))
            # time.sleep(0.05)