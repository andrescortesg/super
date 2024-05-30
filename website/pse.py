# this manages the PSE payment part

import mercadopago

from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from .auth import get_lot, finish_payment, check_tick
from requests import get

# bp creation
pse = Blueprint('pse', __name__)

# access key goes here
sdk = mercadopago.SDK("TEST")

# payment process with PSE starts here
@pse.route('/process_payment', methods=['GET', 'POST'])
def pse_payment():  
    lot_id = request.args.get('lot_id') # lot_id: lottery id
    p_lot = get_lot(lot_id)             # p_lot: lot 

    session['lot_id'] = lot_id          # saves lot_id for later

    # stops illegal access to pse
    if lot_id == None or p_lot == None:
        return redirect(url_for('views.home'))

    # check if there's tickets left
    if check_tick(lot_id) == False:
        return redirect(url_for('views.home'))

    flash('Va a comprar: ' + p_lot['prize'] + ' -- Precios: 2 x $' + str(p_lot['t_price'] * 2) + ' -- 5 x  $' + str(p_lot['t_price'] * 5) + ' -- 10 x $' + str(p_lot['t_price'] * 10) + ' -- 20 x $' + str(p_lot['t_price'] * 20), category="message")

    # when POST -> collects data
    if request.method == 'POST':
        ticks = request.form.get('options')     # amount of tickets
        f_price = p_lot['t_price'] * int(ticks) # final price for the thing
        payment = pse_payment_form(p_lot['prize'], f_price)

        session['ticks'] = ticks
        # checks if final price f_price is greater or equal than 1000
        # 1000 -- lower limit
        
        if f_price <= 1000:
            flash('El precio minimo de pago es $1000.', category='error')
            return redirect(url_for('views.home'))
            pass
        
        # true: error -- false: no error
        if pse_error_check(payment) != True:
            print('HERE')
            return redirect(payment.get('transaction_details').get('external_resource_url'))

    return render_template('pse_form.html')

# JSON of bank list and configuration stuff from the API
@pse.route('/payment_methods')
def pse_bank_list():
    payment_methods_response = sdk.payment_methods().list_all()
    payment_methods = payment_methods_response["response"]

    return payment_methods

# gets data from frontend to fill payment form, sends data to PSE and starts payment
# f_price: final price
# desc: description
def pse_payment_form(desc, f_price): 
    # if marked with x, then it's a required field
    ip = get('https://api.ipify.org').content.decode('utf8')

    # gets special data and saves for later 
    email = request.form.get("email")
    name = request.form.get('name')
    contact = request.form.get("phoneNumber") 

    session['email'] = email
    session['name'] = name
    session['contact'] = contact

    payment_data = {
        "transaction_amount": f_price, # value of purchase
        "description": desc,
        "payment_method_id": "pse",
        "additional_info": {
            "ip_address": "0.0.0.0" #X fuck you
        },
        "transaction_details": {
            "financial_institution": request.form.get("financialInstitution") #x
        },
        "callback_url": 'http://' + ip + ':5000', #x
        "payer": {
            "email": email, #x
            "entity_type": "individual", 
            "identification": { #xx
                "type": request.form.get("identificationType"), #x
                "number": request.form.get("identificationNumber") #x
            },

            # LEGACY CODE: other data fields
            #"address": {
            #   "zip_code": request.form.get("zipCode"), #x
            #   "street_name": request.form.get("streetName"), #x
            #   "street_number": request.form.get("streetNumber"), #x
            #   "neighborhood": request.form.get("neighborhood"), #x
            #   "city": request.form.get("city"), #x
            #   },
            #"phone": {
            #    "area_code": request.form.get("phoneAreaCode"), #x
            #    "number": request.form.get("phoneNumber") #x
            #}

        }
    }

    # email, name, contact, lot_id
    payment_response = sdk.payment().create(payment_data)
    payment = payment_response["response"]
   
    return payment

# checks for various error in data, gets info from transaction
#if true error, else false
def pse_error_check(payment):
    flag = True
    match str(payment['status']):
        case'205':
            flash('Ingresa el número de tu tarjeta.', category="error")
        case '208': 
            flash('Elige un mes.', category='error')
        case '209':
            flash('Elige un año.', category='error')
        case '212':
            flash('Ingresa tu tipo de documento.', category='error')
        case '213':
            flash('Ingresa tu documento.', category='error')
        case '214':
            flash('Ingresa tu documento.', category='error')
        case '220':
            flash('Ingresa tu banco.', category='error')
        case '221':
            flash('Ingresa el nombre y apellido.', category='error')
        case '224':
            flash('Ingresa el código de seguridad.', category='error')
        case 'E203':
            flash('Revisa el código de seguridad.', category='error')
        case 'E301':
            flash('Ingresa un número de tarjeta válido.', category='error')
        case '316':
            flash('Ingresa un nombre válido.', category='error')
        case '322': 
            flash('El tipo de documento es inválido.', category='error')
        case '323':
            flash('Revisa tu documento.', category='error')
        case '324':
            flash('El documento es inválido.', category='error')
        case '325':
            flash('El mes es inválido.', category='error')
        case '326':
            flash('El año es inválido.', category='error')
        case '400':
            if payment['error'] == 'bad_request':
                print("-- SYSTEM ERROR: " + payment['error'])
                print(payment)
            elif payment['message'] == 'payer.email must be a valid email':
                flash('Ha ingresado un correo no valido.')
            else:
                flash('El monto de la transacción excede los límites establecidos en PSE para la empresa.', category='error')
        case '500':
            flash('500: No se pudo crear la transacción. Por favor, intente más tarde.', category='error')
        case _:
            flag = False
    
    return flag

# check for the response
#if true approved, else rejected/in wait
def pse_response_check(payment):
    if payment['response']['status'] != 'approved':
        match payment['response']['status_detail']:
            case 'pending_contingency':
                flash('Estamos procesando tu pago. No te preocupes, menos de 2 días hábiles te avisaremos por e-mail si se acreditó.')
            case 'pending_review_manual': 
                flash('Estamos procesando tu pago. No te preocupes, menos de 2 días hábiles te avisaremos por e-mail si se acreditó o si necesitamos más información.')
            case 'cc_rejected_bad_filled_card_number':
                flash('Revisa el número de tarjeta.', category='error')
            case 'cc_rejected_bad_filled_date':
                flash('Revisa la fecha de vencimiento.', category='error')
            case 'cc_rejected_bad_filled_other':
                flash('Revisa los datos.', category='error')
            case 'cc_rejected_bad_filled_security_code':
                flash('Revisa el código de seguridad de la tarjeta.', category='error')
            case 'cc_rejected_blacklist':
                flash('No pudimos procesar tu pago.', category='error')
            case 'cc_rejected_call_for_authorize':
                flash('Debes autorizar ante ' + payment['response']['payment_method_id'] + ' el pago de ' + payment['response']['fee_details']['amount'] +'.', category='error')
            case 'c_rejected_card_disabled':
                flash('Llama a ' + payment['response']['payment_method_id'] + ' para activar tu tarjeta o usa otro medio de pago. El teléfono está al dorso de tu tarjeta.', category='error')
            case 'cc_rejected_card_error':
                flash('No pudimos procesar tu pago.', category='error')
            case 'cc_rejected_duplicated_payment':
                flash('Ya hiciste un pago por ese valor. Si necesitas volver a pagar usa otra tarjeta u otro medio de pago.', category='error')
            case 'cc_rejected_high_risk':
                flash('Tu pago fue rechazado. Elige otro de los medios de pago, te recomendamos con medios en efectivo.', category='error')
            case 'cc_rejected_insufficient_amount':
                flash('Tu ' + payment['response']['payment_method_id'] + ' no tiene fondos suficientes.', category='error')
            case 'cc_rejected_invalid_installments':
                flash(payment['response']['payment_method_id'] + ' no procesa pagos en ' + payment['response']['installments'] + ' cuotas.', category='error')
            case 'cc_rejected_max_attempts':
                flash('Llegaste al límite de intentos permitidos. Elige otra tarjeta u otro medio de pago.', category='error')
            case 'cc_rejected_other_reason':
                flash(payment['response']['payment_method_id'] + ' no procesó el pago.', category='error')
        return False
    else:
        return True

# finishes payment validation from pse
def pse_finish_payment(pay_id):
    payment = sdk.payment().get(pay_id)     # get payment status

    if pse_response_check(payment) == True:
        finish_payment(session['email'], session['name'], session['contact'], session['lot_id'])


