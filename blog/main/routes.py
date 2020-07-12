from blog.models import Post
from flask import render_template, url_for, Blueprint, request, Response, json, jsonify
from sqlalchemy.exc import SQLAlchemyError

main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    page=request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page )
    return render_template('home.html', posts=posts)

@main.route("/home/feed")
def feed_posts():
    page=request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)
    items = [post.serialize_summary() for post in posts.items]
    data = {
        'items': items,
        'curr_page': posts.page,
        'total_page': posts.pages

    }
    return Response(json.dumps(data))



@main.route("/about")
def about():
    return render_template('about.html', title='About')
