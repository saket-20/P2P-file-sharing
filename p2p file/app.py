import socket
import threading
from flask import Flask, request, render_template,Response
import requests
import atexit

app = Flask(__name__)
file_lock = threading.Lock()
peers = []

def handle_client(client_socket):
    request=client_socket.recv(1024).decode()
    filename=request.split(":")[1]
    try:
        with open("Shared/"+filename, "rb") as file:
            data=file.read()
            client_socket.sendall(data)
    except FileNotFoundError:
        client_socket.sendall(b"File not found")

    client_socket.close()


@app.route("/")
def index():
    return render_template("index.html")

@app.get("/registerpeer")
def registerpeer():
    return render_template("registerpeerform.html")
@app.post("/registerpeer")
def addpeer():
    ip=request.form['ip']
    port=request.form['port']
    peer_details={
        "ip":ip,
        "port":port
    }
    try:
        response = requests.post("http://"+centralserverip+":12345", json=peer_details)
    except Exception as e:
        return Response("Central Index Server Currently down")
    return Response("Peer Successfully Registered")

def getallpeers():
    peerslist=requests.get("http://"+centralserverip+":12345/peers")
    print(peerslist.json())
    for i in peerslist.json():
        ipport=(i['ip'],int(i['port']))
        peers.append(ipport)
    print(peers)
    return peers 

def getpeers(filename):
    peerslist=requests.get("http://"+centralserverip+":12345/returnpeerswithaudio/"+filename)
    print(peerslist.json())
    for i in peerslist.json():
        ipport=(i['ip'],int(i['port']))
        peers.append(ipport)
    print("Peers with requested file are:")
    print(peers)
    print("END")
    return peers 

@app.get("/isNodeActive")
def isNodeActive():
    return Response("Active")


@app.get("/AddFiletoSharedFolder")
def ShareNewFileForm():
    return render_template("ShareNewFile.html")

@app.post("/AddFiletoSharedFolder")
def savefiletosharedfolder():
    try:
        newfile=request.files['newfile']
        filename=request.form['filename']
        if not filename.endswith('.mp3'):
            return Response("File format invalid. Only MP3 files are allowed.")
        newfile.save("Shared/"+filename)
        filedetails={"filename":filename}
        requests.post("http://"+centralserverip+":12345/addfiletopeer/{}".format(hostip),json=filedetails)
    except Exception as e:
        print(e)
        return Response("Error")
        
    return Response("File Succesfully Added to Shared Folder")


@app.route("/download", methods=["GET"])
def download():
    filename = request.args.get("filename")
    peers.clear()
    getpeers(filename)
    print("Peers")
    print(peers)
    ActivePeers=[]
    for peer in peers:
        resp="Inactive"
        try:
            resp=requests.get("http://"+peer[0]+":"+"8001"+"/"+"isNodeActive").text
        except Exception as e:
            resp="Inactive"
        if resp=="Active":
            ActivePeers.append(peer)
    print("ActivePeers")
    print(ActivePeers)
    for peer in ActivePeers:#peers:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(peer)
            request_message = f"GET:{filename}"
            client_socket.send(request_message.encode())

            data = client_socket.recv(1024)
            print("data1")
            #print(data)
            if data == b"File not found": 
            #if data.decode()=="File not found":    
                continue
            else:
                with open("Shared/"+filename, "wb") as file:
                    file.write(data)
                    while True:
                        data = client_socket.recv(1024)
                        #print(data)
                        if not data:
                            break
                        file.write(data)
                return "File transfer complete."
        except Exception as e:
            print(f"Error occurred while downloading from {peer}: {e}")
        finally:
            client_socket.close()

    return "File not found on any peer."


def start_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(5)

    print(f"Server listening on port {port}")

    while True:
        client_socket, client_address = server_socket.accept()
        threading.Thread(target=handle_client, args=(client_socket,)).start()

@app.post("/remove")
def removepeerfromserver():
    requests.post("http://"+centralserverip+":12345/removepeer/{}".format(hostip))
    print(hostip)
    #print("http://"+centralserverip+":12345/removepeer/{}".format(hostip))
    print("Peer removed :)")
    return Response("Peer Removed")

def join_network():
    global hostip
    hostname=socket.gethostname()
    ip=socket.gethostbyname(hostname)
    hostip=ip
    peer_details={
        "ip":ip,
        "port":5000
    }
    response = requests.post("http://"+centralserverip+":12345", json=peer_details)
    print(response.text)
#ondelete cascade
def getcentralserverip(ip):
    global centralserverip
    centralserverip=ip

if __name__ == "__main__":
    serverip="192.168.0.137"
    threading.Thread(target=start_server, args=(5000,)).start()
    getcentralserverip(serverip)
    join_network()
    app.run(host="0.0.0.0", port=8001)
    
#refactor