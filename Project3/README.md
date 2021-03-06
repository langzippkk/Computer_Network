Dependency:
1) Python 3.5

   threading package

2) Start your Ping server first by:

    java -jar pingserver.jar --port=<port> [--loss_rate=<rate>] [--bit_error_rate=<rate>][--avg_delay=<delay>]]

    for example:
    java -jar pingserver.jar --port=56789 --loss_rate=0.0 --bit_error_rate=0.0  --avg_delay=2000

3) Then start you Ping client by:

    python3 ping_client.py --server_ip=<server ip addr> --server_port=<server port> --count=<number of pings to send> --period=<wait interval> --timeout=<timeout>
    
    for example:
    python3 ping_client.py --server_ip=127.0.0.1 --server_port=56789 --count=10 --period=1000 --timeout=60000

4) The client will send ping request to server and receive reply from server.
   In this process, the client will verifies the checksum for reply from server.
   The timeout is handled by Timer function in threading package.

5) At last, the aggregate statistics will be printed after all threads finished(which is
	done using threading.join()).