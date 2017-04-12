from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
# from sqlalchemy import backref

Base = declarative_base()

class User(Base):
  __tablename__ = 'user'

  id = Column(Integer, primary_key=True)
  name = Column(String(250), nullable=False)
  email = Column(String(250), nullable=False)
  picture = Column(String(250))


class Strategy(Base):
  __tablename__ = 'strategy'

  id = Column(Integer, primary_key=True)

  # foreign keys
  user_id = Column(Integer, ForeignKey('user.id'))
  user = relationship(User)
  # configure cascade behavior
  tactics = relationship("Tactic", backref="belongs_to", cascade="all, delete-orphan")
  # table data
  name = Column(String(250), nullable=False)
  # Add Strategy description & picture 
  description = Column(Text)
  image = Column(Text)
  # TODO - Add strategy owner name??

  @property
  def serialize(self):
    """Return object data in easily serializeable format"""
    return {
      'name'  :self.name,
      'id'    :self.id,
      'description' : self.description,
      'image'       : self.image
    }


class Tactic(Base):
  __tablename__ = 'tactic'

  id = Column(Integer, primary_key=True)

  # foreign keys
  strategy_id = Column(Integer, ForeignKey('strategy.id'))
  # delete the assoc. tactics if the strategy is deleted
  strategy = relationship(Strategy, cascade="all, delete-orphan", single_parent=True)
  user_id = Column(Integer, ForeignKey('user.id'))
  user = relationship(User)

  # table data
  name = Column(String(100), nullable=False)
  description = Column(Text)
  difficulty = Column(String(50))
  resource_link = Column(String(500))
  tool_link = Column(String(500))


  @property
  def serialize(self):
    return {
    'id'            : self.id,
    'name'          : self.name,
    'description'   : self.description,
    'difficulty'    : self.difficulty,
    'resource_link' : self.resource_link,
    'tool_link'     : self.tool_link,
    }

engine = create_engine('sqlite:///strategytactic.db')

Base.metadata.create_all(engine)