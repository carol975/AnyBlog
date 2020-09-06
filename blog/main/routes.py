from blog.models import Post
from flask import render_template, url_for, Blueprint, request, Response, json, jsonify
from flask_login import current_user
from sqlalchemy.exc import SQLAlchemyError

main = Blueprint('main', __name__)

@main.route("/home")
@main.route("/home/feed")
def feed_posts():
    page=request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)
    print(page)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=per_page, page=page)
    items = []
    for post in posts.items:
        p = post.to_json_summary()
        if current_user.is_authenticated and current_user.id == p.get('author_user_id'):
            p['is_curr_user'] = True
        else:
            p['is_curr_user'] = False
        items.append(p)
    
    data = {
        'items': items,
        'total_items': posts.total

    }
    return Response(json.dumps(data))

@main.route('/home/following')
def get_following_posts():
    pass

@main.route('/home/trending')
def get_trending_posts():
    pass

@main.route("/about")
def about():
    data = {
        'about': "Welcome to AnyBlog! You can write anything you like here!"
    }
    return Response(json.dumps(data))
