from settings import settings
from threads import server_socket, post_sockets, worker, threading

def main():
    w = worker(settings.max_queue_size, settings.max_buffer_size, settings.log_level)
    threading_pool = []
    threading_pool += [threading.Thread(target=w.consumer, args=[socket]) for socket in post_sockets]
    threading_pool += [threading.Thread(target=w.receiver, args=[socket]) for socket in post_sockets]
    max_buffer_size = settings.max_buffer_size
    for thd in threading_pool:
        thd.start()

    while True:
        flag = True             # to handle ConnectionResetError:[WinError10054]
        while flag:
            try:
                request, addr = server_socket.recvfrom(max_buffer_size)
                flag = False
            except:
                flag = True

        thd = threading.Thread(target=w.producer, args=(request, addr))
        thd.start()
    
    for thd in threading_pool:
        thd.join()

if __name__ == '__main__':
    main()