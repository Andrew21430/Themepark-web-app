from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange, Optional
from app.models import Ride, Park




class RideSearchForm(FlaskForm):
    search = StringField("Search Rides", validators=[DataRequired()])
    submit = SubmitField("Search")


class ParkSearchForm(FlaskForm):
    search = StringField("Search Parks", validators=[DataRequired()])
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



class ReviewForm(FlaskForm):
    content = TextAreaField("Your Review", validators=[DataRequired()])
    rating = IntegerField("Rating (1–5)", validators=[
        DataRequired(),
        NumberRange(min=1, max=5, message="Rating must be between 1 and 5")
    ])

    # Optional dropdown to associate review with either a Ride or a Park
    ride_id = SelectField("Ride", coerce=int, validators=[Optional()])
    park_id = SelectField("Park", coerce=int, validators=[Optional()])

    submit = SubmitField("Submit Review")

    def set_choices(self):
        self.ride_id.choices = [(0, "--- None ---")] + [
            (ride.id, ride.name) for ride in Ride.query.order_by(Ride.name).all()
        ]
        self.park_id.choices = [(0, "--- None ---")] + [
            (park.id, park.name) for park in Park.query.order_by(Park.name).all()
        ]



class ParkForm(FlaskForm):
    name = StringField("Park Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    submit = SubmitField("Add Park")

class RideForm(FlaskForm):
    name = StringField("Ride Name", validators=[DataRequired()])
    thrill_level = StringField("Thrill level (Low - Extreme)", validators=[DataRequired()])
    park_id = IntegerField("Park ID", validators=[DataRequired()])
    submit = SubmitField("Add Ride")