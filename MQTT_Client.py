import socket
import sys
from os import _exit
## Get local interface ip ##
import netifaces as ni
ni.ifaddresses('wlan0')

from time import sleep
import threading

HOST = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']

# Overwriten in main #
PORT = 3007
room = "192.168.0.142"

def reading_thread(socket):
    """ We are reading data in second thread to make it asynchronous """
    while(1):
        data = socket.recv(1024).decode('utf-8')
        print(data)
        if data == "":
            print("Leaving")
            _exit(0)


def connect():
    """ 
    Main client function.
    In first thread app sends data from input and in the second it's reading incoming data.

    Using input:
    +/[topic] - subscribe topic
    -/[topic] - unsubscribe topic
    p/[topic]/[data] - publish data in topic

    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((room, PORT))
        thrd = threading.Thread(target=reading_thread, args = (s,))
        thrd.start()

        while(1):
            s.sendall(input().encode())
            
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        

import struct
def multicast_question():
    multicast_group = "224.1.1.1"
    multicast_port = 7000
    
    MULTICAST_TTL = 2
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
    
    password = bytearray(input("Put password to access broker: "),"utf-8")
    sock.sendto(password, (multicast_group, multicast_port)) #send password to broker 
    
    mreq = struct.pack("4sl", socket.inet_aton(multicast_group), socket.INADDR_ANY) 
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    
    message = sock.recv(1024).decode() #Wait for broker answer if access is granted
    try:
        room, PORT = message.split("|") #Port is string! You have to format it into int
        return (room, int(PORT))
    except:
        print(message)
        exit(0)

if __name__=="__main__":
    try:
        room = str(sys.argv[1])
        PORT = int(sys.argv[2])
        print(room, PORT)
        connect()
    except KeyboardInterrupt:
        exit(0)
    except:
        print("To run script use: python3 [name] [broker ip] [port] or give password")
        room, PORT = multicast_question()
        connect()
    