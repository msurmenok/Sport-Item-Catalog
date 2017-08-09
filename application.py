from flask import Flask, render_template, url_for, jsonify, session
from sqlalchemy import create_engine, asc, desc

from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

import httplib2, json, requests, random, string


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
def showCategory(category_name):
    categories = db_session.query(Category).order_by(Category.name)
    current_category = db_session.query(Category).filter_by(name=category_name).one()
    items = db_session.query(Item).filter_by(category_id=current_category.id).all()

    return render_template('category.html', items=items,
                           current_category=current_category, categories=categories)


@app.route('/catalog/<category_name>/<item_name>/')
def viewItem(category_name, item_name):
    current_category = db_session.query(Category).filter_by(name=category_name).one()
    item = db_session.query(Item).filter_by(category_id=current_category.id, name=item_name).one()
    return render_template('item.html', item=item)


@app.route('/catalog/<item_name>/edit')
def editItem(item_name):
    pass


@app.route('/catalog/<item_name>/delete/')
def deleteItem(item_name):
    pass


@app.route('/login/')
def login():
    state = ''.join([random.choice(string.ascii_letters + string.digits) for x in range(0, 32)])
    session['state'] = state
    return render_template('login.html', state=state)


# Facebook OAuth
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    pass


# JSON API.
@app.route('/catalog.json/')
def getCatalogJSON():
    categories = db_session.query(Category).all()
    return jsonify(Category=[createCategoryDict(category) for category in categories])


@app.route('/<category_name>.json/')
@app.route('/catalog/<category_name>.json/')
def getCategoryJSON(category_name):
    category = db_session.query(Category).filter_by(name=category_name).one()
    return jsonify(Category=createCategoryDict(category))


@app.route('/<category_name>/<item_name>.json/')
@app.route('/catalog/<category_name>/<item_name>.json/')
def getItemJSON(category_name, item_name):
    category = db_session.query(Category).filter_by(name=category_name).one()
    item = db_session.query(Item).filter_by(name=item_name, category=category).one()
    return jsonify(Item=item.serialize)


# JSON Helper functions.
def createCategoryDict(category):
    serialized_category = category.serialize

    items = db_session.query(Item).filter_by(category_id=category.id).all()
    if items:
        serialized_category['items'] = [item.serialize for item in items]
    return serialized_category


# At the end start Flask app.
if __name__ == '__main__':
    app.secret_key = 'ADD YOUR SECRET KEY HERE'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
