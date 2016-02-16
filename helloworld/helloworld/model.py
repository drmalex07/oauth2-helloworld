import os
import hashlib
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm
from sqlalchemy import (
    Table, Column,
    Integer, String, DateTime, Text, Enum, 
    ForeignKey, Index,
    UniqueConstraint, PrimaryKeyConstraint, CheckConstraint)
from datetime import (datetime, timedelta)
from base64 import (b64encode, b64decode)

Base = declarative_base()

#
# Object-Relational Mapping
#

user_table = Table('user', Base.metadata,
    Column('id', Integer(), primary_key=True, autoincrement=True),
    Column('email', String(64), nullable=False, unique=True),
    Column('fullname', String(128)),
    Column('password', String(64), key='digested_password', nullable=True),
)

class User(Base):
    
    __table__ = user_table

    @staticmethod
    def digest(s): 
        return hashlib.sha256(s).hexdigest()

    def __init__(self, email, password=None, fullname=None):
        self.email = email
        self.fullname = fullname
        self.digested_password = self.digest(password) if password else None
    
    def check_password(self, password):
        return password and (self.digest(password) == self.digested_password)
    
    def __str__(self):
        return '<User %s>' % (self.email)

client_table = Table('client', Base.metadata,
    Column('id', Integer(), primary_key=True, autoincrement=True),
    Column('client_type', Enum('confidential', 'public', name='client_type'), nullable=False),
    Column('uri', String(256), unique=True, nullable=False),
    Column('name', String(128), nullable=False),
    Column('secret', String(128), nullable=True), # Note: store digested secret ?
    Column('user_id', Integer(), ForeignKey('user.id', ondelete='cascade'), nullable=False),
)

class Client(Base):
    '''Represents a `client` as described at rfc6749#section-1.1.
    
    See on client registration at rfc6749#section-2
    '''
    
    __table__ = client_table

    user = orm.relationship(User)   

    def __init__(self, uri, name, client_type='public', secret=None, user=None):
        self.uri = uri
        self.name = name
        self.client_type = client_type
        self.secret = secret
        self.redirect_uris = []
        self.user = user
        self.user_id = user.id if user else None

    def __str__(self):
        return '<Client uri="%s">' % (self.uri)

redirection_uri_table = Table('redirection_uri', Base.metadata,
    Column('uri', String(256), nullable=False),
    Column('client_id', Integer(), ForeignKey('client.id', ondelete='cascade'), index=True, nullable=False),
    PrimaryKeyConstraint('uri', 'client_id'),
) 

class RedirectionUri(Base):

    __table__ = redirection_uri_table

    client = orm.relationship(Client, backref=orm.backref('redirect_uris'))
    
    def __init__(self, client, uri='urn:ietf:wg:oauth:2.0:oob'):
        self.uri = uri
        self.client = client
        self.client_id = client.id if client else None

application_table = Table('application', Base.metadata,
    Column('id', Integer(), primary_key=True, autoincrement=True),
    Column('name', String(256), unique=True, nullable=False),
    Column('title', String(256)),
    Column('url', String(256), unique=True, nullable=False),
    Column('scope_prefix', String(256), unique=True, nullable=False),
)

class Application(Base):
    '''Respesents a `resource server` as described at rfc6749#section-1.1'''

    __table__ = application_table

    def __init__(self, name, url, scope_prefix=None, title=None):
        self.name = name
        self.url = url
        self.scope_prefix = scope_prefix or url
        self.title = title

    def __str__(self):
        return '<Application "%s" at %s>' % (self.name, self.url)
    
scope_table = Table('scope', Base.metadata,
    Column('id', Integer(), primary_key=True, autoincrement=True),
    Column('name', String(128), nullable=False),
    Column('app_id', Integer(), ForeignKey('application.id', ondelete='cascade'), nullable=False),
    UniqueConstraint('name', 'app_id'),
)

class Scope(Base):
    '''Represents an application-specific scope'''
    
    __table__ = scope_table
    
    app = orm.relationship(Application, backref=orm.backref('scopes'))

    def __init__(self, name, app=None):
        self.name = name
        self.app = app
        self.app_id = app.id if app else None

    def as_token(self):
        return self.app.scope_prefix.strip('/') + '/' + self.name
    
    def __str__(self):
        return '<Scope %s>' % (self.as_token())

authorization_code_table = Table('authorization_code', Base.metadata,
    Column('id', Integer(), primary_key=True, autoincrement=True),
    Column('user_id', Integer(), 
        ForeignKey('user.id', ondelete='cascade'), nullable=False),
    Column('client_id', Integer(),
        ForeignKey('client.id', ondelete='cascade'), nullable=False, index=True),
    Column('code', String(128), nullable=False),
    Column('expires', DateTime(), nullable=False),
    Column('exhanged', DateTime(), nullable=True),
)

class AuthorizationCode(Base):
    '''Represents an authorization code, see rfc6749#section-4.1'''
   
    __table__ = authorization_code_table

    ttl = timedelta(seconds=360)

    def __init__(self, code, client, user):
        self.code = code
        self.user = user
        self.user_id = user.id
        self.client = client
        self.client_id = client.id
        self.expires = datetime.now() + self.ttl
        self.exhanged = None

authorization_scope_table = Table('authorization_scope', Base.metadata,
    Column('code_id', Integer(), 
        ForeignKey('authorization_code.id', ondelete='cascade'), nullable=False),
    Column('scope_id', Integer(), ForeignKey('scope.id'), nullable=False),
    PrimaryKeyConstraint('code_id', 'scope_id'),
)

class AuthorizationScope(Base):

    __table__ = authorization_scope_table

    auth_code = orm.relationship(AuthorizationCode, backref=orm.backref('scopes'))
    
    scope = orm.relationship(Scope)

    def __init__(self, code, scope):
        self.code = code
        self.code_id = code.id
        self.scope = scope
        seld.scope_id = scope.id

token_table = Table('token', Base.metadata,
    Column('id', Integer(), primary_key=True, autoincrement=True),
    Column('user_id', Integer(), 
        ForeignKey('user.id', ondelete='cascade'), nullable=False),
    Column('client_id', Integer(),
        ForeignKey('client.id', ondelete='cascade'), nullable=False, index=True),
    Column('access_token', String(128), nullable=False),
    Column('refresh_token', String(128), nullable=True),
    Column('access_expires', DateTime(), nullable=False),
    Column('refresh_expires', DateTime(), nullable=False),
)

class Token(Base):
    '''Represents a bearer token, see rfc6749#section-4.1'''

    __table__ = token_table
    
    access_ttl = timedelta(seconds=3600)

    refresh_ttl = timedelta(days=1)
    
    @staticmethod
    def make_token(length=32):
        s = os.urandom(length)
        return b64encode(s)

    def __init__(self, client, user, access_token=None, refresh_token=None):
        self.client = client
        self.client_id = client.id
        self.user = user
        self.user_id = user.id
        self.access_token = access_token or self.make_token()
        self.refresh_token = refresh_token or self.make_token()
        now = datetime.now()
        self.access_expires = now + self.access_ttl
        self.refresh_expires = now + self.refresh_ttl
        
token_scope_table = Table('token_scope', Base.metadata,
    Column('token_id', Integer(), 
        ForeignKey('token.id', ondelete='cascade'), nullable=False),
    Column('scope_id', Integer(), ForeignKey('scope.id'), nullable=False),
    PrimaryKeyConstraint('token_id', 'scope_id'),
)

class TokenScope(Base):

    __table__ = token_scope_table

    token = orm.relationship(Token, backref=orm.backref('scopes'))
    
    scope = orm.relationship(Scope)

    def __init__(self, code, scope):
        self.code = code
        self.code_id = code.id
        self.scope = scope
        seld.scope_id = scope.id

#
# Session factory
#

# This session factory should be (re)configured when options are available
Session = orm.scoped_session(orm.sessionmaker())
