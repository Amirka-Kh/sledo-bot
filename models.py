from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, nullable=False)
    user_tg_id = Column(Integer, unique=True)
    name = Column(String)
    surname = Column(String)
    username = Column(String, unique=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    score = Column(Integer)
    paid = Column(Boolean, default=False)


class Feedback(Base):
    __tablename__ = 'feedback'
    feedback_id = Column(Integer, primary_key=True, nullable=False)
    feedback_name = Column(String, nullable=False)
    feedback = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    author_id = Column(Integer, ForeignKey("users.user_tg_id", ondelete="CASCADE"), nullable=False)
    grade = Column(Integer)


class Quest(Base):
    __tablename__ = 'quest'
    quest_id = Column(Integer, primary_key=True, nullable=False)
    quest_name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    step = Column(Integer, nullable=False, default=0)
    player_id = Column(Integer, ForeignKey("users.user_tg_id", ondelete="CASCADE"), nullable=False)
    active = Column(Boolean, nullable=False, default=False)
    finished = Column(Boolean, nullable=False, default=False)

    __table_args__ = (
        UniqueConstraint('quest_name', 'player_id', name='_quest_player_unique'),
    )
