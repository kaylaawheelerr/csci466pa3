'''
Created on Oct 12, 2016

@author: mwittie
'''
import queue
import threading
from network import Interface, NetworkPacket, Router, Host

        
## Implements a network layer packet (different from the RDT packet 
# from programming assignment 2).
# NOTE: This class will need to be extended to for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket_3(NetworkPacket):
    ## packet encoding lengths 
    dst_addr_S_length = 5
    origin_addr_S_length = 5
    
    ##@param dst_addr: address of the destination host
    # @param data_S: packet payload
    def __init__(self, origin_addr, dst_addr, data_S):
        self.origin_addr = origin_addr
        self.dst_addr = dst_addr
        self.data_S = data_S
        
    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.origin_addr).zfill(self.origin_addr_S_length)
        byte_S += str(self.dst_addr).zfill(self.dst_addr_S_length)
        byte_S += self.data_S
        return byte_S
    
    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        origin_addr = int(byte_S[0 : NetworkPacket_3.origin_addr_S_length])
        dst_addr = int(byte_S[NetworkPacket_3.origin_addr_S_length : NetworkPacket_3.origin_addr_S_length + NetworkPacket.dst_addr_S_length])
        data_S = byte_S[NetworkPacket_3.origin_addr_S_length + NetworkPacket.dst_addr_S_length : ]
        return self(origin_addr, dst_addr, data_S)
    

    

## Implements a network host for receiving and transmitting data
class Host_3(Host):

    ## create a packet and enqueue for transmission
    # @param dst_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst_addr, data_S):
        p = NetworkPacket_3(self.addr, dst_addr, data_S)
        self.out_intf_L[0].put(p.to_byte_S()) #send packets always enqueued successfully
        print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))

        


## Implements a multi-interface router described in class
class Router_3(Router):
    
    ##@param name: friendly router name for debugging
    # @param intf_count: the number of input and output interfaces 
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, intf_count, max_queue_size, routing_dictionary):
        self.table = routing_dictionary
        self.stop = False #for thread termination
        self.name = name
        #create a list of interfaces
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]

    ## look through the content of incoming interfaces and forward to
    # appropriate outgoing interfaces
    def forward(self):
        for i in range(len(self.in_intf_L)):
            pkt_S = None
            try:
                #get packet from interface i
                pkt_S = self.in_intf_L[i].get()
                #if packet exists make a forwarding decision
                if pkt_S is not None:
                    #print("OUT INTERFACSE!: " +str(self.in_intf_L))
                    p = NetworkPacket.from_byte_S(pkt_S) #parse a packet out
                    # if(len(self.in_intf_L) == 1):
                    #     self.out_intf_L[0].put(p.to_byte_S(), True)
                    # else:
                    #     if self.name == "A":
                    #         if pkt_S[4] == "1":
                    #             print("GOING TO B.")
                    #             self.out_intf_L[0].put(p.to_byte_S(), True)
                    #         elif pkt_S[4] == "2":
                    #             self.out_intf_L[1].put(p.to_byte_S(), True)
                    #             print("GOING TO C.")
                    #     elif self.name == "D":
                    #         if pkt_S[9] == "3":
                    #             self.out_intf_L[0].put(p.to_byte_S(), True)
                    #             print("GOING TO HOST 3.")
                    #         elif pkt_S[9] == "4":
                    #             self.out_intf_L[1].put(p.to_byte_S(), True)
                    #             print("GOING TO HOST 4.")
                    if (len(self.in_intf_L) == 1):
                        # This will take care of routers B and C.
                        self.out_intf_L[0].put(p.to_byte_S(), True)
                    else:
                        for path in self.table:
                            if self.name == 'A':
                                if pkt_S[4] == '1':
                                    self.out_intf_L[0].put(p.to_byte_S(), True)
                                    break
                                elif pkt_S[4] == '2':
                                    self.out_intf_L[1].put(p.to_byte_S(), True)
                                    break

                            elif int(path) == int(pkt_S[9]):
                                if int(path) == 3:
                                    self.out_intf_L[0].put(p.to_byte_S(), True)
                                elif int(path) == 4:
                                    self.out_intf_L[1].put(p.to_byte_S(), True)
                                break
                    # HERE you will need to implement a lookup into the
                    # forwarding table to find the appropriate outgoing interface
                    # for now we assume the outgoing interface is also i
                    #self.out_intf_L[i].put(p.to_byte_S(), True)
                    print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                        % (self, p, i, i, self.out_intf_L[i].mtu))
            except queue.Full:
                print('%s: packet "%s" lost on interface %d' % (self, p, i))
                pass
