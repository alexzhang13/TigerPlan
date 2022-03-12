from flask import render_template, flash, redirect, url_for

from app import app

@app.route("/", methods=["GET", "POST"])
def index():
    categories = [{'dep: COS'},
    {'dep:ORF'}]
    return render_template("index.html", title='TigerPlan', categories=categories)

# TODO: Add login page
@app.route("/login")
def login():
    # form = LoginForm()
    return render_template("index.html", title='Log In')