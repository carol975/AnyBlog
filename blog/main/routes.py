from blog.models import Post
from flask import render_template, url_for, Blueprint, request, Response, json, jsonify
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

main = Blueprint('main', __name__)

@main.route("/home")
@main.route("/home/feed")
def feed_posts():
    page=request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    items = []
    for post in posts.items:
        p = post.serialize_summary()
        print(current_user.id, p.get('author_user_id'))
        if current_user and current_user.id == p.get('author_user_id'):
            p['is_curr_user'] = True
        else:
            p['is_curr_user'] = False
        items.append(p)
    
    data = {
        'items': items,
        'curr_page': posts.page,
        'total_page': posts.pages

    }
    return Response(json.dumps(data))



@main.route("/about")
def about():
    data = {
        'about': "Welcome to AnyBlog! You can write anything you like here!"
    }
    return Response(json.dumps(data))
