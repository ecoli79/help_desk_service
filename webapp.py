import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm, Databoard_searchform
from models import User
from configparser import ConfigParser
# local module
import config
import db_working


db_data_for_connect = config.get_config_data('postgresql')

app = Flask(__name__)
app.secret_key = "secret key" # используется для защиты сессий пользователей
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_data_for_connect.get("user")}:{db_data_for_connect.get("password")}@{db_data_for_connect.get("host")}/{db_data_for_connect.get("database")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
            
        login_user(user, remember=form.remember.data)
        return redirect(url_for('dashboard'))
    
    return render_template('login.html', form = form)        


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data,
                    password = form.password.data,
                    firstname = form.firstname.data,
                    lastname = form.lastname.data,
                    email = form.email.data,
                    position = form.position.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    else:
        print(form.errors)

    return render_template('register.html', form=form)


@app.route('/dashboard', methods=['POST', 'GET'])
@login_required
def dashboard():

    types_ticket = db_working.get_ticket_types()

    form = ''
    type_ticket = ''
    is_done = ''

    if request.method == 'POST':
        form = request.form
        if 'types_ticket' in form:
            type_ticket = form['types_ticket']
            session['type_ticket'] = type_ticket
        if 'done_tickets' in form:
            is_done = form['done_tickets']
            session['done_tickets'] = 'checked'
        else:
            session['done_tickets'] = ''
        
    
    tickets = db_working.get_tickets(ticket_type_name = type_ticket, is_done = is_done)
    #types_ticket.insert(0,('',))
    return render_template('dashboard.html', types_ticket = types_ticket, 
                           tickets = tickets, form = form, selected_val = type_ticket)


@app.route('/ticketditails/<ticket_id>', methods=['POST', 'GET'])
def tickeditails(ticket_id):
    
    ticket = db_working.get_ticket(ticket_id)
   
    img_path = ticket[0][15]
    form = request.form
    
    if request.method == "POST":
        ticket_close = False
        employee_id = current_user.id
        ticket_response = form['ticket_response']
        ticket_note = form['ticket_note']
        if form.get('is_done') == 'on':
            ticket_close = True
        
        db_working.update_ticket(ticket_id = ticket_id,
                                 employee_id = employee_id,
                                 text_response = ticket_response,
                                 note = ticket_note,
                                 is_done = ticket_close)
        
        type_ticket = session.get('type_ticket')
        is_done = False
        if session.get('done_tickets'):
            is_done = session.get('done_tickets')
        types_ticket = db_working.get_ticket_types()
        tickets = db_working.get_tickets(ticket_type_name = type_ticket, is_done = is_done)  
        return render_template('dashboard.html', types_ticket = types_ticket, selected_val = type_ticket, tickets = tickets)
    else:        
        return render_template('ticketditails.html', ticket = ticket, form = form, img_path = img_path)
   

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/work/<ticket_id>', methods=['POST', 'GET'])
def get_ticket_work(ticket_id):
    
    if request.method == "POST":
        employee_id = current_user.id
        is_work = True
        db_working.ticket_in_work(ticket_id=ticket_id,
                                      emploeey_id=employee_id,
                                      is_work=is_work)

        
    return redirect(f'/ticketditails/{ticket_id}') #, ticket_id=ticket_id))
    
    # if request.method == "POST":
    #     employee_id = current_user.id
    #     is_work = True
    #     db_working.ticket_in_work(ticket_id = ticket_id,
    #                             emploeey_id = employee_id,
    #                             is_work = is_work)
    
    # return redirect(url_for('tickeditails', ticket_id = ticket_id))


if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', debug=True)