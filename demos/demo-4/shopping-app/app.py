from flask import Flask, request, g, render_template
from models import db, Product, Visitor, Visit, CartItem
from populate_db import populate_db

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///shop.db"
db.init_app(app)

with app.app_context():
    db.create_all()
    populate_db(db)


@app.before_request
def track_visitor():
    g.is_new_visitor = False


@app.route("/")
def index():
    stores = db.session.query(Product.category).distinct().all()
    return render_template("index.html", stores=[s[0] for s in stores])


@app.route("/store/<category>")
def store(category):
    all_products = Product.query.filter_by(category=category).all()
    return render_template("store.html", products=all_products)


if __name__ == "__main__":
    app.run(debug=True)
