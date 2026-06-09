import json
from models import Product


def populate_db(db):
    if Product.query.count() > 0:
        return

    with open("products.json", "r") as f:
        data = json.load(f)
        for item in data:
            p = Product(
                title=item["title"],
                brand=item["brand"],
                category=item["category"],
                price=item["price"],
                description=item["description"],
            )
            db.session.add(p)
        db.session.commit()
    print("database seeded!")
