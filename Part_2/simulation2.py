# Richard Wheeler and Kristijonas Umbrasas
# ECS 152A - Project - Part 2: Binary Exponential Backoff and Linear Backoff Simulation

import random
import simpy
import math

RANDOM_SEED = 29
SIM_TIME = 100000
MU = 1

#The current slot in the ethernet simulation model
currentSlotGlobal = 0
#The total number of packets processed in the ethernet simulation model
totalPacketsProcessed = 0


""" 10-Queue system  """
    

class server_queue:
    def __init__(self, env, arrival_rate):
        #***We define slot period to be 1 'second' in this program***
        self.env = env
        #N is the number of times the packet at the head of the queue has been retransmitted. When a new packet comes to
        #the head of the queue n is reset to 1, since the first time we use N will be the first time it is retransmitted.
        self.N = 1 
        #The slot number when the next transmission attempt will be made for the packet ready to be processed in this queue.
        self.slotTargetNum = 1 
        self.total_no_packets = 0
        self.server = simpy.Resource(env, capacity = 1)
        #The length of the queue which has infinite capacity
        self.queue_len = 0
        self.arrival_rate = arrival_rate
        self.proccessingPacket = 0
        
    #Here we process the packet at the head of the queue
    def process_packet(self, env):
        global currentSlotGlobal, totalPacketsProcessed
        self.queue_len -= 1
        totalPacketsProcessed = totalPacketsProcessed + 1
        
        if self.queue_len > 0:
            self.N = 1
            self.slotTargetNum = currentSlotGlobal + 1
            self.proccessingPacket = 1
        elif self.queue_len == 0:
            self.proccessingPacket = 0
                
    #Here is an infinite loop of arriving packets to this queue, per arrival rate
    def packets_arrival(self, env):
        while True:
            yield env.timeout(random.expovariate(self.arrival_rate))

            self.total_no_packets += 1
            self.queue_len += 1

            if self.proccessingPacket == 0:
                self.N = 1
                self.slotTargetNum = currentSlotGlobal + 1
                self.proccessingPacket = 1

#The simulation model which can represent both Binary Exponential Backoff and Linear Backoff Algorithms
class ethernet_model:
    def __init__(self, env, queues):
        self.env = env
        self.currentSlot = 1
        self.queues = queues
        self.packetsProcessed = 0
        self.totalCollisions = 0

        [env.process(self.queues[i].packets_arrival(self.env)) for i in range(10)]
        
    #Run Binary Exponential Backoff model
    def runModelBinary(self,env):
        global currentSlotGlobal
        while True:
            queueIndexesToSend = []
            for j in range(10):
                #Check if the current queue in the loop wants to process a packet in this slot
                if (((self.queues[j].proccessingPacket) == 1) and (self.queues[j].slotTargetNum <= currentSlotGlobal)):
                    #Here we update the slotTargetNum in case it's a slot that has passed
                    self.queues[j].slotTargetNum = currentSlotGlobal
                    queueIndexesToSend.append(j) 

            #For all queues that want to process a packet calculate a future slot in case of collision, 
            #if there is only one slot that wants to process we account for this in the next if statement.
            for index in queueIndexesToSend:
                self.exponentionalBackoff(self.queues[index])
                self.totalCollisions = self.totalCollisions + 1

            #If only one packet wants to be processed in this slot then process it
            if(len(queueIndexesToSend) == 1):
                self.queues[queueIndexesToSend[0]].process_packet(env)
                
            #Lets say that env.timeout(1) represents 1 second, which is the service time
            yield env.timeout(1)
            currentSlotGlobal = currentSlotGlobal + 1


    #Run Binary Exponential Backoff calculation
    def exponentionalBackoff(self, queue):
        k = min(queue.N, 10)
        randVar = random.randint(0,2**k)
        queue.slotTargetNum = queue.slotTargetNum + randVar
        queue.N = queue.N + 1

    #Run Linear Backoff model
    def runModelLinear(self,env):
        global currentSlotGlobal
        while True:
            queueIndexesToSend = []
            for j in range(10):
                #Check if the current queue in the loop wants to process a packet in this slot
                if (((self.queues[j].proccessingPacket) == 1) and (self.queues[j].slotTargetNum <= currentSlotGlobal)):
                    #Here we update the slotTargetNum in case it's a slot that has passed
                    self.queues[j].slotTargetNum = currentSlotGlobal
                    queueIndexesToSend.append(j) 

            #For all queues that want to process a packet calculate a future slot in case of collision, 
            #if there is only one slot that wants to process we account for this in the next if statement.
            for index in queueIndexesToSend:
                self.linearBackoff(self.queues[index])
                self.totalCollisions = self.totalCollisions + 1

            #If only one packet wants to be processed in this slot then process it
            if(len(queueIndexesToSend) == 1):
                self.queues[queueIndexesToSend[0]].process_packet(env)
                
            #Lets say that env.timeout(1) represents 1 second, which is the service time
            yield env.timeout(1)
            currentSlotGlobal = currentSlotGlobal + 1

    #Run Linear Backoff calculation
    def linearBackoff(self, queue):
        k = min(queue.N, 1024)
        randVar = random.randint(0,k)
        queue.slotTargetNum = queue.slotTargetNum + randVar
        queue.N = queue.N + 1


def main():
    global currentSlotGlobal, totalPacketsProcessed
    random.seed(RANDOM_SEED)
    
    print("Binary Exponential Backoff Model with 10 Queues, for slot time of 1 and 10 hosts: ")
    for arrival_rate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]:
        print ("{0:<15} {1:<15} {2:<17} {3:<15} {4:<15}".format(
                "Lambda", "TotalSlots","ProcessedPackets","Throughput","PacketSlotCollisions"))
        currentSlotGlobal = 0
        totalPacketsProcessed = 0
        env = simpy.Environment()
        queues = [server_queue(env, arrival_rate) for j in range(10)]
        router = ethernet_model(env, queues)
        env.process(router.runModelBinary(env))
        env.run(until=SIM_TIME)
        print ("{0:<1.2f} {1:<10} {2:<15} {3:<17} {4:<2.5f} {5:<7} {6:<15}".format(
                float(arrival_rate),
                "",
                int(currentSlotGlobal),
                int(totalPacketsProcessed),
                float(float(totalPacketsProcessed)/currentSlotGlobal),
                "",
                int(router.totalCollisions)))

    print("")
    print("Linear Backoff Model with 10 Queues, for slot time of 1 and 10 hosts: ")
    for arrival_rate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]:
        print ("{0:<15} {1:<15} {2:<17} {3:<15} {4:<15}".format(
                "Lambda", "TotalSlots","ProcessedPackets","Throughput","PacketSlotCollisions"))
        currentSlotGlobal = 0
        totalPacketsProcessed = 0
        env = simpy.Environment()
        queues = [server_queue(env, arrival_rate) for j in range(10)]
        router = ethernet_model(env, queues)
        env.process(router.runModelLinear(env))
        env.run(until=SIM_TIME)
        print ("{0:<1.2f} {1:<10} {2:<15} {3:<17} {4:<2.5f} {5:<7} {6:<15}".format(
                float(arrival_rate),
                "",
                int(currentSlotGlobal),
                int(totalPacketsProcessed),
                float(float(totalPacketsProcessed)/currentSlotGlobal),
                "",
                int(router.totalCollisions)))
    
if __name__ == '__main__': main()