'''
Created on Oct 27, 2019

@author: Cole Sluggett, Kayla Wheeler
'''
import queue
import threading
from network import Interface, NetworkPacket, Router, Host

        
class NetworkPacket_3(NetworkPacket):
    ## packet encoding lengths 
    dst_addr_S_length = 5
    origin_addr_S_length = 5
 
    def __init__(self, origin_addr, dst_addr, data_S):
        self.origin_addr = origin_addr
        self.dst_addr = dst_addr
        self.data_S = data_S
 
    def to_byte_S(self):
        byte_S = str(self.origin_addr).zfill(self.origin_addr_S_length)
        byte_S += str(self.dst_addr).zfill(self.dst_addr_S_length)
        byte_S += self.data_S
        return byte_S

    @classmethod
    def from_byte_S(self, byte_S):
        origin_addr = int(byte_S[0 : NetworkPacket_3.origin_addr_S_length])
        dst_addr = int(byte_S[NetworkPacket_3.origin_addr_S_length : NetworkPacket_3.origin_addr_S_length + NetworkPacket.dst_addr_S_length])
        data_S = byte_S[NetworkPacket_3.origin_addr_S_length + NetworkPacket.dst_addr_S_length : ]
        return self(origin_addr, dst_addr, data_S)
    

    

## Implements a network host for receiving and transmitting data
class Host_3(Host):

    def udt_send(self, dst_addr, data_S):
        packet = NetworkPacket_3(self.addr, dst_addr, data_S)
        self.out_intf_L[0].put(packet.to_byte_S()) 
        print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, packet, self.out_intf_L[0].mtu))

        



class Router_3(Router):
    def __init__(self, name, intf_count, max_queue_size, routing_dictionary):
        self.table = routing_dictionary
        self.stop = False 
        self.name = name
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]

    def forward(self):
        for i in range(len(self.in_intf_L)):
            packet_string = None
            try:
                packet_string = self.in_intf_L[i].get()
                if packet_string is not None:
                    packet = NetworkPacket.from_byte_S(packet_string)               
                    if (len(self.in_intf_L) == 1):
                        self.out_intf_L[0].put(packet.to_byte_S(), True)
                    else:
                        for path in self.table:
                            if self.name == 'A':
                                if packet_string[4] == '1':
                                    self.out_intf_L[0].put(packet.to_byte_S(), True)
                                    break
                                elif packet_string[4] == '2':
                                    self.out_intf_L[1].put(packet.to_byte_S(), True)
                                    break

                            elif int(path) == int(packet_string[9]):
                                if int(path) == 3:
                                    self.out_intf_L[0].put(packet.to_byte_S(), True)
                                elif int(path) == 4:
                                    self.out_intf_L[1].put(packet.to_byte_S(), True)
                                break
           
                    print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                        % (self, packet, i, i, self.out_intf_L[i].mtu))
            except queue.Full:
                print('%s: packet "%s" lost on interface %d' % (self, packet, i))
                pass
