# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Text, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///evechem_api/data/info.db')
Session = sessionmaker(bind=engine)


Base = declarative_base()
metadata = Base.metadata


class AccessLevel(Base):
    __tablename__ = 'access_levels'

    level = Column(Integer, primary_key=True)
    name = Column(Text)


class Key(Base):
    __tablename__ = 'keys'

    key = Column(Text, primary_key=True)
    access_level = Column(ForeignKey('access_levels.access_level'))
    operation_id = Column(ForeignKey('operations.operation_id'))

    access = relationship('AccessLevel')
    operation = relationship('Operation')


class Operation(Base):
    __tablename__ = 'operations'

    operation_id = Column(Integer, primary_key=True)
    name = Column(Text)
    public_name = Column(Text)