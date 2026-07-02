from .auth import auth_bp as auth_bp
from .blogs import blog_bp as blogs_bp


def register_blueprints(app):
  app.register_blueprint(auth_bp, url_prefix="/api")
  app.register_blueprint(blogs_bp, url_prefix="/api")
