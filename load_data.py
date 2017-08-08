from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

engine = create_engine('postgresql://vagrant@/catalog')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# Create dummy user
user1 = User(name='Rick Sanchez', email='mad@scientist.org')
user2 = User(name='The Doctor', email='doctor@who.uk')

db_session.add(user1)
db_session.add(user2)

db_session.commit()

# Create few categories
cat1 = Category(name='Snowboarding')
cat2 = Category(name='Bouldering')
cat3 = Category(name='Soccer')
cat4 = Category(name='Hiking')
cat5 = Category(name='Jogging')
cat6 = Category(name='Time travel')

db_session.add(cat1)
db_session.add(cat2)
db_session.add(cat3)
db_session.add(cat4)
db_session.add(cat5)

db_session.commit()

# Create few items
item1 = Item(name='Snowboard',
             description='A board resembling a short, broad ski, used for '
                         'sliding downhill on snow',
             category=cat1,
             user=user1)

item2 = Item(name='Tardis',
             description='Time And Relative Dimension In Space is a '
                         'time-travelling spacecraft created by the'
                         ' Time Lords, an advanced extraterrestrial '
                         'civilisation. A TARDIS can transport its occupants '
                         'to any point in time and space. The interior of a '
                         'TARDIS is much larger than its exterior. ',
             category=cat6,
             user=user2
             )

db_session.add(item1)
db_session.add(item2)

db_session.commit()

print("Added items!")

