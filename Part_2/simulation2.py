# Richard Wheeler and Kristijonas Umbrasas

# Part 2: Binary Exponential Backoff Simulation

import random
import simpy
import math

RANDOM_SEED = 29
SIM_TIME = 100000
MU = 1
B = 10


""" 10-Queue system  """
    

class server_queue:
    def __init__(self, env, arrival_rate, Packet_Delay, Server_Idle_Periods):
        #self.L = 0 #The number of packets in the queue.
        self.N = 0 #The number of times the packet at the head of the queue has been retransmitted. When a new packet comes to
            #the head of the queue n is reset to 0.
        self.slotNum = 0 #The slot number when the next transmission attempt will be made for the packet at the head of the queue.
    

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
        self.total_no_packets = 0
        self.discards = 0
        
    def process_packet(self, env, packet):
        with self.server.request() as req:
            start = env.now
            yield req
            yield env.timeout(random.expovariate(MU))
            latency = env.now - packet.arrival_time
            self.Packet_Delay.addNumber(latency)
            #print("Packet number {0} with arrival time {1} latency {2}".format(packet.identifier, packet.arrival_time, latency))
            self.queue_len -= 1
            if self.queue_len == 0:
                self.flag_processing = 0
                self.start_idle_time = env.now
                
    def packets_arrival(self, env):
        # packet arrivals 
        
        while True:
             # Infinite loop for generating packets
            yield env.timeout(random.expovariate(self.arrival_rate))
              # arrival time of one packet

            self.total_no_packets += 1
            if self.queue_len < B:
                self.packet_number += 1
                  # packet id
                arrival_time = env.now  
                #print(self.num_pkt_total, "packet arrival")
                new_packet = Packet(self.packet_number,arrival_time)
                self.queue_len += 1
                env.process(self.process_packet(env, new_packet))
            else:
                self.discards += 1
            
    

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
    def sum(self):
        n = len(self.dataset)
        sum = 0
        for i in self.dataset:
            sum = sum + i
        return sum
    def mean(self):
        n = len(self.dataset)
        sum = 0
        for i in self.dataset:
            sum = sum + i
        return sum/n
    def maximum(self):
        return max(self.dataset)
    def minimum(self):
        return min(self.dataset)
    def count(self):
        return len(self.dataset)
    def median(self):
        self.dataset.sort()
        n = len(self.dataset)
        if n//2 != 0: # get the middle number
            return self.dataset[n//2]
        else: # find the average of the middle two numbers
            return ((self.dataset[n//2] + self.dataset[n//2 + 1])/2)
    def standarddeviation(self):
        temp = self.mean()
        sum = 0
        for i in self.dataset:
            sum = sum + (i - temp)**2
        sum = sum/(len(self.dataset) - 1)
        return math.sqrt(sum)

class ethernet_model:
    def __init__(self, env, arrival_rate, Packet_Delay, Server_Idle_Periods):
        self.currentSlot = 0
        self.env = env
        self.Packet_Delay = Packet_Delay
        self.Server_Idle_Periods = Server_Idle_Periods
        self.queues = [server_queue(env, arrival_rate, Packet_Delay, Server_Idle_Periods) for _ in range(10)]


        
    def runModel(self,env):
        currentSlot = 1
        while True:
            queuesThatWantToSend = []
            self.currentSlot = self.currentSlot + 1
            print(self.currentSlot)
            for currentQueue in range(1,10):
                if self.queues[currentQueue].queue_len > 0
                    queuesThatWantToSend.append(currentQueue) #this will tell us which queues want to send
            if(len(queuesThatWantToSend) > 1):
                self.exponentionalBackoff(self,env,queuesThatWantToSend)
            else if(len(queuesThatWantToSend) == 1):
                self.queues[queuesThatWantToSend[0]].process_packet


            yield env.timeout(1) # lets say that env.timeout(1) represents 1 second, which is the service time

    def exponentionalBackoff(self,env,queuesThatWantToSend):
        for currentIndex in range(1,len(queuesThatWantToSend)):
            self.queues[queuesThatWantToSend[currentIndex]].N = self.queues[queuesThatWantToSend[currentIndex]].N + 1
            proposedBackoffSlot = random.randrange(currentSlot+1,2**self.queues[queuesThatWantToSend[currentIndex]].N)
            for currentQueue in range(1,10):
                self.queues[currentQueue]. 



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
