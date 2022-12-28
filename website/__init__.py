from flask import Flask, render_template,request, Blueprint, redirect, url_for, session, flash
import logging 
import sys
import click
import random
import string


def get_app():
    class RemoveColorFilter(logging.Filter):
        def filter(self, record):
            if record and record.msg and isinstance(record.msg, str):
                record.msg = click.unstyle(record.msg) 
            return True

    remove_color_filter = RemoveColorFilter()
    app = Flask(__name__,template_folder='templates')
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = "92b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf"

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler('error.txt',encoding="utf8")
    file_handler.addFilter(remove_color_filter)
    file_handler.setLevel(logging.DEBUG)

    streamhandler = logging.StreamHandler(sys.stdout)

    logger.addHandler(file_handler)
    logger.addHandler(streamhandler)
    app.register_blueprint(view,url_prefix='/')

    return app

view = Blueprint('view',__name__)

@view.route('/home')
def home():
    return render_template('home.html')

@view.route('/info', methods=['GET', 'POST'])
def info():
    email = request.form.get('email')
    username =request.form.get('username')
    first_name = request.form.get('first name')
    last_name = request.form.get('last name')
    age = request.form.get('age')
    phone = request.form.get('phone')
    item = request.form.get('product')
    invoice = 'W'
    for i in range(10):
        invoice += random.choice(string.digits)
    real_invoice = str(invoice)

    session['invoice'] = real_invoice
    if request.method == 'POST':
        if len(username) <= 6:
            flash('Your username is too short')
        elif len(username) >= 30:
            flash('Your username is too long')
        else:
            return redirect(url_for('view.confirm'))

    elif request.method == 'GET':
        return render_template('personinfo.html')
        
    return render_template('personinfo.html')

@view.route('/confirm')
def confirm():
    real_invoice = session.get('invoice',None)
    return render_template('confirm.html',text=real_invoice)