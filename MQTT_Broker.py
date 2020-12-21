import socket,select
## Get local interface ip ##
import netifaces as ni
ni.ifaddresses('wlan0')
from time import sleep

HOST = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
HOST = "127.0.0.1"
PORT = 3000
MAX_DEVICES = 10
WELCOME_MESS = b"You're welcome at server\n"

def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        s.bind((HOST, PORT))
        s.listen(MAX_DEVICES)
        inputs = [s]
        while(1):
            infds, outfds, errfds = select.select(inputs, inputs, [], MAX_DEVICES)
            if len(infds) != 0:
                for fds in infds:
                    if fds is s:
                        conn, addr = fds.accept()
                        inputs.append(conn)
                        print("Connection from ", addr[0])
                        conn.sendall(WELCOME_MESS)
                    else:
                        data = fds.recv(1024)                    
                        if not data:
                            inputs.remove(fds)
                        else:
                            print(data)

if __name__ == "__main__":
    run_server()