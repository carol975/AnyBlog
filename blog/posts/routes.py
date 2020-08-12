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
@posts.route('/post/new', methods=['POST'])
@login_required
def new_post():
    form = PostForm(csrf_enabled=False)
    if form.validate_on_submit():
        # author is the bacref
        summary = "This is a summary place holder.This is a summary place holder. This is a summary place holder.This is a summary place holder."
        post = Post(title=form.title.data,
                    content=form.content.data, summary=summary, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        return Response(status=200)
    return Response(status=400)


@posts.route('/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get(post_id).to_json()
    if current_user and current_user.id == post['author_user_id']:
        post['is_curr_user'] = True
    else:
        post['is_curr_user'] = False 
   
    return Response(json.dumps(post))


@posts.route('/post/<int:post_id>/update', methods=['POST'])
@login_required
def update_post(post_id):
    post = Post.query.get(post_id)
    if not post or post.author != current_user:
        return Response(status=403)
    else:
        form = PostForm(csrf_enabled=False)
        if form.validate_on_submit():
            post.title = form.title.data
            print(post.content)
            post.content = form.content.data
            db.session.commit()
            return Response(status=200)
        return Response(status=400)
        


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get(post_id)
    if not post or post.author != current_user:
        # forbidden route
        return Response(status=403)

    db.session.delete(post)
    db.session.commit()
    return Response(status=200)


# @posts.route('/upload_image', methods=['GET', 'POST'])
# @login_required
# def upload_image():
#     if request.method == 'POST':
#         files = request.files
#         print(files)
#     print('hello world, you"re uploading image right NOWWNOWNWOW')
#     return Response(jsonify(files=[{'url':'', 'fileName':'Something'}, ]), 204)
