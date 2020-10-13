from settings import settings
from utility import parser

class file:
    '''
    Read settings and load host file.
    '''
    def __init__(self, hosts='hosts', log_level=1):
        self.addr_dict = dict()

        with open(hosts, 'r') as f:
            for line in f.readlines():
                ip, addr = line.strip().split()
                if self.addr_dict.__contains__(addr):
                    self.addr_dict[addr].append(ip)
                else:
                    self.addr_dict[addr] = list([ip])

        if log_level != 0:
            print('local dns:\n', self.addr_dict)
            print('*' * 20)
    
    def lookup(self, addr):
        '''
        Try to find ip address correspondes to addr in local data.
        '''
        if self.addr_dict.__contains__(addr):
            return True, self.addr_dict[addr]
        return False, list()


class dns(file):
    def nslookup(self, request):
        '''
        Try to handle DNS request with local dns.
        '''
        parse = parser(request)
        response = bytearray(request)

        if parse.QTYPE != 0x01:         # ignore ipv6 type request, turn to remote dns for help
            return False, None

        flag, ip = self.lookup(parse.QNAME)
        if flag == False:               # QNAME not found
            return False, None
        else:
            response[2] |= 0x80         # set QR=1
            if '0.0.0.0' in ip:         # request blocked
                response[3] &= 0xf0
                response[3] |= 0x03     # set RCODE=3
            else:
                n_ip = len(ip)

                def construct_resource_record(ip):
                    ret = bytearray()
                    ret += bytearray.fromhex('c00c')    # set RNAME
                    ret += bytearray.fromhex('0001')    # set RTYPE
                    ret += bytearray.fromhex('0001')    # set RCLASS
                    ret += bytearray.fromhex('0002a300')   # set TLL=24*3600sec
                    ret += bytearray.fromhex('0004')    # set RDLENGTH

                    lst = ip.split('.')                 # construct RDATA
                    for byte in lst:            
                        ret.append(int(byte))           
                    return ret

                for i in range(n_ip):
                    response += construct_resource_record(ip[i])
                
                response[6] = (n_ip & 0xff00) >> 8      # set ANCOUNT
                response[7] = n_ip & 0x00ff             

            response = bytes(response)
            return True, response

localdns = dns(settings.hosts, settings.log_level)