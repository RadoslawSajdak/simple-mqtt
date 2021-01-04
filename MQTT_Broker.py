import socket,select
## Get local interface ip ##
import netifaces as ni
from time import sleep
import sys
import logging

#multicast imports
import threading
import struct
from daemonize import Daemonize

ni.ifaddresses('wlan0')
HOST = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
#HOST = "192.168.0.144" # Uncomment this line to set server ip manually
PORT = 3000
MAX_DEVICES = 10
WELCOME_MESS = "You're welcome at server\n +/[topic] - subscribe topic \n -/[topic] unsubscribe topic \n p/[topic]/[data] - publish data in topic \n Leave broker - exit"

# Multicast
multicast_group = "224.1.1.1"
multicast_port = 7000
multicast_password = b"SocketProgramming"

# Logging to file
logging.basicConfig(filename='/var/log/MQTT_Broker.log',format='%(levelname)s %(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p', filemode='a', level=logging.INFO)
logger = logging.getLogger(__name__)

def run_multicast_srv():

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sck:
        sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sck.bind((multicast_group,multicast_port))
        
        # '4s' - arg1 is 4char string, l - arg2 is long int
        mreq = struct.pack("4sl", socket.inet_aton(multicast_group), socket.INADDR_ANY) 
        sck.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while 1:
            data_multi,client = sck.recvfrom(1024)
            if (data_multi == multicast_password):
                logger.warning("New multicast connection from %s", client)
                # Send broker address to UDP client
                sck.sendto(bytearray((HOST + "|" + str(PORT)),"utf-8"),client)
            else:
                logger.error("Multicast access from %s denied!", client)
                sck.sendto(b"Connection refused",client)


topics = {          # Dictionary for topics joined with list of it's subscribers
    "test0" : []
}

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.bind((HOST, PORT))
        s.listen(MAX_DEVICES)
        inputs = [s]
        # Main loop #
        while(1):
            infds, outfds, errfds = select.select(inputs, inputs, [], MAX_DEVICES)
            if len(infds) != 0:
                for fds in infds:
                    if fds is s:
                        conn, addr = fds.accept()
                        inputs.append(conn)
                        logger.info("Connection from %s %s", addr[0],addr[1])
                        conn.sendall(WELCOME_MESS.encode())
                    else:
                        """
                            All received data should be formated with pattern:
                            subscribing: +/[topic]
                            unsubscribing: -/[topic]
                            publishing: p/[topic to publish in]/[Message]

                            Other data will be printed on screen and removed from the memory
                        """
                        data = fds.recv(1024)    
                        cli_sock = inputs[inputs.index(fds)]
                        cli_addr = cli_sock.getpeername()
                        
                        # Subscribing #
                        if str(data).find("+/") > 0:
                            
                            new_topic = str(data).split("/")            # Extract topic from string
                            new_topic = new_topic[1][:len(new_topic[1])-1]
                            
                            try:
                                topics[new_topic].append(cli_sock)
                            except:
                                topics[new_topic] = [cli_sock]
                            logger.info("%s Subscribed: %s",cli_addr, new_topic)

                            cli_sock.sendall("You're subscriber of ".encode() + new_topic.encode())         # Return message to client
                        # Publishing #
                        elif str(data).find("p/") > 0:
                            rcv = str(data).split("/")
                            
                            try:
                                pub = rcv[2][:len(rcv[2]) - 1]
                                top = rcv[1][:len(rcv[1])]
                                
                                # Send to all subscribers #
                                for snd in topics[top]:
                                    snd.sendall((pub + " <-from " + top).encode())
                                logger.info("%s Published %s in %s",cli_addr, pub, top)
                            except:
                                cli_sock.sendall("syntax is p/topic/message".encode())


                        # Unsubscribing #
                        elif str(data).find("-/") > 0:
                            rm_topic = str(data).split("/")
                            rm_topic = rm_topic[1][:len(rm_topic[1])-1]

                            try:
                                topics[rm_topic].remove(cli_sock)
                                cli_sock.sendall(("Unsubscribed from " + rm_topic).encode())
                            except:
                                cli_sock.sendall(("You're not subscriber of " + rm_topic).encode())
                            
                            logger.info("%s Unsubscribed from: %s",cli_addr, rm_topic)
                        # Client disconnect
                        elif str(data).find("exit") > 0:
                            logger.info("%s Disconnected", cli_addr)
                            cli_sock.sendall(b"Bye")
                            cli_sock.close()
                            inputs.remove(cli_sock)
                        else:
                            logger.warning("Wrong data came from %s! %s",cli_addr,data)
                        if not data:
                            inputs.remove(fds)
                        



def main():
    

    global HOST, multicast_password, logger

    try:
        HOST = ni.ifaddresses(sys.argv[1])[ni.AF_INET][0]['addr']
        multicast_password = bytearray(sys.argv[2], "utf-8")
    except:
        pass
    logger.info( "Running server on %s : %s | Max devices: %d", HOST,PORT,MAX_DEVICES)
    logger.info( "Multicast password is: %s", multicast_password.decode())

    thr = threading.Thread(target=run_multicast_srv)
    thr.start()

    
    run_server()

pid = "/tmp/MQTT_Broker_d.pid"
if __name__ == "__main__":
    daemon = Daemonize(app="MQTT_Broker",pid = pid, action = main, auto_close_fds=False, logger=logger)
    daemon.start()