from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from datetime import datetime
from uuid import uuid4
from werkzeug.exceptions import abort
from searcher.models import Searcher
from os import getenv

from searcher.auth import login_required

bp = Blueprint('search', __name__)

post_id_to_post = {}

searcher = Searcher(getenv('OPENAI_API_KEY'))

@bp.route('/')
def index():
    if g.user is not None and g.user['id'] is not None:
        posts = post_id_to_post.values()
    else:
        posts = []
    return render_template('search/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            now = datetime.now()
            id = str(uuid4())
            post = { 'id': id, 'title': title, 'body': body, 'author_id': g.user['id'], 'created_at': now, 'updated_at': now }
            post_id_to_post[id] = post
            return redirect(url_for('search.index'))

    return render_template('search/create.html')


def get_post(id, check_author=False):
    post = post_id_to_post.get(id)

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            now = datetime.now()
            new_post = { 'id': id, 'title': title, 'body': body, 'author_id': g.user['id'], 'created_at': post['created_at'], 'updated_at': now }
            post_id_to_post[id] = new_post
            return redirect(url_for('search.index'))

    return render_template('search/update.html', post=post)


@bp.route('/<id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = post_id_to_post.get(id)
    if post is not None:
        del post_id_to_post[id]

    return redirect(url_for('search.index'))


@bp.route('/train', methods=('POST',))
@login_required
def train():
    searcher.train(post_id_to_post.values())
    flash('Trained!')
    return redirect(url_for('search.index'))


@bp.route('/query', methods=('GET', 'POST'))
@login_required
def query():
    answer = None
    if request.method == 'POST':
        query = request.form['query']
        answer = searcher.ask(query)
        return render_template('search/query.html', query=query, answer=answer)

    return render_template('search/query.html', answer=None)
