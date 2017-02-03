# coding: utf-8
from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint, Integer, Numeric, Table, Text, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

engine = create_engine('sqlite:///evechem_api/data/info.db')
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
    capacity = Column(Float)
    cpu = Column(Float)
    powergrid = Column(Float)

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
    volume = Column(Float)

    group = relationship('Group')


class ReactionMaterial(Base):
    __tablename__ = 'reaction_io'

    reaction_id = Column('reaction', ForeignKey('reactions.type'),primary_key=True)
    is_input = Column('is_input', Boolean, primary_key=True)
    material_id = Column('material', ForeignKey('materials.type'),primary_key=True)
    quantity = Column('quantity', Integer)

    reaction = relationship('Reaction')
    material = relationship('Material')


class Reaction(Base):
    __tablename__ = 'reactions'

    type = Column(Integer, primary_key=True)
    group_id = Column(ForeignKey('groups.group_id'))
    name = Column(Text)

    group = relationship('Group')

    materials = relationship('ReactionMaterial')


class Tower(Base):
    __tablename__ = 'towers'

    type = Column(Integer, primary_key=True)
    fuel_bay = Column(Float)
    stront_bay = Column(Float)
    name = Column(Text)
    storage_mult = Column(Float)
    cpu = Column(Float)
    powergrid = Column(Float)
    fuel_usage = Column(Integer)
    stront_usage = Column(Integer)
    fuel_type = Column(ForeignKey('materials.type'))

    fuel = relationship('Material')