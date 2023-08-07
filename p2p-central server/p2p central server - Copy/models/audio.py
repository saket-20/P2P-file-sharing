from db import db
class AudioModel(db.Model):
    __tablename__="audio"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,unique=True,nullable=False)
    #total_chunks=db.Column(db.Integer,unique=False,nullable=False)
    peer = db.relationship("PeerModel", back_populates="audio", secondary="peer_audio")
