from flask import Flask

app = Flask(__name__)

from app import program

app.run(debug=True)
