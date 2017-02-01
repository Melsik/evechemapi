# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, Numeric, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine('sqlite:///./data/info.db')
Session = sessionmaker(bind=engine)


Base = declarative_base()
metadata = Base.metadata


t_allowed_groups = Table(
    'allowed_groups', metadata,
    Column('equipment', ForeignKey('equipment.type')),
    Column('resource_group', ForeignKey('groups.group_id'))
)


class Equipment(Base):
    __tablename__ = 'equipment'

    type = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey('groups.group_id'))
    name = Column(Text)
    capacity = Column(Numeric)
    cpu = Column(Numeric)
    powergrid = Column(Numeric)

    group = relationship('Group')
    groups = relationship('Group', secondary='allowed_groups')


class Group(Base):
    __tablename__ = 'groups'

    group_id = Column(Integer, primary_key=True)
    name = Column(Text)


class Material(Base):
    __tablename__ = 'materials'

    type = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey('groups.group_id'))
    name = Column(Text)
    volume = Column(Numeric)

    group = relationship('Group')


t_reaction_io = Table(
    'reaction_io', metadata,
    Column('reaction', ForeignKey('reactions.type')),
    Column('input', Integer),
    Column('material', ForeignKey('materials.type')),
    Column('quantity', Integer)
)


class Reaction(Base):
    __tablename__ = 'reactions'

    type = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey('groups.group_id'))
    name = Column(Text)

    group = relationship('Group')


class Tower(Base):
    __tablename__ = 'towers'

    type = Column(Integer, primary_key=True)
    fuel_bay = Column(Numeric)
    stront_bay = Column(Numeric)
    name = Column(Text)
    storage_mult = Column(Numeric)
    cpu = Column(Numeric)
    powergrid = Column(Numeric)
    fuel_usage = Column(Integer)
    stront_usage = Column(Integer)
    fuel_type = Column(ForeignKey('materials.type'))

    material = relationship('Material')

