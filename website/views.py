from flask import Blueprint, render_template, request, session, redirect
from flask_login import login_required, current_user
from .pse import pse_finish_payment

views = Blueprint('views', __name__)

# TODO: transferir lot_number para hacer compra
@views.route('/')
def home():
    # this part gets the lot to be purchased
    lot_id = request.args.get('lot_id', None)

    # payment id: this is when you already made a purchase
    pay_id = request.args.get('payment_id')
    
    if pay_id != None:          # finish the payment by writing the tickets to db IN
        pse_finish_payment(pay_id)

    return render_template('home.html')
