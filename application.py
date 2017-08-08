from flask import Flask
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
    for cat in categories:
        output += cat.name + '<br>'
    output += '<br><hr><br>'
    for item in last_items:
        output += item.name + ' (' + item.category.name + ')<br>'
    return output




# At the end start Flask app.
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)