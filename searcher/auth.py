import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from os import getenv

bp = Blueprint('auth', __name__, url_prefix='/auth')

user = { 'id': 1, 'username': 'admin' }
password = getenv('APP_PASSWORD')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        form_username = request.form['username']
        form_password = request.form['password']
        if form_username == user['username'] and form_password == password:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials')

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = user

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view
