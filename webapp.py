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
    is_done = False
    start_date = ''
    end_date = ''

    if request.method == 'POST':
        form = request.form
        session['is_done'] =  bool(form.get('is_done'))
        
        if 'types_ticket' in form:
            type_ticket = form['types_ticket']
            session['type_ticket'] = type_ticket
        # if 'is_done' in form:
        #     is_done = form['is_done']
        #     session['is_done'] = is_done
        if 'start_date' in form:
            start_date = form['start_date']
            session['start_date'] = start_date
        if 'end_date' in form:
            end_date = form['end_date']
            session['end_date'] = end_date
        else:
            session['is_done'] = ''
            
    is_done = session.get('is_done')
    
    tickets = db_working.get_tickets(ticket_type_name = type_ticket, is_done = is_done, start_date = start_date, end_date = end_date )
    count_tickets = len(tickets)
    return render_template('dashboard.html', types_ticket = types_ticket, 
                           tickets = tickets, form = form, selected_val = type_ticket, count_tickets = count_tickets)


@app.route('/ticketditails/<ticket_id>', methods=['POST', 'GET'])
def tickeditails(ticket_id):
    
    ticket = db_working.get_ticket(ticket_id)
   
    img_path = ticket[0][14]
    form = request.form
    
    if request.method == "POST":
        is_done = False
        employee_id = current_user.id
        ticket_response = form['ticket_response']
        ticket_note = form['ticket_note']
        if form['is_done'] == 'on':
            is_done  = True
        db_working.update_ticket(ticket_id = ticket_id,
                                 employee_id = employee_id,
                                 text_response = ticket_response,
                                 note = ticket_note,
                                 is_done = is_done)
        
        type_ticket = session.get('type_ticket')
        is_done =session.get('is_done')
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

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', debug=True)