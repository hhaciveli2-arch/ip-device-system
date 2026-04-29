from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    sicil_no = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

class Region(db.Model):
    __tablename__ = "regions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    branches = db.relationship("Branch", backref="region", lazy=True)

class Branch(db.Model):
    __tablename__ = "branches"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    region_id = db.Column(db.Integer, db.ForeignKey("regions.id"), nullable=False)

class Device(db.Model):
    __tablename__ = "devices"  
    id = db.Column(db.Integer, primary_key=True)

    pgm_no = db.Column(db.String(50))
    mudurluk = db.Column(db.String(255))
    amirlik = db.Column(db.String(255))
    sube = db.Column(db.String(255))
    ip_no = db.Column(db.String(50))
    mac_adresi = db.Column(db.String(50))
    isletim_sistemi = db.Column(db.String(255))
    pc_markasi = db.Column(db.String(255))
    pc_modeli = db.Column(db.String(255))
    islemci = db.Column(db.String(255))
    hard_disk = db.Column(db.String(255))
    ram_boyutu = db.Column(db.String(50))
    ram_modeli = db.Column(db.String(255))
    bit_tipi = db.Column(db.String(50))
    ekran_karti = db.Column(db.String(255))
    ses_karti = db.Column(db.String(255))
    network_karti = db.Column(db.String(255))
    ana_kart = db.Column(db.String(255))
    ekran = db.Column(db.String(255))
    yazici = db.Column(db.String(255))
    aciklama = db.Column(db.Text)

class IpPool(db.Model):
    __tablename__ = "ip_pool"
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), unique=True, nullable=False)
    is_assigned = db.Column(db.Boolean, default=False)

class AuditLog(db.Model):
    __tablename__ = "audit_log"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    action = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
