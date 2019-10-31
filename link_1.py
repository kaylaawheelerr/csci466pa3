'''
Created on Oct 27, 2019

@author: Cole Sluggett, Kayla Wheeler
'''
import queue
import threading
from link import LinkLayer, Link

## An abstraction of a link between router interfaces
class Link_1(Link):
    
    ## creates a link between two objects by looking up and linking node interfaces.
    # @param from_node: node from which data will be transfered
    # @param from_intf_num: number of the interface on that node
    # @param to_node: node to which data will be transfered
    # @param to_intf_num: number of the interface on that node
    # @param mtu: link maximum transmission unit
    
    ##transmit a packet from the 'from' to the 'to' interface
    def tx_pkt(self):
        pkt_S = self.in_intf.get()
        if pkt_S is None:
            return #return if no packet to transfer
        if len(pkt_S) > self.out_intf.mtu:
            print('%s: packet "%s" length greater then link mtu (%d)' % (self, pkt_S, self.out_intf.mtu))
            end_of_packet_string = pkt_S[45:]
            final_number = pkt_S[-1]
            server = pkt_S[:5]
            pkt_S = pkt_S[:45]

            try:
                self.out_intf.put(pkt_S+" "+final_number)
                print('%s: transmitting packet "%s"' % (self, pkt_S+" ")+final_number)
                self.out_intf.put(server+end_of_packet_string)
                print('%s: transmitting packet "%s"' % (self, server+end_of_packet_string))

            except queue.Full:
                print('%s: packet lost' % (self))
                pass

            return #return without transmitting if packet too big
        #otherwise transmit the packet
        try:
            self.out_intf.put(pkt_S)
            print('%s: transmitting packet "%s"' % (self, pkt_S))
            #self.out_intf.put(self.end_of_packet_string)
            #print('%s: transmitting packet "%s"' % (self, end_of_packet_string))

        except queue.Full:
            print('%s: packet lost' % (self))
            pass
        
        
    
