from db import db  
class PeerAudio(db.Model):
    __tablename__="peer_audio"
    id=db.Column(db.Integer,primary_key=True)
    audio_id=db.Column(db.Integer,db.ForeignKey('audio.id'))
    peer_id=db.Column(db.Integer,db.ForeignKey('peer.id'))