import socket
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
            
            #data = s.recv(1024)
            #print(data)
            s.sendall(input().encode())
            
        s.shutdown(socket.SHUT_RDWR)
        s.close()
    sleep(1)

if __name__=="__main__":
    connect()