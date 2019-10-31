'''
Created on Oct 12, 2016

@author: mwittie
'''
import network_3 as network
import link_3 as link
import threading
from time import sleep

##configuration parameters
router_queue_size = 0 #0 means unlimited
simulation_time = 1 #give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = [] #keeps track of objects, so we can kill their threads
    
    #create network nodes

    table = {
        "A": ["B","C"],
        "B": ["D"],
        "C": ["D"],
        "D": ["3","4"]
    }

    #HOSTS

    client_1 = network.Host_3(1)
    client_2 = network.Host_3(2)
    client_3 = network.Host_3(3)
    client_4 = network.Host_3(4)

    object_L.append(client_1)
    object_L.append(client_2)
    object_L.append(client_3)
    object_L.append(client_4)

    #ROUTERS

    router_a = network.Router_3(name='A', intf_count=2, max_queue_size=router_queue_size, routing_dictionary=table["A"])
    router_b = network.Router_3(name='B', intf_count=1, max_queue_size=router_queue_size, routing_dictionary=table["B"])
    router_c = network.Router_3(name='C', intf_count=1, max_queue_size=router_queue_size, routing_dictionary=table["C"])
    router_d = network.Router_3(name='D', intf_count=2, max_queue_size=router_queue_size, routing_dictionary=table["D"])

    object_L.append(router_a)
    object_L.append(router_b)
    object_L.append(router_c)
    object_L.append(router_d)

    
    #create a Link Layer to keep track of links between network nodes
    link_layer = link.LinkLayer()
    object_L.append(link_layer)
    
    #add all the links
    #link parameters: from_node, from_intf_num, to_node, to_intf_num, mtu
    link_layer.add_link(link.Link(client_1, 0, router_a, 0, 50))
    link_layer.add_link(link.Link(client_2, 0, router_a, 1, 50))
    link_layer.add_link(link.Link(router_a, 0, router_b, 0, 50))
    link_layer.add_link(link.Link(router_a, 1, router_c, 0, 50))
    link_layer.add_link(link.Link(router_b, 0, router_d, 0, 50))
    link_layer.add_link(link.Link(router_c, 0, router_d, 1, 50))
    link_layer.add_link(link.Link(router_d, 0, client_3, 0, 50))
    link_layer.add_link(link.Link(router_d, 1, client_4, 0, 50))
    
    
    #start all the objects
    thread_L = []
    thread_L.append(threading.Thread(name=client_1.__str__(), target=client_1.run))
    thread_L.append(threading.Thread(name=client_2.__str__(), target=client_2.run))
    thread_L.append(threading.Thread(name=client_3.__str__(), target=client_3.run))
    thread_L.append(threading.Thread(name=client_4.__str__(), target=client_4.run))
    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))
    thread_L.append(threading.Thread(name=router_b.__str__(), target=router_b.run))
    thread_L.append(threading.Thread(name=router_c.__str__(), target=router_c.run))
    thread_L.append(threading.Thread(name=router_d.__str__(), target=router_d.run))
    thread_L.append(threading.Thread(name="Network", target=link_layer.run))
    
    for t in thread_L:
        t.start()
    
    
    #create some send events
    client_1.udt_send(3, 'Sample Data.')
    client_2.udt_send(4, 'Sample Data.')

    
    
    #give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)
    
    #join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()
        
    print("All simulation threads joined")



# writes to host periodically