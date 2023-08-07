from flask import Flask,request,Response,render_template,jsonify
from db import db
from models.peer import PeerModel
from models.peeraudio import PeerAudio
from models.audio import AudioModel
from flask_smorest import Api
import os
def create_app(db_url=None):
    app = Flask(__name__)
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Central Server REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    api = Api(app)

    with app.app_context():
        db.create_all()

    @app.get("/peers")
    def SendPeerList():
        allpeers=PeerModel.query.all()
        peerlist=[]
        for peer in allpeers:
            peerdict={
                "ip":peer.ip,
                "port":peer.port
            }
            peerlist.append(peerdict)
        return jsonify(peerlist)
    
    @app.get("/")
    def index():
        return render_template("index.html")
    
    @app.post("/")
    def addpeer():
        ip=request.json['ip']
        port=request.json['port']
        instance=PeerModel.query.filter_by(ip=ip).first()
        if instance:
            return Response("Peer Exists")
        else:
            peer=PeerModel(ip=ip,port=port)
            db.session.add(peer)
            db.session.commit()
            print(peer)
            return Response("Peer Added Successfully")
    

    @app.post("/removepeer/<string:ip>")
    def removepeer(ip):
        try:
            peer=PeerModel.query.filter_by(ip=ip).first_or_404()
            db.session.delete(peer)
            db.session.commit()
            print(peer)
            return Response("Peer Has Been Removed")
        except Exception as e:
            return(e)
    @app.post("/addfiletopeer/<string:ip>")
    def addaudiotopeers(ip):
        filename=request.json['filename']
        print(filename)
        print(ip)
        audio=AudioModel(name=filename)
        db.session.add(audio)
        db.session.commit()
        peer=PeerModel.query.filter_by(ip=ip).first_or_404()
        peer.audio.append(audio)
        db.session.add(peer)
        db.session.commit()
        for p in PeerModel.query.all():
            for a in p.audio:
                print(p.ip)
                print(p.port)
                print(a.name)
        return Response("Success")
    
    @app.get("/returnpeerswithaudio/<string:audioname>")
    def returnpeerswithaudio(audioname):
        PeersWithAudioList=[]
        Peers=PeerModel.query.all()
        print(Peers)
        for peer in Peers:
            print(peer.ip)
            print("Peeraudiolist")
            print(peer.audio)
            for audio in peer.audio:
                print("audio.name:{}".format(audio.name))
                print("audioname:{}".format(audioname))
                if audio.name==audioname:
                    peerdict={
                        "ip":peer.ip,
                        "port":peer.port
                    }
                    PeersWithAudioList.append(peerdict)
        return jsonify(PeersWithAudioList)
    #refactor

    return app


create_app()