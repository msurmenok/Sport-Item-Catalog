from flask import Flask, render_template, url_for
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item


app = Flask(__name__)

# Connect DB.
engine = create_engine('postgresql://vagrant@/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()


# Handle pages.
@app.route('/')
@app.route('/catalog/')
def index():
    output = ''
    categories = db_session.query(Category).order_by(Category.name)
    last_items = db_session.query(Item).order_by(desc(Item.id)).limit(10)

    return render_template('index.html', categories=categories, items=last_items)


@app.route('/catalog/<category_name>/')
@app.route('/catalog/<category_name>/items/')
def showCategory(category_name):
    categories = db_session.query(Category).order_by(Category.name)
    current_category = db_session.query(Category).filter_by(name=category_name).one()
    print(current_category.id)
    print(current_category.name)
    items = db_session.query(Item).filter_by(category_id=current_category.id).all()
    return render_template('category.html', items=items,
                           current_category=current_category, categories=categories)

# At the end start Flask app.
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)