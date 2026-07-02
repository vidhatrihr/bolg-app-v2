from werkzeug.security import generate_password_hash
from models import db, User, Blog, Like, Comment
import json


def populate_db():
  if User.query.count() > 0:
    return

  vidu = User(
      name="Vidu", email="vidu@example.com", password=generate_password_hash("12345")
  )

  vishnu = User(
      name="Vishnu",
      email="vishnu@example.com",
      password=generate_password_hash("12345"),
  )

  db.session.add_all([vidu, vishnu])
  db.session.commit()

  json_path = "sample_blogs.json"
  with open(json_path, 'r', encoding='utf-8') as f:
    blog_data = json.load(f)

  user_map = {
      'vidu@example.com': vidu,
      'vishnu@example.com': vishnu
  }

  blogs = []
  blog_map = {}
  for item in blog_data:
    blog = Blog(
        title=item['title'],
        slug=item['slug'],
        description=item['description'],
        content=item['content'],
        user_id=user_map[item['author_email']].id
    )

    blogs.append(blog)
    blog_map[item['slug']] = blog

  db.session.add_all(blogs)
  db.session.commit()

  like1 = Like(user_id=vishnu.id, blog_id=blog_map['getting-started-with-vue-3'].id)
  like2 = Like(user_id=vishnu.id, blog_id=blog_map['why-sqlite-is-perfect-for-learning'].id)
  like3 = Like(user_id=vidu.id, blog_id=blog_map['flask-in-five-minutes'].id)

  db.session.add_all([like1, like2, like3])

  comments = []
  for item in blog_data:
    blog = blog_map[item['slug']]
    for comment_item in item.get('comments', []):
      comment = Comment(
          content=comment_item['content'],
          user_id=user_map[comment_item['user_email']].id,
          blog_id=blog.id
      )

      comments.append(comment)

  db.session.add_all(comments)
  db.session.commit()
