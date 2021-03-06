## This python code is revised from the textbook, chapter 2.7.

## This code accept server port number as the first cmd argument
## and will wait for the text that send from client and print it and send it back.

import socket
import sys
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverPort = int(sys.argv[1])
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('The server is ready ro receive')
while True:
    connectionSocket, addr = serverSocket.accept()
    input1 = connectionSocket.recv(1024).decode()
    print(input1)
    connectionSocket.send(input1.encode())
    connectionSocket.close()