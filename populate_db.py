from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import User, Strategy, Tactic, Base

engine = create_engine('sqlite:///strategytactic.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Test User
test_user = User(name="Corinn Pope", email="corinn.pope@gmail.com", picture="https://pbs.twimg.com/profile_images/742180129674121216/fx3e7ELb.jpg")
session.add(test_user)
session.commit()

# New Strategy
strat1 = Strategy(user_id=1, name="Email Marketing")
session.add(strat1)
session.commit()

# add tactics to email marketing strategy(strat1)
stratTactic11 = Tactic(
						user_id=1,
						name="Auto-Responders",
						description="An autoresponder is just a sequence of email marketing messages that gets sent to subscribers in the order and frequency that you decide.",
					    difficulty="Medium",
					    resource_link="https://webprofits.agency/blog/ultimate-guide-email-sequences/",
					    tool_link="https://www.drip.co/",
					    strategy=strat1
					    )
session.add(stratTactic11)
session.commit()

stratTactic12 = Tactic(
						user_id=1,
						name="Welcome Mat",
						description="A welcome mat is quite similar to a popup. \
						However, the major difference here is that you cannot see the site's \
						content behind a welcome mat. It fills the entire screen. So, when a\
						visitor first happens across your site, they're greeted by a fullscreen\
						message, typically optimized with a prominent call-to-action.",
					    difficulty="Easy",
					    resource_link="https://premium.wpmudev.org/blog/welcome-mats/?omtr=b&utm_expid=3606929-101.yRvM9BqCTnWwtfcczEfOmg.1",
					    tool_link="https://sumo.com/examples",
					    strategy=strat1
						)
session.add(stratTactic12)
session.commit()

# Repeat!
# New Strategy
strat2 = Strategy(user_id=1, name="Content Marketing")
session.add(strat2)
session.commit()

# add tactics to email marketing strategy(strat1)
stratTactic21 = Tactic(
						user_id=1,
						name="Guest Posts",
						description="Guest posting means writing and publishing an article on someone else's website or blog",
					    difficulty="Medium",
					    resource_link="https://blog.kissmetrics.com/guide-to-guest-blogging/",
					    tool_link="https://www.guestposttracker.com/",
					    strategy=strat2
					    )
session.add(stratTactic21)
session.commit()

stratTactic22 = Tactic(
						user_id=1,
						name="Blog Post Promotion",
						description="Once you write a blog post, your work isn't done. To get the results you want, you'll have to promote the heck out of your post.",
					    difficulty="Easy",
					    resource_link="neilpatel.com/blog/the-uncensored-guide-to-promoting-a-blog-post/",
					    tool_link="http://www.buffer.com",
					    strategy=strat2
						)
session.add(stratTactic22)
session.commit()

print "database populated!"