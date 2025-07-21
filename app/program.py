from app import app
from flask import render_template, abort, request, redirect, url_for, flash, session, g
from flask_sqlalchemy import SQLAlchemy  # no more boring old SQL for us!
# from sqlalchemy.orm import joinedload
from collections import defaultdict
from app.forms import RideSearchForm, ParkSearchForm, RegisterForm, LoginForm
from functools import wraps
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash


import os


basedir = os.path.abspath(os.path.dirname(__file__))
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "database.db")
db.init_app(app)

import app.models as models
from app.models import User 


# basic route
@app.route('/')
def root():
    return render_template('home.html', page_title='HOME')


@app.route('/park', methods=['GET', 'POST'])
def park():
    form = ParkSearchForm()
    parks = []
    if form.validate_on_submit():
        search_term = form.search.data
        parks = models.Park.query.filter(models.Park.name.ilike(f"%{search_term}%")).all()
    else:
        parks = models.Park.query.all()
    return render_template('park.html', page_title='PARKS', parks=parks, form=form)


@app.route('/ride', methods=['GET', 'POST'])
def ride():
    form = RideSearchForm()
    rides = []
    if form.validate_on_submit():
        search_term = form.search.data
        rides = models.Ride.query.filter(models.Ride.name.ilike(f"%{search_term}%")).all()
    else:
        rides = models.Ride.query.join(models.Layout).order_by(models.Ride.height.desc()).all()
    return render_template('ride.html', page_title='RIDES', rides=rides, form=form)


@app.route('/ride/<int:id>')
def rideid(id):
    form = RideSearchForm()
    rides = []
    rides = models.Ride.query.join(models.Layout).order_by(models.Ride.height.desc()).filter(models.Ride.id == id).first_or_404()
    return render_template('ride.html', page_title='RIDES', rides=[rides], form=form)


@app.route('/manufactuer')
def manufactuer():
    manufactuers = models.Manufacturer.query.all()
    return render_template('manufactuer.html', page_title='MANUFACTUER', manufactuers=manufactuers)


@app.route('/rideelements')
def rideelements():
    elements = models.RideElement.query.all()
    return render_template('rideelement.html', page_title='RIDEELEMENTS', elements=elements)


@app.route('/ridetype')
def ridetype():
    # types = models.RideType.query.options(db.joinedload(models.RideType.manufacturers)).all()
    # joinedload is used to join many to many tables
    types = models.RideType.query.join(models.Manufacturer).all()
    return render_template('ridetype.html', page_title='RIDETYPES', types=types)


@app.route('/add', methods=['GET', 'POST'])
def add():
    print(request.args.get('ROR2'))
    return "Done"
    # return render_template('add.html', page_title = 'ADD')


@app.route('/parkrides')
def parkrides():
    # order and join of a many to many without using joined loaded as otherwise I would have to change all of my models tables
    results = db.session.query(models.Park, models.Ride).join(models.ParkRide, models.Park.id == models.ParkRide.c.park_id).join(models.Ride, models.Ride.id == models.ParkRide.c.ride_id).order_by(models.Park.name).all()
    # make it so that the parks only show once for all the rides
    grouped_parks = defaultdict(list)
    for park, ride in results:
        grouped_parks[park].append(ride)
    return render_template('parkrides.html', page_title='PARKRIDES', grouped_parks=grouped_parks)


app.config['SECRET_KEY'] = 'yoursecretkeyhere'



def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped

# make current user available in templates
@app.before_request
def load_logged_in_user():
    g.user = None
    if "user_id" in session:
        g.user = User.query.get(session["user_id"])




@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
            flash("Account created – please log in.", "success")
            return redirect(url_for("login"))
        except IntegrityError:
            db.session.rollback()
            flash("Username already taken.", "danger")
    return render_template("register.html", form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            session["user_id"] = user.id
            session["username"] = user.username
            flash(f"Welcome, {user.username}!", "success")
            return redirect(url_for("root"))
        else:
            flash("Invalid username or password. Please try again.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html", form=form, page_title="Login")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("root"))



@app.route("/secret")
@login_required
def secret():
    return f"Hello {g.user.username}, this is top‑secret!"

