from utility import sys_pause	
from enum import IntEnum

class LOG_LEVEL(IntEnum):
    OFF = 0
    LOW = 1
    HIGH = 2

class conf:
    level_map = {'OFF':LOG_LEVEL.OFF, 'LOW':LOG_LEVEL.LOW, 'HIGH':LOG_LEVEL.HIGH}

    def __init__(self, path='./conf.ini'):
        self.local_host = tuple()
        self.remote_host = tuple()
        self.log_level = LOG_LEVEL.LOW
        self.hosts = './hosts'
        self.max_queue_size = 1024
        self.max_buffer_size = 4096


        import configparser
        config = configparser.ConfigParser()
        config.read(path)
        
        local_addr = '127.0.0.1'
        remote_addr = '114.114.114.114'
        port = 53
        post_port = 1314
        if config.has_section('SERVER_CONFIG'):
            if config.has_option('SERVER_CONFIG', 'DNS_PORT'):
                port = config.getint('SERVER_CONFIG', 'DNS_PORT')
            if config.has_option('SERVER_CONFIG', 'POST_PORT'):
                post_port = config.getint('SERVER_CONFIG', 'POST_PORT')
            if config.has_option('SERVER_CONFIG', 'LOCAL_HOST'):
                local_addr = config.get('SERVER_CONFIG', 'LOCAL_HOST')
            if config.has_option('SERVER_CONFIG', 'REMOTE_HOST'):
                remote_addr = config.get('SERVER_CONFIG', 'REMOTE_HOST')
        
        if config.has_section('I/O_CONFIG'):
            if config.has_option('I/O_CONFIG', 'LOG_LEVEL'):
                self.log_level = conf.level_map[config.get('I/O_CONFIG', 'LOG_LEVEL')]
            if config.has_option('I/O_CONFIG', 'DNSRELAY_FILE'):
                self.hosts = config.get('I/O_CONFIG', 'DNSRELAY_FILE')
        
        if config.has_section('THREADING'):
            if config.has_option('THREADING', 'MAX_QUEUE_SIZE'):
                self.max_queue_size = config.getint('THREADING', 'MAX_QUEUE_SIZE')
            if config.has_option('THREADING', 'MAX_BUFFER_SIZE'):
                self.max_buffer_size = config.getint('THREADING', 'MAX_BUFFER_SIZE')
        
        self.local_host = ("", port)
        self.post_host = ("", post_port)
        self.remote_host = (remote_addr, port)

        self.show_info()

    def show_info(self):
        print('*' * 20)
        print('local host:\t', self.local_host)
        print('remote host:\t', self.remote_host)
        print('post host:\t', self.post_host)
        print('log level:\t', self.log_level)
        print('host file:\t', self.hosts)
        print('max queue size:\t', self.max_queue_size)
        print('max buffer size:\t', self.max_buffer_size)
        print('*' * 20)

settings = conf()