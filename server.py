from settings import settings
from utility import sys_pause, parser
from threads import *



def main():
    # data = b'\x1a^\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x06vortex\x04data\tmicrosoft\x03com\x00\x00\x01\x00\x01'
    # udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # udpSocket.bind(("0.0.0.0", 7989))
    # udpSocket.sendto(data, settings.remote_host)
    # sys_pause()
    w = worker(settings.max_queue_size)
    threading.Thread(target=w.consumer).start()
    threading.Thread(target=w.receiver).start()
    max_buffer_size = settings.max_buffer_size

    while True:
        request, addr = server_socket.recvfrom(max_buffer_size)
        # print('haha')
        parse = parser(request)
        print(parse.QNAME)
        # print(request)
        threading.Thread(target=w.producer, args=(request, addr)).start()

if __name__ == '__main__':
    main()