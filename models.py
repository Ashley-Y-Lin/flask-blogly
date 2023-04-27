from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

DEFAULT_IMAGE_URL = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"


def connect_db(app):
    """Connect to database."""

    app.app_context().push()
    db.app = app
    db.init_app(app)


"""Models for Blogly."""


class User(db.Model):
    """User."""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    first_name = db.Column(db.String(50), nullable=False)

    last_name = db.Column(db.String(50), nullable=False)

    image_url = db.Column(
        db.Text,
        nullable=False,
        default=DEFAULT_IMAGE_URL,
    )


class Post(db.Model):
    """Post."""

    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.String(100), nullable=False)

    content = db.Column(db.Text, nullable=False)

    # TODO: does this work?
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=db.func.now())

    author_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)

    author = db.relationship('User', backref='posts')

    tags = db.relationship(
        'Tag', secondary='post_tags', backref='posts')


class Tag(db.Model):
    """Tag."""

    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(50), nullable=False, unique=True)


class PostTag(db.Model):
    """PostTag."""

    __tablename__ = "post_tags"

    post_id = db.Column(db.Integer, db.ForeignKey(
        'posts.id'), primary_key=True, nullable=False)

    tag_id = db.Column(db.Integer, db.ForeignKey(
        'tags.id'), primary_key=True, nullable=False)
