from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from datetime import datetime
from uuid import uuid4
from werkzeug.exceptions import abort
from searcher.models import Searcher, TrainingError, Fact
from os import getenv, environ
from searcher.auth import login_required
from searcher.extensions import db

bp = Blueprint('search', __name__)

environ['TOKENIZERS_PARALLELISM'] = 'false'

searcher = Searcher(getenv('OPENAI_API_KEY'), getenv('OPENAI_MODEL_NAME'), getenv('CHROMA_HOST', 'localhost'), getenv('CHROMA_PORT', '8000'))

@bp.route('/')
def index():
    if g.user is None or g.user['id'] is None:
        return redirect(url_for('auth.login'))
    posts = Fact.query.all()
    return render_template('search/index.html', posts=posts)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not body:
            error = 'Body is required.'

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            now = datetime.now()
            id = str(uuid4())
            post = Fact(id=id, title=title, body=body, author_id=g.user['id'], created_at=now, updated_at=now)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('search.index'))

    return render_template('search/create.html')


def get_post(id, check_author=False):
    post = Fact.query.get(id)

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

        if not body:
            error = 'Body is required.'

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            post = Fact.query.get(id)
            if post is not None:
                post.title = title
                post.body = body
                post.updated_at = datetime.now()
                db.session.commit()
            return redirect(url_for('search.index'))

    return render_template('search/update.html', post=post)


@bp.route('/<id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = Fact.query.get(id)
    if post is not None:
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for('search.index'))


@bp.route('/train', methods=('POST',))
@login_required
def train():
    try:
        searcher.train(list(map(lambda p: p.body, Fact.query.all())))
        flash('Trained!')
    except TrainingError as training_error:
        flash(training_error.message)
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
