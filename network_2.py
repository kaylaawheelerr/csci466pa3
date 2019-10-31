'''
Created on Oct 27, 2019

@author: Cole Sluggett, Kayla Wheeler
'''
import queue
import threading
import math
from network import Interface, NetworkPacket, Host, Router        

class NetworkPacket_2(NetworkPacket):
    ## packet encoding lengths 
    dst_addr_S_length = 5
    offset_length = 5
    flag_length = 5
    

    def __init__(self, dst_addr, offset, fragment_flag, data_S):
        self.dst_addr = dst_addr
        self.offset = offset 
        self.fragment_flag = fragment_flag 
        self.data_S = data_S 
        
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
        offset = int(byte_S[NetworkPacket.dst_addr_S_length:NetworkPacket.dst_addr_S_length+NetworkPacket_2.offset_length])
        fragment_flag = int(byte_S[NetworkPacket.dst_addr_S_length+NetworkPacket_2.offset_length:NetworkPacket.dst_addr_S_length+NetworkPacket_2.offset_length+NetworkPacket_2.flag_length])
        data_S = byte_S[NetworkPacket.dst_addr_S_length+NetworkPacket_2.offset_length+NetworkPacket_2.flag_length:]
        return self(dst_addr, offset, fragment_flag, data_S)
    

class Host_2(Host):
       
    def udt_send(self, dst_addr, data_S):

        data_length = len(data_S)
        mtu_payload = self.out_intf_L[0].mtu-11

        #  Fragmentation:
        if data_length > mtu_payload:
            split_packets = fragment_packet(mtu_payload, data_S, dst_addr)

            for p in split_packets:
                self.out_intf_L[0].put(p.to_byte_S()) 
                print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))

        else:
            p = NetworkPacket_2(dst_addr, 0, 0, data_S)
            self.out_intf_L[0].put(p.to_byte_S()) 
            print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))

    received = []

    def udt_receive(self):
        packet_string = self.in_intf_L[0].get()
        if packet_string is not None:
            if packet_string[14] == str(1):
                self.received.append(packet_string)
                if packet_string[-1] == str(0):
                    final_packet_payload = ''
                    destination = packet_string[0:5]

                    for i in self.received:
                        final_packet_payload += i[15:]

                    packet = NetworkPacket_2(destination, 0, 0, final_packet_payload)
                    final_packet = packet.to_byte_S()

                    self.received = []
                    print(str(self) + " has received CONSTRUCTED PACKET: " + final_packet + "\n")
                elif packet_string[-1] == str(1):
                    final_packet_payload = ''
                    destination = packet_string[0:5]

                    for i in self.received:
                        final_packet_payload += i[15:]
                    packet = NetworkPacket_2(destination, 0, 0, final_packet_payload)
                    final_packet = packet.to_byte_S()
                    self.received = []
                    print(str(self) + " has received CONSTRUCTED PACKET: " + final_packet + "\n")

                elif packet_string[-1] == str(2):
                    final_packet_payload = ''
                    destination = packet_string[0:5]
                    for i in self.received:
                        final_packet_payload += i[15:]

                    packet = NetworkPacket_2(destination, 0, 0, final_packet_payload)
                    final_packet = packet.to_byte_S()

                    self.received = []
                    print(str(self) + " has received CONSTRUCTED PACKET: " + final_packet + "\n")


class Router_2(Router):

    def forward(self):
        for i in range(len(self.in_intf_L)):
            packet_string = None
            try:
                packet_string = self.in_intf_L[i].get()
                if packet_string is not None:
                    packet = NetworkPacket.from_byte_S(packet_string) 
                    mtu_payload = self.out_intf_L[i].mtu-11
                    length = len(packet_string)
                    if length > mtu_payload:
                        destination = packet_string[0:5]
                        payload = packet_string[15:]
                        split_packets = fragment_packet(mtu_payload, payload, destination)
                        for p_new in split_packets:
                            self.out_intf_L[i].put(p_new.to_byte_S(), True)
                            print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                                  % (self, packet, i, i, self.out_intf_L[i].mtu))
                    else:
                        self.out_intf_L[i].put(packet.to_byte_S(), True)
                        print('%s: forwarding packet "%s" from interface %d to %d with mtu %d' \
                            % (self, packet, i, i, self.out_intf_L[i].mtu))
            except queue.Full:
                print('%s: packet "%s" lost on interface %d' % (self, packet, i))
                pass


def fragment_packet(mtu, data_S, dst_addr):

    split_packets = []
    count = 0

    while count < len(data_S):
        add = mtu - 10
        p = NetworkPacket_2(dst_addr, count, 1, data_S[count:add+count])
        count += add
        split_packets.append(p)

    return split_packets
