import sys
import struct
import os
import socket
import argparse
import time
from ipaddress import ip_address
from threading import Timer
import argparse

count = 0
received = 0

def Checksum(message,send_receive):
	'''
	16 bits checksum
	'''
	maxNumber = 1<<16
	temp = 0
	n = len(message)
	for i in range(0,n,2):
		# since checksum is 16bits
		temp += (message[i+1]+ (message[i]*256))
	temp &= 0xffffffff
	temp = (temp>>16) + (temp & 0xffff)
	temp += (temp>>16)
	if send_receive:
	 # mask(make ZEROs) all but the lowest 16 bits of the number
		return struct.pack('!H',(~temp & 0xffff))
	else:
		return (temp == 65535)

def printMessage(time_list,IP,COUNT,end,start):
	print('--- {} ping statistics ---'.format(IP))
	global received
	total_time = sum(time_list)
	if len(time_list)>0:
		min_val = min(time_list)
		max_val = max(time_list)
	else:
		min_val = 0
		max_val = 0
	if received > 0:
		print('{} / {} received/transmitted, {}% loss, time {} ms'.format(
				received, COUNT, 100-received/COUNT*100, int(end[0]-start[0])))
		print('rtt min/avg/max = {}/{}/{}'.format(min_val, int(total_time/received), max_val))
	else:
		print('{} / {} received/transmitted,  {}% loss, time {} ms'.format(
				0, COUNT, 100, int(end[0]-start[0])))
		print('rtt min/avg/max = 0/0/0')


def client(start,end):
	seqno = 1
	time_list = []
	package_list = []
	idf = os.getpid()
	#print(idf)
	input_total = argparse.ArgumentParser(description='client')
	input_total.add_argument('--server_ip', default='127.0.0.1', type=str, help='servers ip')
	input_total.add_argument('--server_port', default=3158, type=int, help='port')
	input_total.add_argument('--count', default=3, type=int, help='# of pings')
	input_total.add_argument('--period', default=1000, type=int, help='wait period')
	input_total.add_argument('--timeout', default=100, type=int, help='timeout')
	argument = input_total.parse_args()
	IP = argument.server_ip
	PORT = argument.server_port
	COUNT = argument.count
	PERIOD = argument.period
	TIMEOUT = argument.timeout
	try:
		ip_address(IP)
	except ValueError:
		print('invalid IP')
		exit()
	try:
		PORT = int(PORT)
		COUNT = int(COUNT)
		PERIOD = int(PERIOD)//1000
		TIMEOUT = int(TIMEOUT)//1000
	except:
		print('please enter an integer value')
		exit()
	type1 = struct.pack('!B', 8)
	code = struct.pack('!B', 0)
	print('PING {}'.format(IP))
	idf = idf % 65535
	timeout_flag = [False]
	global count
	threads = []
	start[0] = int(time.time() * 1000)
	for i in range(COUNT):
		thread = Timer(PERIOD,send_ping,args =[TIMEOUT,package_list,timeout_flag,time_list,start,type1,code,idf,seqno+i,COUNT,PERIOD,IP,PORT,end])
		threads.append(thread)
		#time.sleep(PERIOD)
	for thread in threads:
		## start all threads
		thread.start()
	for thread in threads:
		## wait all finished
		thread.join()
	#print(time_list)
	end[0] = int(time.time()*1000)
	printMessage(time_list,IP,COUNT,end,start)


def send_ping(TIMEOUT,package_list,timeout_flag,time_list,start,type1,code,idf,seqno,COUNT,PERIOD,IP,PORT,end):
	finish_flag = [False]
	ping_socket =socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	ping_socket.settimeout(TIMEOUT)
	idf_bit = struct.pack('!H',idf)
	seq_bit = struct.pack('!H',seqno)
	current= int(time.time() * 1000)
	current_time = current.to_bytes(6, byteorder='big')
	initial_checksum = struct.pack('!H', 0)
	message = type1 + code + initial_checksum + idf_bit + seq_bit + current_time
	message =  type1 + code + Checksum(message,True) + idf_bit + seq_bit + current_time
	global count
	ping_socket.sendto(message,(IP,PORT))
	# if count == 0:
	# 	start[0] = current
		#print(start,end,count)
	count += 1
	if count <= COUNT:
		receive_pong(package_list,timeout_flag,time_list,finish_flag,COUNT,IP,ping_socket,end)
	elif count > COUNT:
		ping_socket.close()
		return

def receive_pong(package_list,timeout_flag,time_list,finish_flag,COUNT,IP,ping_socket,end):
	estimate_time = 0
	try:
		message,server = ping_socket.recvfrom(1024)
		current_time = int(time.time()*1000)
		previous_time  = int.from_bytes(message[8:],byteorder='big')
		estimate_time = current_time - previous_time
		seqno_pong =  struct.unpack('!H', message[6:8])
		package_list.append(seqno_pong[0])
		#print(package_list)
		if seqno_pong == COUNT:
			finish_flag[0] = True	
		if Checksum(message,False):
			time_list.append(estimate_time)
			print('PONG {}: seq={} time={} ms' .format(server[0], seqno_pong[0], estimate_time))
			global count,received
			received +=1
			if count == (COUNT):
				finish_flag[0] = True
				return
		else:
			 print('Checksum verification failed for echo reply seqno={}' .format(seqno_pong[0]))
			 return
	except:
		timeout_flag[0] = True
		end[0] = int(time.time() * 1000)
		#time_list.append(0)
		#print(time_list)
		return

if __name__ == "__main__":
	start = [0]
	end = [0]
	client(start,end)