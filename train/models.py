#!/usr/bin/env python

"""SQLAlchemy Models"""

from datetime import datetime
from sqlalchemy import create_engine, Table, Column, ForeignKey
from sqlalchemy import Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine("sqlite:///database.sqlite")#, echo=True)
Base = declarative_base()

# users on trains
user_trains = Table("passengers", Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id")),
    Column("train_id", Integer, ForeignKey("train.id")),
)

class User(Base):
    __tablename__ = "user"

    id       = Column(Integer, primary_key=True)
    username = Column(String, nullable=False) # Email address
    password = Column(String, nullable=False)
    verified = Column(Boolean, default=False)

    @property
    def serialize(self):
        return dict(
            username=self.username,
        )

class Train(Base):
    __tablename__ = "train"

    id      = Column(Integer, primary_key=True)
    name    = Column(String, nullable=False)
    owner   = Column(Integer, ForeignKey(User.id, ondelete="SET NULL"))
    created = Column(DateTime, default=datetime.utcnow)
    expires = Column(DateTime)

    user = relationship(User)

    # Users signed up on this train
    passengers = relationship(User, secondary=user_trains, backref="trains")

    @property
    def serialize(self):
        return dict(
            id=self.id,
            name=self.name,
            owner=self.user.username,
            created=self.created,
            expires=self.expires,
            passengers=[ u.username for u in self.passengers ],
            meta=dict(
                expired=datetime.utcnow() > self.expires,
            )
        )

Base.metadata.create_all(engine)
