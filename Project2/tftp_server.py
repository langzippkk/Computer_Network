import socket,sys,random
from threading import Thread,Event
import struct
from _thread import *

SIZE = 1024
READ_SIZE = 512

def Data(opCode,blocknumber,data):
	packet = b'\x00\x03'
	packet += struct.pack('!H', blocknumber)
	packet += data
	return packet

def ACK_write(opCode,ack):
	packet = b'\x00\x04'
	packet += struct.pack('!H', ack)
	return packet

def error(errorCode,msg,socket,clientAddress):
    ACK = struct.pack('!HH', 5, errorCode) + msg.encode() + b'\x00'
    socket.sendto(ACK, clientAddress)
    print('Error: ' + msg)
    exit()



def error_handling_read(previous_packet,timeout_stop,socket,rearorwrite,ack,readData,file,senddata,block,clientAddress):
	timeout_flag = False
	drop_out_times = 0
	previous_ack = ack
	duplicate_flag = True
	last_data = False
	data_length = 512	
	while True:
		if drop_out_times >50 and readData:
			print('your drop rate is too high or the file is too long,try again')
			readData.append(1)
			exit()
		try:
			nextRead, newAddress = socket.recvfrom(1024)
			#print(nextRead)
			opCode, clientAckNum = struct.unpack('!HH', nextRead)
			print("get ACK: ",clientAckNum)

			if opCode == 5:
				print('ERROR')
				error(0,'error',socket,clientAddress)
				break

			elif opCode == 4:
				#print(clientAckNum,ack)
				if clientAckNum == previous_ack and not readData:
					print('duplicate data blocks,resend')
					socket.sendto(previous_packet,clientAddress)
					if last_data and data_length<512:
						readData.append(None)
						print('complete')
						break
				else:
					if timeout_flag == True:
						print("drop packet occur, it takes some time to resend data block")

					data = file.read(READ_SIZE)
					data_length = len(data)
					packet1 = Data(4,block,data)
					socket.sendto(packet1,clientAddress)
					previous_packet = packet1
					previous_length = len(data)
					if last_data and data_length<512:
						print('complete')
						readData.append(None)
						file.close()
						break
					ack += 1
					block +=1
					timeout_flag = False
					previous_ack = clientAckNum
					if len(data) < 512:
						last_data = True
						print('complete if the last DATA not been dropped')
						continue
		except Exception as e:
			## deal with timeout
			if readData:
				print('complete')
				file.close()
				break
			else:
				if 'timed' in str(e) and duplicate_flag:
					duplicate_flag = False
					print('timeout,resend')
					socket.sendto(previous_packet,clientAddress)
					if last_data and data_length<512:
						readData.append(None)
				drop_out_times += 1
				timeout_flag = True
				continue

def error_handling_write(previous_packet,timeout_stop,socket,rearorwrite,ack,readData,file,senddata,block,clientAddress):
	timeout_flag = False
	drop_out_times = 0
	previous_block = block
	duplicate_flag = True
	last_data = False
	data_length = 512
	while True:
		# if drop_out_times >50 and readData:
		# 	print('your drop rate is too high or the file is too long,try again')
		# 	readData.append(1)
		# 	exit()
		try:
			nextRead, newAddress = socket.recvfrom(1024)
			#print(nextRead)
			blockNumber = struct.unpack('!H', nextRead[2:4])[0]
			opCode = struct.unpack('!H', nextRead[:2])[0]
			data = nextRead[4:]
			data_length = len(data)
			print("ACK: ",blockNumber)
			#print(opCode)
			if opCode == 5:
				print('ERROR')
				error(0,'error',socket,clientAddress)
				break

			elif opCode == 3:
				if blockNumber == block and not readData:
					print('duplicate ACK')
					socket.sendto(previous_packet,clientAddress)
					#print(last_data,data_length)
					if data_length<512:
						readData.append(None)
						# print('complete')
						# break
				else:
					duplicate_flag = True
					if timeout_flag == True:
						print("drop packet occur, it takes some time to resend data block")
					file.write(data) 
					packet1 = ACK_write(3,ack)
					socket.sendto(packet1,clientAddress)
					previous_packet = packet1
					ack += 1
					block +=1
					timeout_flag = False
					if last_data and data_length < 512:
						print('complete')
						readData.append(None)
						last_data = True
						file.close()
						break
		except Exception as e:
			## deal with timeout
			if readData:
				print('complete')
				file.close()
				break
			else:
				if 'timed' in str(e) and duplicate_flag:
					duplicate_flag = False
					print('timeout,resend')
					#socket.sendto(previous_packet,clientAddress)
					if data_length<512:
						readData.append(None)
				drop_out_times += 1
				timeout_flag = True
				continue

def readThread(clientAddress,clientRequest,fileName,opCode,timeout):
	print("start read request")

	newsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	ephemeral_port = random.randint(0, 65535)
	while newsocket.bind(('', ephemeral_port)) == False:
		ephemeral_port = random.randint(0, 65535)
	print("using ephemeral_port: ",ephemeral_port)

	try:
		file = open(fileName,'rb')
		## READ
	except:
		msg = error(1,'file not found',newsocket,clientAddress)
		newsocket.sendto(msg,clientAddress)
	block = 1
	ack = 0
	newsocket.settimeout(timeout)
	senddata = file.read(READ_SIZE)
	packet = Data(3,block,senddata)
	newsocket.sendto(packet,clientAddress)
	block += 1
	FLAG1 = True
	while FLAG1:
		## start a new threading for read only
		readData = []
		timeout_stop = Event()
		readthread =Thread(target = error_handling_read, 
						   name='readthread', 
						   args=[packet,timeout_stop,newsocket, 'READ',ack,readData,file,senddata,block,clientAddress],)
		readthread.start()
		readthread.join()
		if len(readData) > 0 and readData[0] == None:
			break
		if len(readData) > 0 and readData[0] == 1:
			break
	newsocket.close()
	print('exit thread')
	exit()

def writeThread(clientAddress,clientRequest,fileName,opCode,timeout):
	print("start write request")

	newsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	ephemeral_port = random.randint(0, 65535)
	while newsocket.bind(('', ephemeral_port)) == False:
		ephemeral_port = random.randint(0, 65535)
	print("using ephemeral_port: ",ephemeral_port)
		
	try:
		file = open(fileName,'ab')
		## READ
	except:
		msg = error(1,'file not found',newsocket,clientAddress)
		newsocket.sendto(msg,clientAddress)
	block = 0
	ack = 0
	newsocket.settimeout(timeout)
	senddata = ACK_write(4,ack)
	newsocket.sendto(senddata,clientAddress)
	ack += 1
	FLAG2 = True

	while FLAG2:    
	## start a new threading for write only
		readData = []
		timeout_stop = Event()
		readthread =Thread(target = error_handling_write, 
						   name='writethread', 
						   args=[senddata,timeout_stop,newsocket, 'WRITE',ack,readData,file,senddata,block,clientAddress],)
		readthread.start()
		readthread.join()
		if len(readData) > 0 and readData[0] == None:
			break
		if len(readData) > 0 and readData[0] == 1:
			break
	newsocket.close()
	print('exit thread')
	exit()




def main():
	FLAG = True
	server = int(sys.argv[1])
	socket1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	socket1.bind(('', server))
	timeout = int(sys.argv[2])/1000
	print("Server is listenning from port: ", server)

	while(FLAG):
		clientRequest,clientAddress=socket1.recvfrom(SIZE)
		print('connect to ', clientAddress)
		opCode = struct.unpack('>h', clientRequest[0:2])
		fileName = clientRequest[2:-7].decode('ASCII')
		print(fileName)
		if opCode[0] == 1:
			start_new_thread(readThread,(clientAddress,clientRequest,fileName,opCode,timeout))
		elif opCode[0] == 2:
			start_new_thread(writeThread,(clientAddress,clientRequest,fileName,opCode,timeout))
		else:
			pass
	socket.close()








if __name__ == "__main__":
	main()