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
	def __init__(self, env, B, arrival_rate, Packet_Delay, Server_Idle_Periods):
		self.server = simpy.Resource(env, capacity = 1)
		self.buffer = simpy.Container(env, init=0, capacity=B)
		self.buff_proc = env.process(self.monitor_buffer(env))
		self.env = env
		self.queue_len = 0
		self.flag_processing = 0
		self.packet_number = 0
		self.sum_time_length = 0
		self.start_idle_time = 0
		self.arrival_rate = arrival_rate
		self.Packet_Delay = Packet_Delay
		self.Server_Idle_Periods = Server_Idle_Periods

        def monitor_buffer(self, env):
                while True:
                        if self.buffer.level > B:
                                print('Buffer full: expecting packet loss...')
                                print('You should consider a cache')
                                print('Or a bigger buffer')
                        yield env.timeout(15)

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

""" Packet class """			
class Packet:
	def __init__(self, ID, arrival_time):
		self.ID = ID
		self.arrival_time = arrival_time

class StatObject:
    def __init__(self):
        self.dataset =[]

    def addNumber(self,x):
        self.dataset.append(x)

        
def main():
	print("Simple queue system model:mu = {0}".format(MU))
	print ("{0:<9} {1:<9} {2:<9}".format("Lambda", "B=10", "B=50"))
	random.seed(RANDOM_SEED)
        for arrival_rate in [0.2, 0.4, 0.6, 0.8, 0.9, 0.99]:
            # run the sim until num.packets.in.buff == B
            # yield to packet drop process until transmit packet,
            # clearing buffer: |buffer| = B-1
            
if __name__ == '__main__': main()
