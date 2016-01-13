# Database setup for Gifter Web App
# written by jennifer lyden for Udacity FullStack Nanodegree

import os
import sys
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy import Integer, String, Date, Numeric, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


# Intentionally named "Givers" not "Users" because this isn't a wish-list app,
# but a shopping-record app. The "Users" of this app ARE the "Givers."
class Givers(Base):

    __tablename__ = 'givers'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False)
    picture = Column(String(250))


class Recipients(Base):

    __tablename__ = 'recipients'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    bday = Column(String(20))
    sizes = Column(String(30))
    giver_id = Column(Integer, ForeignKey('givers.id'))
    givers = relationship(Givers)

    # for jsonify
    @property
    def serialize(self):
        return {
                'id': self.id,
                'name': self.name,
                'bday': self.bday,
                'sizes': self.sizes,
        }


class Gifts(Base):

    __tablename__ = 'gifts'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    desc = Column(String(250))
    link = Column(String(250))
    image = Column(String(250))
    status = Column(String(10))
    date_added = Column(Date(), nullable=False)
    date_given = Column(Date())
    giver_id = Column(Integer, ForeignKey('givers.id'))
    givers = relationship(Givers)
    rec_id = Column(Integer, ForeignKey('recipients.id'))
    recipients = relationship(Recipients)

    # for jsonify
    @property
    def serialize(self):
        return {
                'id': self.id,
                'name': self.name,
                'description': self.desc,
                'link': self.link,
                'status': self.status,
        }

engine = create_engine('sqlite:///giftie.db')

Base.metadata.create_all(engine)
