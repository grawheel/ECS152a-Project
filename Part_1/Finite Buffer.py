# Part 1: Finite Buffer Simulation
# simulation of a simple queueing system with a finite buffer
# to study the probability of packet loss as a function of
# the buffer size B and the traffic intensity

import random
import simpy
import math


# lambda: Packet arrival_rate
# mu: Packet service rate R/L
# R: outgoing link rate, bps
# L: Packet length, random variable

RANDOM_SEED = 29
#For true random:
# RANDOM_SEED = <tt>os.</tt><tt>urandom</tt>(<em>n</em>)
SIM_TIME = 1000000
#   To keep things simple, let mu = 1 pkt/sec
MU = 1

#Need to simulate and plot (or tabulate) the following:
# 1) Determine packet loss probability Pd when:
#       arrival_rate = lambda = [0.2; 0.4; 0.6; 0.8; 0.9; 0.99]
#       B = 10; 50
# 2) Compare these results using formula derived in class/discussion

""" Queue system  """		
class server_queue:
        #initialize server
	def __init__(self, env, Dropped_Packets, NonDropped_Packets, B, arrival_rate, Packet_Delay, Server_Idle_Periods):
		self.server = simpy.Resource(env, capacity = 1)
		#self.buffer = simpy.Container(env, init=0, capacity=B)
		self.buff_proc = env.process(self.monitor_buffer(env))
		self.env = env
		self.queue_len = 0
		self.buffer_max = B
		self.flag_processing = 0
		self.packet_number = 0
		self.sum_time_length = 0
		self.start_idle_time = 0
		self.arrival_rate = arrival_rate
		self.Packet_Delay = Packet_Delay
		self.Dropped_Packets = Dropped_Packets
		self.NonDropped_Packets = NonDropped_Packets
		self.Server_Idle_Periods = Server_Idle_Periods

        #process a packet
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
			if self.queue_len <= self.buffer_max:
				self.NonDropped_Packets.addNumber(1)
				self.packet_number += 1
				  # packet id
				arrival_time = env.now  
				#print("packet arrival %d" % self.packet_number)
				new_packet = Packet(self.packet_number,arrival_time)
				if self.flag_processing == 0:
					self.flag_processing = 1
					idle_period = env.now - self.start_idle_time
					self.Server_Idle_Periods.addNumber(idle_period)
					#print("Idle period of length {0} ended".format(idle_period))
				self.queue_len += 1
				env.process(self.process_packet(env, new_packet))
			else:
				self.Dropped_Packets.addNumber(1)


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

        
def main():
	print("Simple queue system model:mu = {0}".format(MU))
	print ("{0:<9} {1:<9} {2:<9}".format("Lambda", "B=10", "B=50"))
	random.seed(RANDOM_SEED)
	for B in [10, 50]
        for arrival_rate in [0.2, 0.4, 0.6, 0.8, 0.9, 0.99]:
            # run the sim until num.packets.in.buff == B
            # yield to packet drop process until transmit packet,
            # clearing buffer: |buffer| = B-1
        	env = simpy.Environment()
            Packet_Delay = StatObject()
            Server_Idle_Periods = StatObject()
			Dropped_Packets = StatObject()
			NonDropped_Packets = StatObject()
			router = server_queue(env, Dropped_Packets, NonDropped_Packets, B, arrival_rate, Packet_Delay, Server_Idle_Periods)
			env.process(router.packets_arrival(env))
            env.run(until=SIM_TIME)
            print ("{0:<9} {1:<9}".format(
				int(Dropped_Packets.count()),
				int(NonDropped_Packets.count())))
            
if __name__ == '__main__': main()
