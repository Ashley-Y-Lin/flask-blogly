"""Blogly application."""

import os

from flask import Flask, redirect, render_template, request, flash
from models import db, connect_db, User

app = Flask(__name__)

app.config["SECRET_KEY"] = "please-dont-tell!"
# app.config[“DEBUG_TB_INTERCEPT_REDIRECTS”] = [“dont-show-debug-toolbar”]
# debug = DebugToolbarExtension(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///blogly"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

connect_db(app)


@app.get("/")
def get_root():
    """root endpoint which redirects to /users"""

    return redirect("/users")


@app.get("/users")
def display_users_list():
    """returns a list of all users"""

    users = User.query.all()

    return render_template("user_listing.html", users=users)


@app.get("/users/new")
def display_new_user_form():
    """returns a form to add a new user"""

    return render_template("new_user.html")


@app.post("/users/new")
def add_new_user():
    """adds a new user with the details in the request body
    before redirecting to /users if the request was successful"""

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")

    # TODO: default profile image
    image_url = request.form.get("image_url") or None

    user = User(first_name=first_name, last_name=last_name, image_url=image_url)

    db.session.add(user)
    db.session.commit()

    return redirect("/users")


@app.get("/users/<int:user_id>")
def display_user_info(user_id):
    """returns the user info page for a given user by id"""

    user = User.query.get_or_404(user_id)

    return render_template("user_detail.html", user=user)


@app.get("/users/<int:user_id>/edit")
def display_edit_user_form(user_id):
    """returns the edit user page for a given user by id"""

    user = User.query.get_or_404(user_id)

    return render_template("edit_user.html", user=user)


@app.post("/users/<int:user_id>/edit")
def edit_user(user_id):
    """updates info for user with id user_id with the data from the form
    and redirects to /users if successful"""

    user = User.query.get_or_404(user_id)

    user.first_name = request.form.get("first_name")
    user.last_name = request.form.get("last_name")

    # TODO: default profile image
    user.image_url = request.form.get("image_url", "")

    db.session.add(user)
    db.session.commit()

    return redirect(f"/users")


@app.post("/users/<int:user_id>/delete")
def delete_user(user_id):
    """deletes a user by id"""

    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    flash(f"User '{user.first_name} {user.last_name}' was deleted.")

    return redirect("/users")
