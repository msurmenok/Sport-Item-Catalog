from flask import Flask, jsonify,  redirect, flash, abort
from flask import render_template, url_for, session, request, make_response

from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import httplib2
import json
import requests
import random
import string

from functools import wraps

from database_setup import Base, User, Category, Item


app = Flask(__name__)

# Connect DB.
engine = create_engine('postgresql://vagrant@/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()


# Decorators
def user_logged_in(function):
    """ Decorator that checks if user is logged in. """
    @wraps(function)
    def wrapper(*args, **kwargs):
        if 'user_id' in session:
            return function(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrapper


def user_owns_item(function):
    """ Decorator that checks that the item was created by current user. """
    @wraps(function)
    def wrapper(category_name, item_name, *args, **kwargs):
        category = db_session.query(Category
                                    ).filter_by(name=category_name).one()
        user_id = session['user_id']
        item = db_session.query(Item
                                ).filter_by(category=category, name=item_name
                                            ).one()

        if item.user_id == user_id:
            return function(category_name, item_name, *args, **kwargs)
        else:
            abort(403)
    return wrapper


# Handle pages.
@app.route('/')
@app.route('/catalog/')
def index():
    """ Main page. Show all categories and 10 latest item. """
    categories = db_session.query(Category).order_by(Category.name)
    last_items = db_session.query(Item).order_by(desc(Item.id)).limit(10)

    return render_template('index.html',
                           categories=categories, items=last_items)


@app.route('/catalog/<category_name>/')
def showCategory(category_name):
    """ Show all items of the specific category. """
    categories = db_session.query(Category).order_by(Category.name)
    current_category = db_session.query(Category
                                        ).filter_by(name=category_name).one()
    items = db_session.query(Item
                             ).filter_by(category_id=current_category.id).all()

    return render_template('category.html',
                           items=items,
                           current_category=current_category,
                           categories=categories)


@app.route('/catalog/<category_name>/<item_name>/')
def viewItem(category_name, item_name):
    """
    View specific item
    Args:
        category_name(str): Name of the parent category.
        item_name(str): Name of the item.
    """
    current_category = db_session.query(Category
                                        ).filter_by(name=category_name).one()
    item = db_session.query(Item
                            ).filter_by(category_id=current_category.id,
                                        name=item_name
                                        ).one()
    return render_template('item.html', category_name=category_name, item=item)


@app.route('/catalog/new/', methods=['GET', 'POST'])
@user_logged_in
def addNewItem():
    """ Create new item. """
    categories = db_session.query(Category).order_by(Category.name)
    if request.method == 'GET':
        return render_template('create_item.html',
                               categories=categories,
                               info=None)
    if request.method == 'POST':
        item_name = request.form['item_name']
        description = request.form['description']
        category_id = request.form['category_id']

        # Check that item_name is not empty.
        info = dict()
        info['description'] = description
        info['category_id'] = category_id
        if not item_name:
            info['error'] = 'Name cannot be empty'
            return render_template('create_item.html',
                                   categories=categories,
                                   info=info)

        # Check if such item is already exists.
        items = db_session.query(Item).filter_by(category_id=category_id).all()
        names = [item.name for item in items]
        if item_name in names:
            info['error'] = 'Such item already exists'
            return render_template('create_item.html',
                                   categories=categories,
                                   info=info)

        new_item = Item(name=item_name, description=description,
                        category_id=category_id, user_id=session['user_id'])
        db_session.add(new_item)
        db_session.commit()

        flash('Item was created')
    return redirect(url_for('index'))


@app.route('/catalog/<category_name>/<item_name>/edit/',
           methods=['GET', 'POST'])
@user_logged_in
@user_owns_item
def editItem(category_name, item_name):
    """
    Edit specific item.
    Args:
        category_name(str): Name of parent category.
        item_name(str): Name of the item that should be edited.
    """
    categories = db_session.query(Category).order_by(Category.name)

    current_category = db_session.query(Category
                                        ).filter_by(name=category_name).one()
    item = db_session.query(Item
                            ).filter_by(category_id=current_category.id,
                                        name=item_name
                                        ).one()

    info = dict()
    info['item_name'] = item.name
    info['description'] = item.description
    info['category_id'] = item.category_id
    info['category_name'] = category_name
    info['error'] = ''

    if request.method == 'GET':
        return render_template('edit_item.html',
                               categories=categories,
                               info=info)

    if request.method == 'POST':
        item_name = request.form['item_name']
        description = request.form['description']
        category_id = request.form['category_id']

        print("Current item name: %s" % item.name)
        print("item name: %s" % item_name)
        print("Description: %s" % description)
        print("Category_id: %s" % category_id)
        # Check that item_name is not empty.
        info['description'] = description
        info['category_id'] = category_id
        if not item_name:
            info['error'] = 'Name cannot be empty'
            return render_template('edit_item.html',
                                   categories=categories,
                                   info=info)

        # Check if such item is already exists.
        items = db_session.query(Item).filter_by(category_id=category_id).all()
        names = [i.name for i in items]
        if item_name != item.name and item_name in names:
            info['error'] = 'Item "%s" is already exists. The old one %s' % \
                            (item_name, item.name)
            return render_template('edit_item.html',
                                   categories=categories,
                                   info=info)

        item.name = item_name
        item.description = description
        item.category_id = category_id

        db_session.commit()
        flash('Item was edited')
    return redirect(url_for('index'))


@app.route('/catalog/<category_name>/<item_name>/delete/')
@user_logged_in
@user_owns_item
def deleteItem(category_name, item_name):
    """
    Delete specific item.
    Args:
        category_name(str): Name of parent category.
        item_name(str): Name of the item that should be deleted.
    """
    current_category = db_session.query(Category
                                        ).filter_by(name=category_name).one()
    item = db_session.query(Item
                            ).filter_by(category_id=current_category.id,
                                        name=item_name
                                        ).one()
    db_session.delete(item)
    db_session.commit()
    flash('Item "%s" successfully deleted' % item.name)
    return redirect(url_for('index'))


@app.route('/login/')
def login():
    """ User log in. """
    state = ''.join([random.choice(string.ascii_letters + string.digits)
                     for x in range(0, 32)])
    session['state'] = state
    return render_template('login.html', state=state)


@app.route('/disconnect/')
@user_logged_in
def disconnect():
    """ User log out. """
    provider = session.get('provider')
    if provider:
        if provider == 'facebook':
            fbdisconnect()
            del session['facebook_id']
        if provider == 'google':
            gdisconnect()
            del session['gplus_id']
        del session['name']
        del session['email']
        del session['picture']
        del session['user_id']
        del session['provider']
        del session['access_token']
        flash('You were successfully logged out.')

    return redirect(url_for('index'))


# Facebook OAuth
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """ Sign in using Facebook account. """
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    access_token = request.data
    app_id = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']

    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (  # NOQA
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    token = result.split(',')[0].split(':')[1].replace('"', '')
    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    print(data)
    session['provider'] = 'facebook'
    session['name'] = data['name']
    session['email'] = data['email']
    session['facebook_id'] = data['id']
    session['access_token'] = access_token

    # Get user picture.
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    session['picture'] = data["data"]["url"]

    # If user doesn't exist, create a new one
    user_id = getUserID(session['email'])
    if not user_id:
        user_id = createUser(session)
    session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += session['name']

    output += '!</h1>'
    output += '<img class="img-circle" src="'
    output += session['picture']
    output += '" style = "width: 200px; height: 200px;">'
    flash('You were successfully logged in as %s' % session['name'])
    return output


@app.route('/fbdisconnect/')
def fbdisconnect():
    """ Sign out from Facebook account. """
    facebook_id = session['facebook_id']
    access_token = session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % \
          (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return 'You have been logged out'


# Google OAuth
@app.route('/gconnect', methods=['POST'])
def gconnect():
    """ Sign in using Google account. """
    # Validate state token
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('g_client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    gplus_id = credentials.id_token['sub']
    stored_access_token = session.get('access_token')
    stored_gplus_id = session.get('gplus_id')

    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps
                                 ('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    result = requests.get(userinfo_url, params=params)

    data = result.json()

    session['provider'] = 'google'
    session['name'] = data['name']
    session['email'] = data['email']
    session['gplus_id'] = gplus_id
    session['picture'] = data['picture']
    session['access_token'] = access_token

    # If user doesn't exist, create a new one
    user_id = getUserID(session['email'])
    if not user_id:
        user_id = createUser(session)
    session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += session['name']

    output += '!</h1>'
    output += '<img class="img-circle" src="'
    output += session['picture']
    output += '" style = "width: 200px; height: 200px;">'
    flash('You were successfully logged in as %s' % session['name'])
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """ Sign out from Google account. """
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
          session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        return 'Successfully disconnected.'
    else:
        return 'Failed to revoke token for given user.'


# JSON API.
@app.route('/catalog.json/')
def getCatalogJSON():
    """ JSON endpoint for all categories and their items. """
    categories = db_session.query(Category).all()
    return jsonify(Category=[createCategoryDict(category)
                             for category in categories])


@app.route('/<category_name>.json/')
@app.route('/catalog/<category_name>.json/')
def getCategoryJSON(category_name):
    """ JSON endpoint for the specific category. """
    category = db_session.query(Category).filter_by(name=category_name).one()
    return jsonify(Category=createCategoryDict(category))


@app.route('/<category_name>/<item_name>.json/')
@app.route('/catalog/<category_name>/<item_name>.json/')
def getItemJSON(category_name, item_name):
    """ JSON endpoint for the specific item. """
    category = db_session.query(Category).filter_by(name=category_name).one()
    item = db_session.query(Item
                            ).filter_by(name=item_name, category=category
                                        ).one()
    return jsonify(Item=item.serialize)


# JSON helper functions.
def createCategoryDict(category):
    """
    Creates serialized representation of the category and all its items.
    Args:
        category(Category): Object of category that will be serialized.
    Returns:
        Serialized representation (dictionary) of the category
        and its items.
    """
    serialized_category = category.serialize

    items = db_session.query(Item).filter_by(category_id=category.id).all()
    if items:
        serialized_category['items'] = [item.serialize for item in items]
    return serialized_category


# User helper functions.
def createUser(session):
    """
    Creates new user in Database.
    Args:
        session(Flask session): Current session with user information.
    Returns:
        Id of created user.
    """
    new_user = User(
        name=session['name'],
        email=session['email'],
        picture=session['picture'])
    db_session.add(new_user)
    db_session.commit()
    user = db_session.query(User).filter_by(email=session['email']).one()
    return user.id


def getUserInfo(user_id):
    """
    Finds user by his/her id
    Args:
        user_id(str): User's id.
    Returns:
        User object.
    """
    user = db_session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """
    Finds user id by his/her email
    Args:
        email (str): User's email.
    Returns:
        User id if user exists, otherwise None.
    """
    try:
        user = db_session.query(User).filter_by(email=email).one()
        return user.id
    except NoResultFound:
        return None


# At the end start Flask app.
if __name__ == '__main__':
    app.secret_key = 'ADD YOUR SECRET KEY HERE'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
