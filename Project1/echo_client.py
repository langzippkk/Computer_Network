## This python code is revised from the textbook, chapter 2.7.

## This code will accpet the server hostname as the first cmd line argument
## And server port as the second argument.
## After running the code, you will be able to enter lines of text and send to
## the server. 

## Example usage: 
## python echo_client.py <host> <port> 

import socket
import sys
serverName = sys.argv[1]
serverPort = int(sys.argv[2])
while True:
    input1 = input('Send a message to server: ')
    if input1:
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect((serverName, serverPort))
        clientSocket.send(input1.encode())
        modifiedInput1 = clientSocket.recv(1024)
        print('The server response is: ', modifiedInput1.decode())
        clientSocket.close()
