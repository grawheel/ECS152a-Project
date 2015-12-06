# Richard Wheeler and Kristijonas Umbrasas

# Part 2: Binary Exponential Backoff Simulation

import random
import simpy
import math

RANDOM_SEED = 29
SIM_TIME = 100000
MU = 1


""" 10-Queue system  """
    

class server_queue:
    def __init__(self, env, arrival_rate, Packet_Delay, Server_Idle_Periods):
        #self.L = 0 #The number of packets in the queue.
        self.N = 0 #The number of times the packet at the head of the queue has been retransmitted. When a new packet comes to
            #the head of the queue n is reset to 0.
        self.slotNum = 1 #The slot number when the next transmission attempt will be made for the packet at the head of the queue.
        self.total_no_packets = 0

        self.server = simpy.Resource(env, capacity = 1)
        self.env = env
        self.queue_len = 0
        self.flag_processing = 0
        self.packet_number = 0
        self.sum_time_length = 0
        self.start_idle_time = 0
        self.arrival_rate = arrival_rate
        self.Packet_Delay = Packet_Delay
        self.Server_Idle_Periods = Server_Idle_Periods
        self.discards = 0
        self.currentPacket = 0
        
    def process_packet(self, env):
        #print("Packet number {0} with arrival time {1} latency {2}".format(packet.identifier, packet.arrival_time, latency))
        self.queue_len -= 1
        print("Processing for slot: " + repr(self.slotNum))
        if self.queue_len == 0:
            self.flag_processing = 0
                
    def packets_arrival(self, env):
        # packet arrivals 
        
        while True:
             # Infinite loop for generating packets
            yield env.timeout(random.expovariate(self.arrival_rate))
              # arrival time of one packet

            self.total_no_packets += 1
            self.packet_number += 1
            self.queue_len += 1
            
    

""" Packet class """            
class Packet:
    def __init__(self, identifier, arrival_time):
        self.identifier = identifier
        self.arrival_time = arrival_time
        

class StatObject:
    def __init__(self):
        self.dataset =[]

    def addNumber(self,x):
        self.dataset.append(x)
    def count(self):
        return len(self.dataset)

class ethernet_model:
    def __init__(self, env, arrival_rate, Packet_Delay, Server_Idle_Periods):
        self.currentSlot = 1
        self.env = env
        self.Packet_Delay = Packet_Delay
        self.Server_Idle_Periods = Server_Idle_Periods
        self.queues = [server_queue(env, arrival_rate, Packet_Delay, Server_Idle_Periods) for _ in range(10)]
        for i in range(0,9):
            env.process(self.queues[i].packets_arrival(env))
        
        
    def runModel(self,env):
        while True:
            queuesThatWantToSend = []
            print(self.currentSlot)
            for currentQueue in range(1,10):#check which queues want to send for current slot number
                if ((self.queues[currentQueue].queue_len) == 0):
                    self.queues[currentQueue].slotNum = self.currentSlot #keep slot numbers current
                if ((self.queues[currentQueue].queue_len > 0) and (self.queues[currentQueue].slotNum==self.currentSlot)):
                    queuesThatWantToSend.append(currentQueue) 

            if(len(queuesThatWantToSend) > 1):#if collisions occur
                self.exponentionalBackoff(env,queuesThatWantToSend)
            elif(len(queuesThatWantToSend) == 1):#otherwise
                #env.process(self.process_packet(env, new_packet))
                self.queues[queuesThatWantToSend[0]].process_packet(env)
                self.queues[queuesThatWantToSend[0]].N = 0
                self.queues[queuesThatWantToSend[0]].slotNum = self.queues[queuesThatWantToSend[0]].slotNum + 1

            yield self.env.timeout(1) # lets say that env.timeout(1) represents 1 second, which is the service time
            self.currentSlot = self.currentSlot + 1

    def exponentionalBackoff(self,env,queuesThatWantToSend):#recalculate slotNum for each queueThatWantToSend
        for currentIndex in range(1,len(queuesThatWantToSend)):
            k = min(self.queues[queuesThatWantToSend[currentIndex]].N, 10)
            randVar = random.randint(0,2**k)
            self.queues[queuesThatWantToSend[currentIndex]].slotNum = self.queues[queuesThatWantToSend[currentIndex]].slotNum + randVar
            self.queues[queuesThatWantToSend[currentIndex]].N = self.queues[queuesThatWantToSend[currentIndex]].N + 1




def main():
    print("Binary Exponential Backoff Model with 10 Queues: ")
    random.seed(RANDOM_SEED)
    env = simpy.Environment()
    Packet_Delay = StatObject()
    Server_Idle_Periods = StatObject()
    for arrival_rate in [0.01, 0.02]:
        router = ethernet_model(env, arrival_rate, Packet_Delay, Server_Idle_Periods)
        #env.process(router.packets_arrival(env))
        env.process(router.runModel(env))
        env.run(until=SIM_TIME)
    
if __name__ == '__main__': main()