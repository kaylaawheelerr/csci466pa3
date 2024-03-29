'''
Created on Oct 12, 2016

@author: mwittie
'''
import queue
import threading
import math

## wrapper class for a queue of packets
class Interface:
    ## @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize)
        self.mtu = None
    
    ##get packet from the queue interface
    def get(self):
        try:
            return self.queue.get(False)
        except queue.Empty:
            return None
        
    ##put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, block=False):
        self.queue.put(pkt, block)
        
        
## Implements a network layer packet (different from the RDT packet 
# from programming assignment 2).
# NOTE: This class will need to be extended to for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket:
    ## packet encoding lengths 
    dst_addr_S_length = 5
    offset_length = 5
    flag_length = 5
    
    ##@param dst_addr: address of the destination host
    # @param data_S: packet payload
    def __init__(self, dst_addr, offset, fragment_flag, data_S):
        self.dst_addr = dst_addr
        self.offset = offset # Number at which the payload stops at, ex: MAX 30 for 30 MTU.
        self.fragment_flag = fragment_flag # 1 If it is a fragment, 0 if it is the whole packet
        self.data_S = data_S # Payload
        
    ## called when printing the object
    def __str__(self):
        return self.to_byte_S()
        
    ## convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
        byte_S += str(self.offset).zfill(self.offset_length)
        byte_S += str(self.fragment_flag).zfill(self.flag_length)
        byte_S += self.data_S
        return byte_S
    
    ## extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(self, byte_S):
        dst_addr = int(byte_S[0 : NetworkPacket.dst_addr_S_length])
        offset = int(byte_S[NetworkPacket.dst_addr_S_length:NetworkPacket.dst_addr_S_length+NetworkPacket.offset_length])
        fragment_flag = int(byte_S[NetworkPacket.dst_addr_S_length+NetworkPacket.offset_length:NetworkPacket.dst_addr_S_length+NetworkPacket.offset_length+NetworkPacket.flag_length])
        data_S = byte_S[NetworkPacket.dst_addr_S_length+NetworkPacket.offset_length+NetworkPacket.flag_length:]
        return self(dst_addr, offset, fragment_flag, data_S)
    

    

## Implements a network host for receiving and transmitting data
class Host:
    
    ##@param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.in_intf_L = [Interface()]
        self.out_intf_L = [Interface()]
        self.stop = False #for thread termination
    
    ## called when printing the object
    def __str__(self):
        return 'Host_%s' % (self.addr)
       
    # create a packet and enqueue for transmission
    # @param dst_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst_addr, data_S):

        data_length = len(data_S)
        mtu_payload = self.out_intf_L[0].mtu-11

        #  Fragmentation:
        if data_length > mtu_payload:
            split_packets = fragment_packet(mtu_payload, data_S, dst_addr)

            for p in split_packets:
                self.out_intf_L[0].put(p.to_byte_S())  # send packets always enqueued successfully
                print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))

        else:
            p = NetworkPacket(dst_addr, 0, 0, data_S)
            self.out_intf_L[0].put(p.to_byte_S()) #send packets always enqueued successfully
            print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))

    received = []
    ## receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.in_intf_L[0].get()
        if pkt_S is not None:
            #print('%s: received packet "%s" on the in interface' % (self, pkt_S))
            if pkt_S[14] == str(1):
                self.received.append(pkt_S)
                #print(self.received)
                if pkt_S[-1] == str(0):
                    final_packet_payload = ''
                    destination = pkt_S[0:5]

                    for i in self.received:
                        final_packet_payload += i[15:]

                    p = NetworkPacket(destination, 0, 0, final_packet_payload)
                    final_p = p.to_byte_S()

                    self.received = []
                    print(str(self) + " has received CONSTRUCTED PACKET: " + final_p + "\n")
                elif pkt_S[-1] == str(1):
                    final_packet_payload = ''
                    destination = pkt_S[0:5]

                    for i in self.received:
                        final_packet_payload += i[15:]

                    p = NetworkPacket(destination, 0, 0, final_packet_payload)
                    final_p = p.to_byte_S()

                    self.received = []
                    print(str(self) + " has received CONSTRUCTED PACKET: " + final_p + "\n")

                elif pkt_S[-1] == str(2):
                    final_packet_payload = ''
                    destination = pkt_S[0:5]

                    for i in self.received:
                        final_packet_payload += i[15:]

                    p = NetworkPacket(destination, 0, 0, final_packet_payload)
                    final_p = p.to_byte_S()

                    self.received = []
                    print(str(self) + " has received CONSTRUCTED PACKET: " + final_p + "\n")

       
    ## thread target for the host to keep receiving data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            #receive data arriving to the in interface
            self.udt_receive()
            #terminate
            if(self.stop):
                print (threading.currentThread().getName() + ': Ending')
                return
        


## Implements a multi-interface router described in class
class Router:
    
    ##@param name: friendly router name for debugging
    # @param intf_count: the number of input and output interfaces 
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, intf_count, max_queue_size):
        self.stop = False #for thread termination
        self.name = name
        #create a list of interfaces
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]

    ## called when printing the object
    def __str__(self):
        return 'Router_%s' % (self.name)

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
                    p = NetworkPacket.from_byte_S(pkt_S) #parse a packet out
                    mtu_payload = self.out_intf_L[i].mtu-11
                    length = len(pkt_S)

                    if length > mtu_payload:
                        destination = pkt_S[0:5]
                        payload = pkt_S[15:]

                        split_packets = fragment_packet(mtu_payload, payload, destination)

                        for p_new in split_packets:
                            # print("Fragmented: " + str(p_new))
                            self.out_intf_L[i].put(p_new.to_byte_S(), True)
                            print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                                  % (self, p, i, i, self.out_intf_L[i].mtu))

                    else:
                        self.out_intf_L[i].put(p.to_byte_S(), True)
                        print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                            % (self, p, i, i, self.out_intf_L[i].mtu))
            except queue.Full:
                print('%s: packet "%s" lost on interface %d' % (self, p, i))
                pass
                
    ## thread target for the host to keep forwarding data
    def run(self):
        print (threading.currentThread().getName() + ': Starting')
        while True:
            self.forward()
            if self.stop:
                print (threading.currentThread().getName() + ': Ending')
                return



def fragment_packet(mtu, data_S, dst_addr):

    split_packets = []
    count = 0

    while count < len(data_S):
        add = mtu - 10
        p = NetworkPacket(dst_addr, count, 1, data_S[count:add+count])
        count += add
        split_packets.append(p)

    return split_packets
