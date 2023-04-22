from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'employee'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique = True, nullable = False)
    password = db.Column(db.String(20), nullable = False)
    firstname = db.Column(db.String(50), nullable = False)
    lastname = db.Column(db.String(50), nullable = False)
    email = db.Column(db.String(120), nullable = False)
    position = db.Column(db.String(120), nullable = False)
    date_insert = db.Column(db.DateTime(), default = datetime.datetime.now(), nullable = False)
    date_update = db.Column(db.DateTime(), default = datetime.datetime.now(), nullable = False)
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def check_password(self, password):
        return self.password == password
    