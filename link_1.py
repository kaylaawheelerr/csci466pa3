'''
Created on Oct 27, 2019

@author: Cole Sluggett, Kayla Wheeler
'''
import queue
import threading
from link import LinkLayer, Link


class Link_1(Link):

    def tx_pkt(self):
        packet_string = self.in_intf.get()
        if packet_string is None:
            return 
        if len(packet_string) > self.out_intf.mtu:
            print('%s: packet "%s" length greater then link mtu (%d)' % (self, packet_string, self.out_intf.mtu))
            end_of_packet_string = packet_string[45:]
            final_number = packet_string[-1]
            server = packet_string[:5]
            packet_string = packet_string[:45]

            try:
                self.out_intf.put(packet_string+" "+final_number)
                print('%s: transmitting packet "%s"' % (self, packet_string+" ")+final_number)
                self.out_intf.put(server+end_of_packet_string)
                print('%s: transmitting packet "%s"' % (self, server+end_of_packet_string))

            except queue.Full:
                print('%s: packet lost' % (self))
                pass

            return 
        try:
            self.out_intf.put(packet_string)
            print('%s: transmitting packet "%s"' % (self, packet_string))


        except queue.Full:
            print('%s: packet lost' % (self))
            pass
        
        
    
