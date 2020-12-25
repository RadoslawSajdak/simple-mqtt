import socket,select
## Get local interface ip ##
import netifaces as ni
ni.ifaddresses('wlan0')
from time import sleep

HOST = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
HOST = "192.168.0.144"
PORT = 3000
MAX_DEVICES = 10
WELCOME_MESS = b"You're welcome at server\n"
SUBSCRIBER = b"NOW YOURE SUBSCRIBER"
topics = {
    "test0" : []
}

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
                        print("Connection from ", addr[0],addr[1])
                        conn.sendall(WELCOME_MESS)
                    else:
                        data = fds.recv(1024)         
                        # Subscribing #
                        if str(data).find("+/") > 0:
                            new_topic = str(data).split("/")
                            new_topic = new_topic[1][:len(new_topic[1])-1]
                            print("Subscribing: ",new_topic)
                            sub = inputs[inputs.index(fds)]
                            try:
                                topics[new_topic].append(sub)
                            except:
                                topics[new_topic] = [sub]
                            sub.sendall("You're subscriber of ".encode() + new_topic.encode())
                        # Publishing #
                        elif str(data).find("p/") > 0:
                            print("Publishing: ")
                            rcv = str(data).split("/")
                            try:
                                pub = rcv[2][:len(rcv[2]) - 1]
                                top = rcv[1][:len(rcv[1])]
                                print(pub, "in", top)

                                # Send to all subscribers #
                                for snd in topics[top]:
                                    snd.sendall((pub + " <-from " + top).encode())
                            except:
                                print("syntax is p/topic/message")
                        # Unsubscribing #
                        elif str(data).find("-/") > 0:
                            rm_topic = str(data).split("/")
                            rm_topic = rm_topic[1][:len(rm_topic[1])-1]
                            print("unsubscribing: ",rm_topic)
                            usub = inputs[inputs.index(fds)]
                            try:
                                topics[rm_topic].remove(usub)
                                usub.sendall(("Unsubscribed from " + rm_topic).encode())
                            except:
                                usub.sendall(("You're not subscriber of " + rm_topic).encode())
                        if not data:
                            inputs.remove(fds)
                        else:
                            print(data)

if __name__ == "__main__":
    run_server()