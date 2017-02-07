# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Text, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///evechem_api/data/application.db')
Session = sessionmaker(bind=engine)


Base = declarative_base()
metadata = Base.metadata


class Key(Base):
    __tablename__ = 'keys'

    key = Column(Text, primary_key=True)
    permission_level = Column(ForeignKey('permissions.level'))
    operation_id = Column(Integer)

    permission = relationship('Permission')


class Operation(Base):
    __tablename__ = 'operations'

    operation_id = Column(Integer, primary_key=True)
    name = Column(Text)
    public_name = Column(Text)



class Permission(Base):
    __tablename__ = 'permissions'

    level = Column(Integer, primary_key=True)
    name = Column(Text)
