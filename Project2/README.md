Dependency:

	1. Python 3.7

Run the program:

	1. Run the tftp_server by python3 tftp_server.py <host> <timeout>
	for example, python3 tftp_server.py localhost 100

Function:

	1. The tftp_server will be able handle multiple clients read
	and write requests using multi-threading.
	2. The server should be able to handle successive requests for 
	a client without restarting it.
	3. Each time it call a read or write request, it will assign
	a unique random port number for each request.
	4. The server keep checking ACK/DATA block number to track if there
	is package lost, if so it will retransmit the packet.
	5. The server also handles timeout using socket.settimeout() function
	together with a try..., except... to make sure it retransmit after
	timeout.