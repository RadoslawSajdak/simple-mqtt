import socket
## Get local interface ip ##
import netifaces as ni
ni.ifaddresses('wlan0')
from time import sleep

HOST = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
PORT = 3000
room = "127.0.0.1"
payload = "+/cars"
MESSAGE = b"Hej"
def connect():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((room, PORT))
        sleep(3)
        s.sendall(MESSAGE)
        
        while(1):
            s.sendall(input().encode())
            #data = s.recv(1024)
            #print(data)

        s.shutdown(socket.SHUT_RDWR)
        s.close()
    sleep(1)

if __name__=="__main__":
    connect()