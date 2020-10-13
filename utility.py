import os

def sys_pause():
    os.system("pause")

class parser:
    def __init__(self, message):
        self.message = bytearray(message)
        self.ID = 0
        self.QR = 0
        self.OPCODE = 0
        self.AA = 0
        self.TC = 0
        self.RD = 0
        self.RA = 0
        self.Z = 0
        self.RCODE = 0
        self.QDCOUNT = 0
        self.ANCOUNT = 0
        self.NSCOUNT = 0
        self.ARCOUNT = 0
        
        self.QNAME = ''
        self.QTYPE = 0
        self.QCLASS = 0
        
        self.RNAME = list()
        self.RTYPE = list()
        self.RCLASS = list()
        self.TTL = list()
        self.RDLENGTH = list()
        self.RDATA = list()
        self.parse_HEADER()

        pos = 12
        pos = self.parse_QUESTION(pos)
        # no need to parse response
        # pos = self.parse_RESPONSE(pos)


    def parse_HEADER(self):
        self.ID = (self.message[0]<<8) + self.message[1]
        self.QR = (self.message[2] & 0x80) >> 7
        self.OPCODE = (self.message[2] & 0x78) >> 3
        self.AA = (self.message[2] & 0x04) >> 2
        self.TC = (self.message[2] & 0x02) >> 1
        self.RD = (self.message[2] & 0x01) >> 0
        self.RA = (self.message[3] & 0x80) >> 7
        self.Z = (self.message[3] & 0x70) >> 4
        self.RCODE = (self.message[3] & 0x0f) >> 0
        self.QDCOUNT = (self.message[4]<<8) + self.message[5]
        self.ANCOUNT = (self.message[6]<<8) + self.message[7]
        self.NSCOUNT = (self.message[8]<<8) + self.message[9]
        self.ARCOUNT = (self.message[10]<<8) + self.message[11]

    def parse_domain(self, pos):
        # if self.QR == 1 or self.QR == 0:
        #     print()
        #     if (len(self.RTYPE)>0):
        #         print(pos, self.RTYPE[-1])
        #     print(self.message)
        lst = list()
        while self.message[pos] != 0:
            if self.message[pos] == 0xc0:
                pos += 2
                break
            length = self.message[pos]
            # print(length, end=' ')
            # if (length > 40):
            #     print(self.message)
            # print(self.message[pos + 1:pos + length + 1].decode())
            try:
                lst.append(self.message[pos + 1:pos + length + 1].decode())
            except UnicodeDecodeError:
                # print(11111)
                pass
            pos += length + 1
            
        pos += 1
        domain = '.'.join(lst)
        return pos, domain

    def parse_QUESTION(self, pos):
        if self.QDCOUNT > 0:        # usually 1
            pos, domain = self.parse_domain(pos)
            self.QNAME = domain
            self.QTYPE = (self.message[pos] << 8) + self.message[pos + 1]
            pos += 2
            self.QCLASS = (self.message[pos] << 8) + self.message[pos + 1]
            pos += 2
        return pos
    
    def parse_RESPONSE(self, pos):
        total = self.ANCOUNT
        while total > 0:
            total -= 1
            domain = ''
            # print('response', pos)
            if (self.message[pos] & 0xc0) == 0xc0:   # indicates message compression
                offset = ((self.message[pos] & 0x3f) << 8) + self.message[pos + 1]
                _, domain = self.parse_domain(offset)
                pos += 2
            else:
                pos, domain = self.parse_domain(pos)
            self.RNAME.append(domain)

            self.RTYPE.append((self.message[pos] << 8) + self.message[pos + 1])
            pos += 2
            self.RCLASS.append((self.message[pos] << 8) + self.message[pos + 1])
            pos += 2
            TTL = 0
            for i in range(pos, pos + 4):
                TTL = (TTL << 8) + self.message[i]
            self.TTL.append(TTL)
            pos += 4
            RDLENGTH = (self.message[pos] << 8) + self.message[pos + 1]
            self.RDLENGTH.append(RDLENGTH)
            pos += 2

            if self.RTYPE[-1] == 1:         # we only interested in A record and ipv4 address
                ip = ''
                for i in range(4):
                    ip += '.' + str(self.message[pos + i])
            else:
                return pos
            pos += RDLENGTH

        return pos