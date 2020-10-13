from settings import settings
from utility import parser

class file:
    def __init__(self):
        self.addr_dict = dict()

        with open(settings.hosts, 'r') as f:
            for line in f.readlines():
                ip, addr = line.strip().split()
                if self.addr_dict.__contains__(addr):
                    self.addr_dict[addr].append(ip)
                else:
                    self.addr_dict[addr] = list([ip])
        print(self.addr_dict)
    
    def lookup(self, addr):
        if self.addr_dict.__contains__(addr):
            return True, self.addr_dict[addr]
        return False, list()

class dns(file):
    def nslookup(self, request):
        parse = parser(request)
        response = bytearray(request)

        print(parse.QNAME)
        flag, ip = self.lookup(parse.QNAME)
        if flag == False:
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
                    ret += bytearray.fromhex('c00c')    # RNAME
                    ret += bytearray.fromhex('0001')    # RTYPE
                    ret += bytearray.fromhex('0001')    # RCLASS
                    ret += bytearray.fromhex('0002a300')   # TLL=24*3600sec
                    ret += bytearray.fromhex('0004')    # RDLENGTH
                    lst = ip.split('.')
                    for byte in lst:
                        ret.append(int(byte))           #RDATA
                    # print(ret)
                    return ret

                for i in range(n_ip):
                    response += construct_resource_record(ip[i])

                    # if response[7]==0xFF:
                    #     response[6]+=1
                    #     response[7]=0
                    # else:
                    #     response[7]+=1
                
                response[6] = (n_ip & 0xff00) >> 8
                response[7] = n_ip & 0x00ff

            response = bytes(response)
            print(response)
            return True, response

localdns = dns()