from db import db
class PeerModel(db.Model):
    __tablename__="peer"
    id=db.Column(db.Integer,primary_key=True)
    ip=db.Column(db.String,unique=True,nullable=False)
    port=db.Column(db.Integer,unique=False,nullable=True)
    audio = db.relationship("AudioModel", back_populates="peer", secondary="peer_audio")

#cascade='all,delete-orphan'