# this is the database model
from . import db
from flask_login import UserMixin

# ticket -- boleto
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)    # clave primaria
    tick = db.Column(db.Integer)                    # tiquete - numero aleatorio
    user_id = db.Column(db.Integer, db.ForeignKey('customer.id'))      # clave foranea user
    lot_id = db.Column(db.Integer, db.ForeignKey('lot.id'))

# lot -- sorteo
class Lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prize = db.Column(db.String(200))
    t_price = db.Column(db.Integer)
    date = db.Column(db.DateTime(timezone=True))
    tickets = db.relationship('Ticket', backref="lot")
   
# user - usuario
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)    # clave primaria
    email = db.Column(db.String(50))                # id unico
    contact = db.Column(db.Integer)                 # celular
    name = db.Column(db.String(150))                # nombre
    tickets = db.relationship('Ticket', backref="customer")

# admin - cuenta administrador
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30))
    passwd = db.Column(db.String(30))