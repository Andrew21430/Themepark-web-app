from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

app = Flask(__name__)

app.config['SECRET_KEY'] = 'dev'

csrf = CSRFProtect(app)

from app import program, models

app.run(debug=True)
