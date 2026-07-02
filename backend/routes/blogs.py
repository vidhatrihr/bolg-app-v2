from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from models import db, Blog, Comment, Like
import re

blog_bp = Blueprint("blogs", __name__)


def make_slug(title):
  slug = title.lower().strip()
  slug = re.sub(r'[^a-z0-9\s-]', '', slug)  # strip special chars
  slug = re.sub(r'[\s]+', '-', slug)  # collapses spaces into hyphens
  return slug


def unique_slug(base_slug):
  slug = base_slug
  counter = 1
  # append incrementing suffix until slug is unique
  while Blog.query.filter_by(slug=slug).first():
    slug = f'{slug}-{counter}'
    counter += 1
  return slug


def serialize_blog(blog, current_user_id=None):
  liked = False
  if current_user_id:
    # check if current user's id is among the blog's like
    liked = any(like.user_id == current_user_id for like in blog.likes)
  return {
      'id': blog.id,
      'title': blog.title,
      'slug': blog.slug,
      'description': blog.description,
      'created_at': blog.created_at.isoformat(),
      'updated_at': blog.updated_at.isoformat(),
      'author': {'id': blog.author.id, 'name': blog.author.name},
      'like_count': len(blog.likes),
      'comment_count': len(blog.comments),
      'liked': liked
  }


# get all blogs, newest first
@blog_bp.route('/blogs')
@login_required
def get_blogs():
  blogs = Blog.query.order_by(Blog.created_at.desc()).all()
  return jsonify({'data': [serialize_blog(b, current_user.id) for b in blogs]})


# post/create a new blog
@blog_bp.route('/blogs', methods=['POST'])
@login_required
def create_blog():
  data = request.get_json()
  slug = unique_slug(make_slug(data['title']))
  blog = Blog(
      title=data['title'],
      slug=slug,
      description=data['description'],
      content=data['content'],
      user_id=current_user.id,
  )
  db.session.add(blog)
  db.session.commit()

  return jsonify({'message': 'Blog published', 'data': serialize_blog(blog, current_user.id)})


# get blog with the slug along with full content, likes and comments
@blog_bp.route('/blogs/<slug>')
@login_required
def get_blog(slug):
  blog = Blog.query.filter_by(slug=slug).first_or_404()
  data = serialize_blog(blog, current_user.id)
  data['content'] = blog.content  # content is excluded from serialize_blog (not needed in feed)

  # comments by current_user first and then other user's comments
  user_comments = [c for c in blog.comments if c.user_id == current_user.id]
  other_comments = [c for c in blog.comments if c.user_id != current_user.id]

  # sort each group newest first
  user_comments.sort(key=lambda c: c.created_at, reverse=True)
  other_comments.sort(key=lambda c: c.created_at, reverse=True)
  all_comments = user_comments + other_comments

  data['comments'] = [
      {
          'id': c.id,
          'content': c.content,
          'created_at': c.created_at.isoformat(),
          'user': {'id': c.user_id, 'name': c.user.name},
          'is_mine': current_user.id
      }
      for c in all_comments
  ]

  return jsonify({'data': data})


# get blogs of particular user with user_id
@blog_bp.route('/users/<int:user_id>/blogs')
@login_required
def user_blogs(user_id):
  blogs = Blog.query.filter_by(user_id=user_id).order_by(Blog.created_at.desc()).all()
  return jsonify({'data': serialize_blog(b, current_user.id) for b in blogs})


# mark like or unlike on particular blog
@blog_bp.route('/blogs/<slug>/like', methods=['POST'])
@login_required
def toggle_like(slug):
  blog = Blog.query.filter_by(slug=slug).first_or_404()
  existing = Like.query.filter_by(user_id=current_user.id, blog_id=blog.id).first()
  # unlike: if already liked
  if existing:
    db.session.delete(existing)
    liked = False
  else:
    db.session.add(Like(user_id=current_user.id, blog_id=blog.id))
    liked = True
  db.session.commit()
  return jsonify({'data': {'liked': liked, 'like_count': len(blog.likes)}})


# comment on a blog
@blog_bp.route('/blogs/<slug>/comments', methods=['POST'])
@login_required
def add_comment(slug):
  blog = Blog.query.filter_by(slug=slug).first_or_404()
  data = request.get_json()
  comment = Comment(content=data['content'], user_id=current_user.id, blog_id=blog.id)
  db.session.add(comment)
  db.session.commit()

  return jsonify({
      'message': 'comment added',
      'data': {
          'id': comment.id,
          'content': comment.content,
          'created_at': comment.created_at.isoformat(),
          'user': {'id': current_user.id, 'name': current_user.name},
          'is_mine': True  # always true - commenter is the current user
      }
  })


# delete user's comment
@blog_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
  comment = Comment.query.filter_by(id=comment_id).first_or_404()
  # only owner of comment can delete it
  if comment.user_id != current_user.id:
    return jsonify({'message': 'Forbidden'}), 403
  db.session.delete()
  db.session.commit()
  return jsonify({'message': 'Comment deleted'})
