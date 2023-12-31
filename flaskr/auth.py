import functools

from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash,generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# This creates a Blueprint named 'auth'. Like the application object, the blueprint needs to know where it’s defined, so __name__ is passed as the second argument. The url_prefix will be prepended to all the URLs associated with the blueprint.

# 1. register view
@bp.route('/register',methods=('GET','POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None


        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username,password) VALUES (?,?)",
                    (username,generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                # An sqlite3.IntegrityError will occur if the username already exists
                error = f"User {username} is already registered."
        
            else:
                return redirect(url_for("auth.login"))
        
        flash(error)
        # flash() stores messages that can be retrieved when rendering the template.

    return render_template('auth/register.html')

'''
Here’s what the register view function is doing:

@bp.route associates the URL /register with the register view function. When Flask receives a request to /auth/register, it will call the register view and use the return value as the response.

If the user submitted the form, request.method will be 'POST'. In this case, start validating the input.

request.form is a special type of dict mapping submitted form keys and values. The user will input their username and password.

Validate that username and password are not empty.

If validation succeeds, insert the new user data into the database.

db.execute takes a SQL query with ? placeholders for any user input, and a tuple of values to replace the placeholders with. The database library will take care of escaping the values so you are not vulnerable to a SQL injection attack.

For security, passwords should never be stored in the database directly. Instead, generate_password_hash() is used to securely hash the password, and that hash is stored. Since this query modifies data, db.commit() needs to be called afterwards to save the changes.

An sqlite3.IntegrityError will occur if the username already exists, which should be shown to the user as another validation error.

After storing the user, they are redirected to the login page. url_for() generates the URL for the login view based on its name. This is preferable to writing the URL directly as it allows you to change the URL later without changing all code that links to it. redirect() generates a redirect response to the generated URL.

If validation fails, the error is shown to the user. flash() stores messages that can be retrieved when rendering the template.

When the user initially navigates to auth/register, or there was a validation error, an HTML page with the registration form should be shown. render_template() will render a template containing the HTML, which you’ll write in the next step of the tutorial.
'''


# 2. login view

@bp.route('login',methods = ('GET','POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone() #fetchone() returns one row from the query. 

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # check_password_hash() hashes the submitted password in the same way as the stored hash and securely compares them. If they match, the password is valid.

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        # session is a dict that stores data across requests. When validation succeeds, the user’s id is stored in a new session

        flash(error)

    return render_template('auth/login.html')

# Load Logged in User

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


# Logout view
# To log out, you need to remove the user id from the session. Then load_logged_in_user won’t load a user on subsequent requests.

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
            # why auth.login? --> When using a blueprint, the name of the blueprint is prepended to the name of the function, so the endpoint for the login function you wrote above is 'auth.login' because you added it to the 'auth' blueprint.

        return view(**kwargs)

    return wrapped_view

# The functools.wraps decorator is used to preserve the original view function's metadata, like its name and docstring, so it doesn't lose its identity when we replace it with wrapped_view.