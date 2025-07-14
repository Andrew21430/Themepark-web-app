from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo




class RideSearchForm(FlaskForm):
    search = StringField("Search Rides", validators=[DataRequired()])
    submit = SubmitField("Search")


class ParkSearchForm(FlaskForm):
    search = StringField("Search Rides", validators=[DataRequired()])
    submit = SubmitField("Search")



class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    confirm  = PasswordField("Confirm",  validators=[DataRequired(), EqualTo('password')])
    submit   = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit   = SubmitField("Login")