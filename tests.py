import os

os.environ["DATABASE_URL"] = "postgresql:///blogly_test"

from unittest import TestCase

from app import app, db
from models import User, DEFAULT_IMAGE_URL

# Make Flask errors be real errors, rather than HTML pages with error info
app.config["TESTING"] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config["DEBUG_TB_HOSTS"] = ["dont-show-debug-toolbar"]

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        # As you add more models later in the exercise, you'll want to delete
        # all of their records before each test just as we're doing with the
        # User model below.
        User.query.delete()

        self.client = app.test_client()

        test_user = User(
            first_name="test1_first",
            last_name="test1_last",
            image_url=None,
        )

        db.session.add(test_user)
        db.session.commit()

        # We can hold onto our test_user's id by attaching it to self (which is
        # accessible throughout this test class). This way, we'll be able to
        # rely on this user in our tests without needing to know the numeric
        # value of their id, since it will change each time our tests are run.
        self.user_id = test_user.id

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_display_users_list(self):
        """Test HTML for /users is displayed, and includes the name
        of a user in the database."""
        with self.client as c:
            resp = c.get("/users")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("test1_first", html)
            self.assertIn("test1_last", html)

    def test_display_new_user_form(self):
        """Test correct HTML is displayed for the form to add a user,
        and that the HTTP status code is 200."""
        with self.client as c:
            resp = c.get("/users/new")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<form id="submit-new-user"', html)

    def test_add_new_user(self):
        """Test adding a new user. Make sure it redirects to /users."""
        with self.client as c:
            resp = c.post(
                "/users/new",
                data={
                    "first_name": "Ashley",
                    "last_name": "Lin",
                    "image_url": "",
                },
                follow_redirects=False,
            )

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "/users")

    def test_add_new_user_redirection(self):
        """Test that after adding a new user, it successfully displays the
        newly added user on the screen."""
        with self.client as c:
            resp = c.post(
                "/users/new",
                data={
                    "first_name": "Ashley",
                    "last_name": "Lin",
                    "image_url": "",
                },
                follow_redirects=True,
            )

            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f"Ashley Lin", html)
            self.assertIn("was added", html)

    def test_valid_display_user_info(self):
        """Test that the user detail page is correctly displayed depending on the
        user id, when a valid user id is submitted."""
        with self.client as c:
            resp = c.get(f"/users/{self.user_id}")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn(f"<!-- this is the {self.user_id} user_detail page -->", html)
            self.assertIn(DEFAULT_IMAGE_URL, html)

    def test_invalid_display_user_info(self):
        """Test that when an invalid user id is submitted to the user detail page,
        it redirects to a 404 error."""
        with self.client as c:
            resp = c.get(f"/users/0")
            self.assertEqual(resp.status_code, 404)

    def test_display_edit_user_form(self):
        """Test that the page for a user with a valid user id to edit their
        profile is displayed."""
        with self.client as c:
            resp = c.get(f"/users/{self.user_id}/edit")
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn(f"<!-- this is the {self.user_id} edit user page -->", html)

    def test_delete_user_no_posts(self):
        """Test deleting a user who doesn't have any posts.
        Make sure it redirects to the user list page."""
        with self.client as c:
            resp = c.post(
                f"/users/{self.user_id}/delete",
                follow_redirects=False,
            )

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "/users")

    def test_delete_user_no_posts_redirection(self):
        """Test that after deleting a user who doesn't have any posts,
        the user is successfully removed from the user list."""
        with self.client as c:
            resp = c.post(
                f"/users/{self.user_id}/delete",
                follow_redirects=True,
            )

            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(User.query.all(), [])
            self.assertIn("was deleted.", html)

    def test_delete_user_with_posts(self):
        """Test deleting a user who has some posts.
        Make sure it redirects to the user list page."""
        with self.client as c:
            # give user a post
            c.post(
                f"/users/{self.user_id}/posts/new",
                data={
                    "title": "A new post",
                    "content": "This is my post content",
                },
                follow_redirects=True,
            )

            resp = c.post(
                f"/users/{self.user_id}/delete",
                follow_redirects=False,
            )

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, "/users")

    def test_delete_user_with_posts_redirection(self):
        """Test that after deleting a user who has some posts,
        the user is successfully removed from the user list."""
        with self.client as c:
            # give the user a post
            c.post(
                f"/users/{self.user_id}/posts/new",
                data={
                    "title": "A new post",
                    "content": "This is my post content",
                },
                follow_redirects=True,
            )

            resp = c.post(
                f"/users/{self.user_id}/delete",
                follow_redirects=True,
            )

            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(User.query.all(), [])
            self.assertIn("was deleted.", html)
