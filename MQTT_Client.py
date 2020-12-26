import socket
import sys
## Get local interface ip ##
import netifaces as ni
ni.ifaddresses('wlan0')
from time import sleep
import threading

HOST = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
PORT = 3000
room = "192.168.0.144"

def reading_thread(socket):
    while(1):
        data = socket.recv(1024).decode('utf-8')
        print(data)


def connect():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((room, PORT))
        thrd = threading.Thread(target=reading_thread, args = (s,))
        thrd.start()
        while(1):
            s.sendall(input().encode())
            
        s.shutdown(socket.SHUT_RDWR)
        s.close()
    sleep(1)

if __name__=="__main__":
    try:
        room = str(sys.argv[1])
        PORT = int(sys.argv[2])
        print(room, PORT)
        connect()
        
    except: #TODO: Add exceptions
        print("To run script use: python3 [name] [broker ip] [port]")
    