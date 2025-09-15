from app import app
from flask import render_template, abort, request, redirect, url_for, flash, session, g, Flask
# from flask_sqlalchemy import SQLAlchemy  # no more boring old SQL for us!
# from collections import defaultdict
from app.forms import RideSearchForm, ParkSearchForm, RegisterForm, LoginForm, ReviewForm, ParkForm, RideForm
from functools import wraps
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash
from flask_wtf import CSRFProtect
from app.models import db  # Import db directly from models.py
from wtforms.validators import ValidationError
from flask_wtf.csrf import validate_csrf
from werkzeug.utils import secure_filename


import app.models as models
from app.models import User, Park  # Ride
# Initialize Flask app and database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'

# Setup the database
import os
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, "database.db")
db.init_app(app)

csrf = CSRFProtect(app)

# Delay importing routes and models until after app is created
with app.app_context():
    from app import models  # this is now safe

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(__file__),
    'static',
    'Images',
    'website',
    'rides'
)

# Make sure the folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Configure Flask to use it
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# basic route
@app.route('/')
def root():
    return render_template('home.html', page_title='HOME')


@app.route('/park', methods=['GET', 'POST'])
def park():
    # Initialize the search form
    form = ParkSearchForm()
    parks = []
    # Check if the form is submitted and valid
    if form.validate_on_submit():
        search_term = form.search.data
        # Query the database for parks matching the search term
        parks = models.Park.query.filter(models.Park.name.ilike(f"%{search_term}%")).all()
    else:
        parks = models.Park.query.all()
    return render_template('park.html', page_title='PARKS', parks=parks, form=form)


@app.route('/park/<int:id>', methods=['GET', 'POST'])
def parkid(id):
    form = ParkSearchForm()
    parks = []
    if form.validate_on_submit():
        search_term = form.search.data
        parks = models.Park.query.filter(models.Park.name.ilike(f"%{search_term}%")).all()
    else:
        parks = models.Park.query.filter(models.Park.id == id).first_or_404()
    return render_template('park.html', page_title='PARKS', parks=[parks], form=form)


@app.route('/ride', methods=['GET', 'POST'])
def ride():
    form = RideSearchForm()
    rides = []
    if form.validate_on_submit():
        search_term = form.search.data
        rides = models.Ride.query.filter(models.Ride.name.ilike(f"%{search_term}%")).all()
    else:
        rides = models.Ride.query.join(models.Layout).order_by(models.Ride.Height.desc()).all()
    return render_template('ride.html', page_title='RIDES', rides=rides, form=form)


@app.route('/ride/<int:id>')
def rideid(id):
    form = RideSearchForm()
    rides = []
    rides = models.Ride.query.join(models.Layout).order_by(models.Ride.Height.desc()).filter(models.Ride.id == id).first_or_404()
    return render_template('ride.html', page_title='RIDES', rides=[rides], form=form)


@app.route('/manufactuer')
def manufactuer():
    # Query all manufacturers from the database
    manufactuers = models.Manufacturer.query.all()
    return render_template('manufactuer.html', page_title='MANUFACTUER', manufactuers=manufactuers)


@app.route('/rideelements')
def rideelements():
    elements = models.RideElement.query.all()
    return render_template('rideelement.html', page_title='RIDEELEMENTS', elements=elements)


@app.route('/ridetype')
def ridetype():
    # Query all ride types and join with manufacturers
    types = models.RideType.query.join(models.Manufacturer).all()
    return render_template('ridetype.html', page_title='RIDETYPES', types=types)


@app.route('/launchtype')
def launchtype():
    # Query all launch types
    launch_types = models.LaunchType.query.all()
    return render_template('launchtype.html', page_title='LAUNCHTYPES', launch_types=launch_types)


@app.route('/parkrides')
def parkrides():
    parks = models.Park.query.order_by(models.Park.name).all()
    # Dictionary of parks and their rides
    grouped_parks = {park: park.rides for park in parks}
    return render_template('parkrides.html', page_title='PARKRIDES', grouped_parks=grouped_parks)


app.config['SECRET_KEY'] = 'yoursecretkeyhere'


# Decorator to require login for certain views
def login_required(view_func):
    @wraps(view_func)
    # This decorator checks if the user is logged in before allowing access to the view
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            # User is not logged in, redirect to login page
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped


# make current user available in templates
@app.before_request
def load_logged_in_user():
    # This function runs before each request to set the current user in the global context
    g.user = None
    if "user_id" in session:
        g.user = User.query.get(session["user_id"])


@app.route("/register", methods=["GET", "POST"])
def register():
    # This route handles user registration
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if the username already exists
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            # Commit the new user to the database
            db.session.commit()
            flash("Account created – please log in.", "success")
            return redirect(url_for("login"))
        # Handle the case where the username is already taken
        except IntegrityError:
            # Rollback the session to avoid committing the error
            db.session.rollback()
            flash("Username already taken.", "danger")
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    # This route handles user login
    form = LoginForm()
    if form.validate_on_submit():
        # Check if the user exists and verify the password
        user = User.query.filter_by(username=form.username.data).first()

        if user and check_password_hash(user.password_hash, form.password.data):
            # User exists and password is correct, log them in
            session["user_id"] = user.id
            session["username"] = user.username
            flash(f"Welcome, {user.username}!", "success")
            return redirect(url_for("root"))
        else:
            # Invalid login attempt
            flash("Invalid username or password. Please try again.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html", form=form, page_title="Login")


@app.route("/logout")
def logout():
    # This route handles user logout
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("root"))


@app.route("/secret")
@login_required
def secret():
    return f"Hello {g.user.username}, this is top‑secret!"


@app.route('/reviews', methods=["GET", "POST"])
def review_page():
    # This route handles both displaying and submitting reviews
    # Check for CSRF token validation
    edit_id = request.args.get('edit_id', type=int)
    editing = False
    # If an edit_id is provided, we are editing an existing review
    park_id_from_query = request.args.get('park_id', type=int)
    ride_id_from_query = request.args.get('ride_id', type=int)

    form = ReviewForm()
    # Set choices for the form fields
    form.set_choices()
    # If park_id or ride_id is provided in the query string, set it in the form
    if park_id_from_query and not edit_id:
        form.park_id.data = park_id_from_query

    if ride_id_from_query and not edit_id:
        form.ride_id.data = ride_id_from_query
    # If edit_id is provided, we are editing an existing review
    if edit_id:
        review = models.Review.query.get_or_404(edit_id)
        # Check if the current user is the owner of the review
        if review.user_id != session.get('user_id'):
            abort(403)
        editing = True
        if request.method == "GET":
            # Populate the form with the existing review data
            form.content.data = review.content
            form.rating.data = review.rating
            form.ride_id.data = review.ride_id or 0  # Match 0 to "--- None ---"
            form.park_id.data = review.park_id or 0

    if form.validate_on_submit():
        # Handle form submission for both creating and editing reviews
        ride_id = form.ride_id.data if form.ride_id.data != 0 else None
        park_id = form.park_id.data if form.park_id.data != 0 else None

        if editing:
            # Update the existing review
            review.content = form.content.data
            review.rating = form.rating.data
            review.ride_id = ride_id
            review.park_id = park_id
            db.session.commit()
            flash("Review updated!", "success")
        else:
            # Create a new review
            new_review = models.Review(
                content=form.content.data,
                rating=form.rating.data,
                ride_id=ride_id,
                park_id=park_id,
                user_id=session.get("user_id")
            )
            db.session.add(new_review)
            db.session.commit()
            flash("Review submitted!", "success")
        return redirect(url_for("review_page"))

    reviews = models.Review.query.order_by(models.Review.timestamp.desc()).all()
    return render_template("review.html", form=form, reviews=reviews, editing=editing, page_title="Reviews")


@app.route('/reviews/delete/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    # This route handles deleting a review
    # Check for CSRF token validation
    try:
        validate_csrf(request.form.get('csrf_token'))
    except ValidationError:
        abort(400, description="Invalid CSRF token")
    # Get the review by ID
    review = models.Review.query.get_or_404(review_id)

    # Check if the current user is the owner of the review
    if review.user_id != session.get('user_id'):
        abort(403)
    # Delete the review
    db.session.delete(review)
    db.session.commit()
    flash("Review deleted!", "success")
    return redirect(url_for("review_page"))


@app.route("/addpark", methods=["GET", "POST"])
def add_park():
    form = ParkForm()
    if form.validate_on_submit():
        filename = None
        if form.photo.data:
            filename = secure_filename(form.photo.data.filename)
            park_folder = os.path.join(os.path.dirname(__file__), 'static', 'Images', 'website')
            os.makedirs(park_folder, exist_ok=True)
            form.photo.data.save(os.path.join(park_folder, filename))
        new_park = Park(
            name=form.name.data,
            location=form.location.data,
            photo=filename  # store just the filename!
        )
        db.session.add(new_park)
        db.session.commit()
        flash("Park added!", "success")
        return redirect(url_for("root"))
    return render_template("addpark.html", form=form)


@app.route('/park/edit/<int:id>', methods=['GET', 'POST'])
def edit_park(id):
    park = models.Park.query.filter(models.Park.id == id).first_or_404()
    form = ParkForm(obj=park)
    if form.validate_on_submit():
        form.populate_obj(park)
        db.session.commit()
        flash("Park updated!", "success")
        return redirect(url_for('parkid', id=park.id))
    return render_template('editpark.html', form=form, park=park)


@app.route('/park/delete/<int:id>', methods=['POST'])
def delete_park(id):
    park = models.Park.query.filter(models.Park.id == id).first_or_404()
    db.session.delete(park)
    db.session.commit()
    flash("Park deleted!", "success")
    return redirect(url_for('park'))


@app.route('/addride', methods=['GET', 'POST'])
def add_ride():
    form = RideForm()
    if form.validate_on_submit():
        # Create Ride without park_id
        new_ride = models.Ride(
            name=form.name.data,
            ride_type_id=form.ride_type_id.data,
            layout_id=form.layout_id.data,
            theme_id=form.theme_id.data,
            launch_type_id=form.launch_type_id.data,
            thrill_level=form.thrill_level.data,
            restriction_id=form.restriction_id.data,
            constructor_id=form.constructor_id.data,
            Height=form.Height.data
        )

        # Handle photo upload
        if form.photo.data:
            filename = secure_filename(form.photo.data.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.photo.data.save(filepath)
            new_ride.photo = f'Images/website/rides/{filename}'

        # Add the new ride to the DB first
        db.session.add(new_ride)
        db.session.commit()

        # Now associate the ride with the selected park
        selected_park = models.Park.query.get(form.park_id.data)
        if selected_park:
            new_ride.parks.append(selected_park)
            db.session.commit()

        flash("New ride added successfully!", "success")
        return redirect(url_for('ride'))

    return render_template('addride.html', form=form)


@app.route('/ride/edit/<int:id>', methods=['GET', 'POST'])
def edit_ride(id):
    ride = models.Ride.query.filter(models.Ride.id == id).first_or_404()
    form = RideForm(obj=ride)
    if form.validate_on_submit():
        form.populate_obj(ride)
        db.session.commit()
        flash("Ride updated!", "success")
        return redirect(url_for('rideid', id=ride.id))
    return render_template('editride.html', form=form, ride=ride)


@app.route('/ride/delete/<int:id>', methods=['POST'])
def delete_ride(id):
    ride = models.Ride.query.filter(models.Ride.id == id).first_or_404()
    db.session.delete(ride)
    db.session.commit()
    flash("Ride deleted!", "success")
    return redirect(url_for('ride'))


# error 404 page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404



if __name__ == "__main__":
    app.run(debug=True)
