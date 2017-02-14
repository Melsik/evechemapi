# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Text, create_engine, Boolean
from sqlalchemy.orm import relationship, sessionmaker, backref
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///evechem_api/data/application.db')
Session = sessionmaker(bind=engine)


Base = declarative_base()
metadata = Base.metadata



class Key(Base):
    __tablename__ = 'keys'

    value = Column(Text, primary_key=True)
    permission = Column(Text)
    operation_id = Column(ForeignKey('operations.id'))
    name = Column(Text)



class Operation(Base):
    __tablename__ = 'operations'

    id = Column(Integer, primary_key=True)
    name = Column(Text)
    public_name = Column(Text)

    towers = relationship('Tower', backref='operation', cascade='all, delete-orphan')
    keys = relationship('Key', backref='operation', cascade='all, delete-orphan')
    master_key = relationship('Key' , uselist=False, primaryjoin="and_(Operation.id==Key.operation_id,Key.permission=='master')")


class Permission(Base):
    __tablename__ = 'permissions'

    name = Column(Text, primary_key=True)

################ Tower Mapping ####################
class Equipment(Base):
    __tablename__ = 'equipment'

    id = Column(Integer, primary_key=True)
    type = Column(Integer)
    name = Column(Text)
    process_id = Column(ForeignKey('processes.id'))
    last_updated = Column(Integer)
    resource = Column(Integer)
    contains = Column(Integer)
    online = Column(Boolean)


    links = relationship('Link', primaryjoin='or_(Equipment.id==Link.target,Equipment.id==Link.source)', cascade='all, delete-orphan')
    inputs = relationship('Link', primaryjoin='Equipment.id==Link.target')
    outputs = relationship('Link', primaryjoin='Equipment.id==Link.source')


class Link(Base):
    __tablename__ = 'links'

    source = Column(ForeignKey('equipment.id'), primary_key=True)
    target = Column(ForeignKey('equipment.id'), primary_key=True)
    resource = Column(Integer, primary_key=True)


class Process(Base):
    __tablename__ = 'processes'

    id = Column(Integer, primary_key=True)
    tower_id = Column(ForeignKey('towers.id'))

    equipment = relationship('Equipment', backref='process', cascade='all, delete-orphan', lazy='dynamic')


class Tower(Base):
    __tablename__ = 'towers'

    id = Column(Integer, primary_key=True)
    op_id = Column(ForeignKey('operations.id'))
    type = Column(Integer)
    system = Column(Text)
    planet = Column(Integer)
    moon = Column(Integer)
    name = Column(Text)
    online = Column(Boolean)
    sov = Column(Boolean)
    cycles_at = Column(Text)
    fuel_count = Column(Integer)
    fuel_last_update = Column(Integer)
    stront_count = Column(Integer)

    processes = relationship('Process', backref='tower', cascade='all, delete-orphan',lazy='dynamic')