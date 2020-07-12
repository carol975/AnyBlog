import secrets
import os

from blog import db
from blog.posts.forms import PostForm
from blog.models import Post
from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint, 
                   Response, json)
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.exc import SQLAlchemyError

posts = Blueprint('posts', __name__)


# TODO use blueprint to separate the routes
@posts.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        # author is the bacref
        summary = "This is a summary place holder.This is a summary place holder. This is a summary place holder.This is a summary place holder."
        post = Post(title=form.title.data,
                    content=form.content.data, summary=summary, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        flash('A new post has been created', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@posts.route('/post/<int:post_id>', methods=['GET', 'POST'])
# def get_post(post_id):
#     # add customized 404 page
#     post = Post.query.get_or_404(post_id)
#     return render_template('post.html', title=post.title, post=post)
def get_post(post_id):
    post = Post.query.get(post_id).serialize()
    return Response(json.dumps(post))


@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        # forbidden route
        abort(403)
    else:
        form = PostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.content = form.content.data
            db.session.commit()
            flash('Your post has been updated!', 'success')
            return redirect(url_for('posts.get_post', post_id=post.id))

        elif request.method == 'GET':
            form.title.data = post.title
            form.content.data = post.content
            return render_template('create_post.html', title='Update Post',
                                   form=form, legend='Update Post')


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        # forbidden route
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))


@posts.route('/upload_image', methods=['GET', 'POST'])
@login_required
def upload_image():
    if request.method == 'POST':
        files = request.files
        print(files)
    print('hello world, you"re uploading image right NOWWNOWNWOW')
    return Response(jsonify(files=[{'url':'', 'fileName':'Something'}, ]), 204)
