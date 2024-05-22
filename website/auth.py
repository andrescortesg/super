## this manages database and tickets

from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import Customer, Ticket, Lot, User
from . import db
from werkzeug.security import generate_password_hash, check_password_hash # this is used for login credential, hashing and stuff
from random import randint
from flask_login import login_user, login_required, logout_user, current_user

import mercadopago

auth = Blueprint('auth', __name__)

# get lot by lot_id
def get_lot(lot_id):
    my_lot = db.session.execute(db.select(Lot).filter_by(id=lot_id)).scalar()

    if my_lot:
        lot_res = {
            'prize': my_lot.prize,          # description of the product
            't_price': my_lot.t_price       # price of ticket
        }
        
        return lot_res
    else:
        return None 

def check_tick(lot_id):
    tick_db = db.session.execute(db.select(Ticket).filter_by(lot_id=lot_id)).scalars()
    tick_array = []

    # get all tickets from a lot in array form
    for row in tick_db:
        tick_array.append(row.tick)

    # check if there's any tickets left
    if len(tick_array) == 10000:
        flash("Ya no hay más boletas")
        return False
    else:
        return True
        
def get_ticket(user, lot_id):
    tick_db = db.session.execute(db.select(Ticket).filter_by(lot_id=lot_id)).scalars()
    tick_array = []

    # get all tickets from a lot in array form
    for row in tick_db:
        tick_array.append(row.tick)

    # check if there's any tickets left
    if len(tick_array) == 10000:
        flash("Ya no hay más boletas")
        return None

    # sort list
    tick_array.sort()

    # generates a random new_tick_num and searchs in
    # the array if it exists already
    new_tick_num = randint(0, 9999)
    while new_tick_num in tick_array:
        new_tick_num = randint(0, 9999)

    new_tick = Ticket(user_id=user.id, lot_id=lot_id, tick=new_tick_num)
    
    return new_tick


@auth.route('/consultar', methods=['GET', 'POST'])
def consultar():
    if request.method == 'POST':
        # query SELECT * FROM User, Ticket WHERE User.id == Ticket.user_id AND User.email == email 
        email = request.form.get('email')
        db_search = db.session.execute(db.select(Customer, Ticket).filter(Customer.id == Ticket.user_id).where(Customer.email==email))
        
        if not db_search:
            return render_template('check.html')
        else:
            return render_template('check.html', db_search=db_search)
        
    return render_template('check.html')


    # check if there's any tickets left
    if len(tick_array) == 10000:
        flash("Ya no hay más boletas")
        return None

    # sort list because why not
    tick_array.sort()

    # generates a random new_tick_num and searchs in
    # the array if it exists already
    new_tick_num = randint(0, 9999)
    while new_tick_num in tick_array:
        new_tick_num = randint(0, 9999)

    new_tick = Ticket(user_id=user.id, lot_id=lot_id, tick=new_tick_num)
    
    return new_tick


# writes contact info in data base db
def finish_payment(email, name, contact, lot_id):
    # database entries
    new_user = Customer(email=email, name=name, contact=contact)

    # user conf load
    db.session.add(new_user)
    
    for i in range(int(session['ticks'])):
        new_ticket = get_ticket(new_user, lot_id)
        db.session.add(new_ticket)

    # commit to db
    db.session.commit() 

    flash('Compra exitosa!', category='success')
    return redirect(url_for('views.home'))



## ------------
## PORTAL ADMIN
##-------------
##  HOW TO CREATE AN ADMIN ACCOUNT:
#   ---- DATABASE ----
#   new_admin = User(login="Login-name-here", passwd=generate_password_hash("password-here", method='pbkdf2:sha256'))
#   db.session.add(new_admin)
#   db.session.commit()


@auth.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
#    the example above goes here, maybe idk
    if request.method == 'POST':
        login = request.form.get('login')
        passwd = request.form.get('passwd')

        # authentication of admin login
        admin_db = db.session.execute(db.select(User).where(User.login==login)).scalar()
        print(admin_db.passwd)
        if admin_db:
            if check_password_hash(admin_db.passwd, passwd):
                flash('Welcome', category='success')
                login_user(admin_db, remember=True)
                return redirect(url_for('auth.admin'))
            else:
                flash('Error: credenciales incorrectas', category='error')
        else:
            flash('Error: el admin no existe', category='error')

    return render_template('admin-login.html')

# logout
@auth.route('/admin-logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('auth.admin_login'))

# admin view
@auth.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():

    if request.method == 'POST':
        # Crea un sorteo nuevo
        # makes new lottery
        lot = request.form.get('lot')
        t_price = request.form.get('t_price')
        new_lot = Lot(prize=lot, t_price=t_price)
        db.session.add(new_lot)
        db.session.commit()

    # query all data to display
    users = db.session.execute(db.select(Customer).order_by(Customer.id)).scalars()
    lots = db.session.execute(db.select(Lot).order_by(Lot.id)).scalars()
    tickets = db.session.execute(db.select(Ticket).order_by(Ticket.id)).scalars()
    tickets = db.session.execute(db.select(Ticket).order_by(Ticket.id)).scalars()
    admins = db.session.execute(db.select(User).order_by(User.id)).scalars()

    return render_template('admin.html', users=users, lots=lots, tickets=tickets, admins=admins)
    
