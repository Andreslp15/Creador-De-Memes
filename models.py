import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    usuario_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_usuario = db.Column(db.String(255), nullable=False, unique=True)
    correo_electronico = db.Column(db.String(300), unique=True, nullable=False)
    contraseña = db.Column(db.String(300), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.datetime.now)

    memes_usuario = db.relationship('Meme', backref='usuario_creador')
    plantillas_usuario = db.relationship('Plantilla', backref='usuario_creador')


class Plantilla(db.Model):
    __tablename__ = 'plantillas'
    plantilla_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imagen = db.Column(db.String(255), nullable=False)
    nombre_plantilla = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.datetime.now)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.usuario_id'), nullable=False)

    memes_asociados = db.relationship('Meme', backref='plantilla_asociada')


class Meme(db.Model):
    __tablename__ = 'memes'
    meme_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    imagen = db.Column(db.String(300), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.datetime.now)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.usuario_id'), nullable=False)
    plantilla_id = db.Column(db.Integer, db.ForeignKey('plantillas.plantilla_id'), nullable=False)

    usuario = db.relationship('Usuario', backref='memes')
    plantilla = db.relationship('Plantilla', backref='memes_utilizados')
