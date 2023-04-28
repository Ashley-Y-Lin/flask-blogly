"""Blogly application."""

import os

from flask import Flask, redirect, render_template, request, flash
from models import db, connect_db, User, Post, Tag, PostTag, DEFAULT_IMAGE_URL

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

    first_name = request.form["first_name"]
    last_name = request.form["last_name"]

    image_url = request.form["image_url"] or None

    user = User(first_name=first_name, last_name=last_name, image_url=image_url)

    db.session.add(user)
    db.session.commit()

    flash(f"User '{user.first_name} {user.last_name}' was added.")

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

    user.first_name = request.form["first_name"]
    user.last_name = request.form["last_name"]

    user.image_url = request.form["image_url"] or DEFAULT_IMAGE_URL

    db.session.add(user)
    db.session.commit()

    return redirect(f"/users")


@app.post("/users/<int:user_id>/delete")
def delete_user(user_id):
    """deletes a user by id"""

    user = User.query.get_or_404(user_id)

    Post.query.filter(Post.author_id == user.id).delete()

    db.session.delete(user)
    db.session.commit()

    flash(f"User '{user.first_name} {user.last_name}' was deleted.")

    return redirect("/users")


@app.get("/users/<int:user_id>/posts/new")
def display_add_post_form(user_id):
    """displays the form to add a new post authored by a given user"""

    user = User.query.get_or_404(user_id)

    tags = Tag.query.all()

    return render_template("new_post.html", user=user, tags=tags)


@app.post("/users/<int:user_id>/posts/new")
def add_new_post(user_id):
    """adds a new post authored by a given user
    and redirects to their user detail page"""

    user = User.query.get_or_404(user_id)

    title = request.form["title"]
    content = request.form["content"]
    tag_ids = request.form.getlist("tags")

    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
    post = Post(title=title, content=content, author_id=user.id, tags=tags)

    db.session.add(post)
    db.session.commit()

    flash("Post added!")

    return redirect(f"/users/{user.id}")


@app.get("/posts/<int:post_id>")
def display_post(post_id):
    """displays a post given its id"""

    post = Post.query.get_or_404(post_id)

    return render_template("view_post.html", post=post)


@app.get("/posts/<int:post_id>/edit")
def display_edit_post_form(post_id):
    """displays a form to edit a post given its id"""

    post = Post.query.get_or_404(post_id)

    tags = Tag.query.all()

    return render_template("edit_post.html", post=post, tags=tags)


@app.post("/posts/<int:post_id>/edit")
def edit_post(post_id):
    """updates the post with the given id
    and redirects to the view post page"""

    post = Post.query.get_or_404(post_id)

    post.title = request.form["title"]
    post.content = request.form["content"]

    tag_ids = request.form.getlist("tags")
    post.tags = [Tag.query.get(id) for id in tag_ids]

    db.session.add(post)
    db.session.commit()

    flash("Post updated!")

    return redirect(f"/posts/{post.id}")


@app.post("/posts/<int:post_id>/delete")
def delete_post(post_id):
    """deletes the post with id post_id
    and redirects to the poster's user detail page"""

    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()

    flash("Post deleted!")

    return redirect(f"/users/{post.author_id}")


@app.get("/tags")
def display_all_tags():
    """displays all existing tags"""

    tags = Tag.query.all()

    return render_template("view_tags.html", tags=tags)


@app.get("/tags/<int:tag_id>")
def display_tag_info(tag_id):
    """returns the tag info page for a given tag by id"""

    tag = Tag.query.get_or_404(tag_id)

    return render_template("tag_detail.html", tag=tag)


@app.get("/tags/new")
def display_add_tag_form():
    """displays the form to add a new tag"""

    return render_template("new_tag.html")


@app.post("/tags/new")
def add_new_tag():
    """adds a new tag and redirects to the tag list page"""

    name = request.form["tag_name"]

    tag = Tag(name=name)
    db.session.add(tag)
    db.session.commit()

    flash("Tag added!")

    return redirect(f"/tags")


@app.get("/tags/<int:tag_id>/edit")
def display_edit_tag_form(tag_id):
    """displays a form to edit a tag given its id"""

    tag = Tag.query.get_or_404(tag_id)

    return render_template("edit_tag.html", tag=tag)


@app.post("/tags/<int:tag_id>/edit")
def edit_tag(tag_id):
    """updates the tag with the given id
    and redirects to the tag list page"""

    tag = Tag.query.get_or_404(tag_id)

    tag.name = request.form["tag_name"]

    db.session.add(tag)
    db.session.commit()

    flash("Tag updated!")

    return redirect(f"/tags")


@app.post("/tags/<int:tag_id>/delete")
def delete_tag(tag_id):
    """deletes a tag by id"""

    tag = Tag.query.get_or_404(tag_id)

    PostTag.query.filter(PostTag.tag_id == tag.id).delete()

    db.session.delete(tag)
    db.session.commit()

    flash(f"The tag '{tag.name}' was deleted.")

    return redirect("/tags")
