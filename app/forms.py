from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, StringField, SubmitField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, NumberRange, Optional
from app.models import Ride, Park, RideType, Layout, Theme, LaunchType, Restriction, Constructor  # adjust imports
from flask_wtf.file import FileField, FileAllowed


class RideSearchForm(FlaskForm):
    search = StringField("Search Rides", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Search")


class ParkSearchForm(FlaskForm):
    search = StringField("Search Parks", validators=[DataRequired(), Length(max=100)])
    submit = SubmitField("Search")


class RegisterForm(FlaskForm):
    # This form is used for user registration
    # It includes fields for username, password, and confirmation
    # and uses validators to ensure the inputs are valid
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    confirm = PasswordField("Confirm",  validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField("Login")


class ReviewForm(FlaskForm):
    content = TextAreaField("Your Review", validators=[DataRequired(), Length(max=1000)])
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
    name = StringField("Park Name", validators=[DataRequired(), Length(max=150)])
    location = StringField("Location", validators=[DataRequired(), Length(max=150)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=2000)])
    photo = FileField('Photo', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField("Add Park")


class RideForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=150)])
    ride_type_id = SelectField('Ride Type', coerce=int, validators=[DataRequired()])
    layout_id = SelectField('Layout', coerce=int, validators=[DataRequired()])
    theme_id = SelectField('Theme', coerce=int, validators=[DataRequired()])
    launch_type_id = SelectField('Launch Type', coerce=int, validators=[DataRequired()])
    park_id = SelectField('Park', coerce=int, validators=[DataRequired()])
    restriction_id = SelectField('Restriction', coerce=int, validators=[DataRequired()])
    constructor_id = SelectField('Constructor', coerce=int, validators=[DataRequired()])

    thrill_level = StringField('Thrill Level', validators=[DataRequired(), Length(max=50)])
    photo = FileField('Photo', validators=[Optional(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    Height = IntegerField('Height (m)', validators=[Optional(), NumberRange(min=0, max=250)])
    submit = SubmitField('Save')

    def __init__(self, *args, **kwargs):
        super(RideForm, self).__init__(*args, **kwargs)
        # Populate dropdown choices dynamically from DB
        self.ride_type_id.choices = [(r.id, r.ride) for r in RideType.query.all()]
        self.layout_id.choices = [(k.id, k.description) for k in Layout.query.all()]
        self.theme_id.choices = [(t.id, t.name) for t in Theme.query.all()]
        self.launch_type_id.choices = [(lt.id, lt.name) for lt in LaunchType.query.all()]
        self.park_id.choices = [(p.id, p.name) for p in Park.query.all()]
        self.restriction_id.choices = [(res.id, res.reason) for res in Restriction.query.all()]
        self.constructor_id.choices = [(c.id, c.name) for c in Constructor.query.all()]

class DummyForm(FlaskForm):
    pass

class ReviewSearchForm(FlaskForm):
    search = StringField("Text", validators=[Optional(), Length(max=100)])
    ride_id = SelectField("Ride", coerce=int, validators=[Optional()])
    park_id = SelectField("Park", coerce=int, validators=[Optional()])
    username = StringField("User", validators=[Optional(), Length(max=80)])
    submit = SubmitField("Search")

    def set_choices(self):
        from app.models import Ride, Park
        self.ride_id.choices = [(-1, "All")] + [(r.id, r.name) for r in Ride.query.order_by(Ride.name).all()]
        self.park_id.choices = [(-1, "All")] + [(p.id, p.name) for p in Park.query.order_by(Park.name).all()]