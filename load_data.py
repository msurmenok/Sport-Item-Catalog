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
cat4 = Category(name='Baseball')
cat5 = Category(name='Jogging')
cat6 = Category(name='Time travel')
cat7 = Category(name='Hockey')
cat8 = Category(name='Tennis')

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

item2 = Item(name='Helmet',
             description='May include many additional features such as vents,'
                         ' earmuffs, headphones, goggle mounts, '
                         'and camera mounts.',
             category=cat1,
             user=user1)


item3 = Item(name='Bat',
             description='smooth wooden or metal club',
             category=cat4,
             user=user1)

item4 = Item(name='Glove',
             description='assists players in catching and fielding balls '
                         'hit by a batter or thrown by a teammate',
             category=cat4,
             user=user2)

item5 = Item(name='Climbing Chalk',
             description='soft, white, porous, sedimentary carbonate rock',
             category=cat2,
             user=user1)

item6 = Item(name='Heart Rate Monitor',
             description='',
             category=cat5,
             user=user1)

item7 = Item(name='Fez',
             description='Geronimo!',
             category=cat6,
             user=user2)

item8 = Item(name='Racket',
             description='a light bat having a netting of catgut or nylon '
                         'stretched in a more or less oval frame and used '
                         'for striking the ball',
             category=cat8,
             user=user1)

item9 = Item(name='Climbing Shoes',
             description='have a close fit, little if any padding, and a '
                         'smooth, sticky rubber sole with an extended '
                         'rubber rand',
             category=cat2,
             user=user2)

item10 = Item(name='Ball',
              category=cat3,
              user=user1)

item11 = Item(name='Tardis',
              description='Time And Relative Dimension In Space is a '
                         'time-travelling spacecraft created by the'
                         ' Time Lords, an advanced extraterrestrial '
                         'civilisation. A TARDIS can transport its occupants '
                         'to any point in time and space. The interior of a '
                         'TARDIS is much larger than its exterior. ',
              category=cat6,
              user=user2)

item12 = Item(name='Stick',
              category=cat7,
              user=user1)

item13 = Item(name='Sonic screwdriver',
              description='Multifunctional fictional tool. '
                          'Gets you into anything',
              category=cat6,
              user=user2)

db_session.add(item1)
db_session.add(item2)
db_session.add(item3)
db_session.add(item4)
db_session.add(item5)
# db_session.add(item6)
db_session.add(item7)
db_session.add(item8)
db_session.add(item9)
db_session.add(item10)
db_session.add(item11)
db_session.add(item12)
db_session.add(item13)

db_session.commit()

print("Added items!")

