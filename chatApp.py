import socket
import _thread
import nmap
import json
import time

onlineDict = {}

"""ip = socket.gethostbyname(socket.gethostname())
server.bind((ip, 12345))"""
print("Welcome to chatApp")
print("what is your name ? (You can use just one word as your nickname. ex: berkay demirtas not accepted)")
name = input()
hostToSendMessage= ""

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
hostIP = s.getsockname()[0]
s.close()

hostIpSplitted = hostIP.split(".")
nmapIP = hostIpSplitted[0]+"."+hostIpSplitted[1]+"."+hostIpSplitted[2]+"."+"0"

def listenerThread():
    #print("listenerThreaddd")
    recievedMessage = {}
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((hostIP, 12345))
        s.listen()
        while 1:
            conn, addr = s.accept()
            with conn:
                #print("Connected by", addr)
                data = conn.recv(10240)
                recievedMessage = json.loads(data)
                #print(recievedMessage["IP"])
                if recievedMessage["type"] == 1:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
                        time.sleep(1)
                        s2.connect((recievedMessage["IP"], 12345))
                        disc = {}
                        disc["type"] = 2
                        disc["IP"] = hostIP  
                        disc["name"] = name
                        discMessage = json.dumps(disc)
                        my_str_as_bytes = str.encode(discMessage)
                        s2.sendall(my_str_as_bytes)
                        onlineDict[recievedMessage["name"]] = recievedMessage["IP"]
                        s2.close()
                if recievedMessage["type"] == 2:
                        onlineDict[recievedMessage["name"]] = recievedMessage["IP"]
                if recievedMessage["type"] == 3:
                        print(recievedMessage["name"] + ": " + recievedMessage["body"])
                

def senderThread():
    print("To send a message, write name of a online user and your message. ex: berkay hello world, to see online users, write 'Online' ")
    while 1:
        message = input()
        if message.lower() == "online":
            for i in onlineDict.keys():
                print(i)
            continue
        nameOfReciver = message.split()[0]
        hostToSendMessage = onlineDict[nameOfReciver]
        message = message.split(' ', 1)[1]
        print("You: "+message)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((hostToSendMessage, 12345))
            except:
                onlineDict.pop(nameOfReciver, None)
                print("User is not online anymore")
                continue
            disc = {}
            disc["type"] = 3
            disc["body"] = message  
            disc["name"] = name
            discMessage = json.dumps(disc)
            my_str_as_bytes = str.encode(discMessage)
            s.sendall(my_str_as_bytes)
            s.close()

print("checking for online users")
nm = nmap.PortScanner()
nm.scan(hosts=nmapIP+"/24", arguments='-n -sP')
hosts_list = [(x, nm[x]['status']['state']) for x in nm.all_hosts()]

upHosts = []
for tup in hosts_list:
    if tup[0] != hostIP:
        upHosts.append(tup[0])


for host in upHosts:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, 12345))
        except:
            continue
        disc = {}
        disc["type"] = 1
        disc["IP"] = hostIP  
        disc["name"] = name
        discMessage = json.dumps(disc)
        my_str_as_bytes = str.encode(discMessage)
        s.sendall(my_str_as_bytes)
        s.close()

_thread.start_new_thread(listenerThread,())  
_thread.start_new_thread(senderThread,())    
  
while 1:
    pass