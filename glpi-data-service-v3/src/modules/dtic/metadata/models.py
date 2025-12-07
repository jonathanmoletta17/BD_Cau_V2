"""
GLPI Data Service V3 - DTIC Metadata Models
Simplified models for metadata tables (Users, Groups, Entities, Locations, Categories, Profiles)
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import TIMESTAMP
from datetime import datetime

from src.core.database import Base


class User(Base):
    """GLPI Users table."""
    __tablename__ = 'glpi_users'
    __table_args__ = {'schema': 'dtic'}
    
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255), index=True)
    realname = Column(String(255))
    firstname = Column(String(255))
    email = Column(String(255), index=True)
    is_active = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False)
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}')>"


class Group(Base):
    """GLPI Groups table."""
    __tablename__ = 'glpi_groups'
    # Schema defined via search_path in Database.get_session()
    
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255), index=True)
    is_task = Column(Boolean, default=False)
    is_itemgroup = Column(Boolean, default=False)
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<Group(id={self.id}, name='{self.name}')>"


class Entity(Base):
    """GLPI Entities table."""
    __tablename__ = 'glpi_entities'
    # Schema defined via search_path in Database.get_session()
    
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255), index=True)
    completename = Column(Text)
    level = Column(Integer)
    entities_id = Column(Integer, index=True)  # Parent ID
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<Entity(id={self.id}, name='{self.name}')>"


class ITILCategory(Base):
    """GLPI ITIL Categories table."""
    __tablename__ = 'glpi_itilcategories'
    # Schema defined via search_path in Database.get_session()
    
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255), index=True)
    completename = Column(Text)
    level = Column(Integer)
    parent_id = Column(Integer, index=True)  # Parent ID
    ancestors_cache = Column(Text)
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<ITILCategory(id={self.id}, name='{self.name}')>"


class Location(Base):
    """GLPI Locations table."""
    __tablename__ = 'glpi_locations'
    # Schema defined via search_path in Database.get_session()
    
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255), index=True)
    level = Column(Integer)
    parent_id = Column(Integer, index=True)  # Parent ID
    ancestors_cache = Column(Text)
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<Location(id={self.id}, name='{self.name}')>"


class Profile(Base):
    """GLPI Profiles table."""
    __tablename__ = 'glpi_profiles'
    # Schema defined via search_path in Database.get_session()
    
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255), index=True)
    is_default = Column(Boolean, default=False)
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<Profile(id={self.id}, name='{self.name}')>"


class GroupUser(Base):
    """N:N relationship between groups and users."""
    __tablename__ = 'glpi_groups_users'
    __table_args__ = (
        UniqueConstraint('users_id', 'groups_id', name='uq_groups_users'),
        {'schema': 'dtic'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    groups_id = Column(Integer, index=True)
    users_id = Column(Integer, index=True)
    is_dynamic = Column(Boolean, default=False)
    is_manager = Column(Boolean, default=False)
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<GroupUser(group={self.groups_id}, user={self.users_id})>"


class ProfileUser(Base):
    """N:N relationship between profiles, users, and entities."""
    __tablename__ = 'glpi_profiles_users'
    __table_args__ = (
        UniqueConstraint('users_id', 'profiles_id', 'entities_id', name='uq_profiles_users'),
        {'schema': 'dtic'}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    users_id = Column(Integer, index=True)
    profiles_id = Column(Integer, index=True)
    entities_id = Column(Integer, index=True)
    is_recursive = Column(Boolean, default=False)
    is_dynamic = Column(Boolean, default=False)
    sincronizado_em = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)

    def __repr__(self):
        return f"<ProfileUser(user={self.users_id}, profile={self.profiles_id})>"
