from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from models import db, User
from routes import register_blueprints
from populate_db import populate_db

app = Flask(__name__)
app.secret_key = "super-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

register_blueprints(app)

db.init_app(app)
with app.app_context():
  db.create_all()
  populate_db()

login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)


if __name__ == "__main__":
  app.run(debug=True)
