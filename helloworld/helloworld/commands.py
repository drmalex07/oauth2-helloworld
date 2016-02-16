import os
import logging
import paste.deploy
import paste.script 
from paste.deploy.converters import (asbool, aslist, asint)

CONFIG_FILE = 'config.ini'

class Command(paste.script.command.Command):

    group_name = 'helloworld'

class InitDatabase(Command):
    
    summary = "Initialize database"

    # Describe positional arguments    
    max_args = 1
    min_args = 0
    usage = "CONFIG-FILE"
    
    # Describe optional (getopt-style) arguments
    parser = Command.standard_parser(verbose=True)
    parser.add_option('--recreate', '-r', action='store_true', dest='recreate',
        help="Create database from scratch")
    
    def _create_schema(self, config):
        
        import sqlalchemy
        import helloworld.model as model

        database_url = config['database.url']
        engine = sqlalchemy.create_engine(database_url, echo=self.verbose)

        if self.options.recreate:
            model.Base.metadata.drop_all(bind=engine)

        model.Base.metadata.create_all(bind=engine)
        
        logging.info('Tables were created successfully')

    def _initialize_tables(self, config):
       
        pass
            
    def command(self):
        config_file = os.path.realpath(
            self.args[0] if len(self.args) else CONFIG_FILE)
        config_uri = 'config:%s#main' % (config_file)
        config = paste.deploy.appconfig(config_uri)

        if self.verbose:
            logging.basicConfig(level=logging.INFO)

        # Create database schema
        
        self._create_schema(config)

        # Populate tables with initial data

        self._initialize_tables(config)

        return

class InitAuthzScopes(Command):

    summary = 'Initialize application-specific authorization scopes'
    
    # Describe positional arguments    
    max_args = 1
    min_args = 0
    usage = "CONFIG-FILE"
    
    # Describe optional (getopt-style) arguments
    parser = Command.standard_parser(verbose=True)
    parser.add_option("--name", "-n", dest='app_name', default='main')

    def command(self):
        config_file = os.path.realpath(
            self.args[0] if len(self.args) else CONFIG_FILE)
       
        import sqlalchemy
        import helloworld.model as model

        app_name = self.options.app_name

        config_uri = 'config:%s#main' % (config_file)
        config = paste.deploy.appconfig(config_uri)
        database_url = config['database.url']
        engine = sqlalchemy.create_engine(database_url, echo=self.verbose)
        
        if app_name != 'main':
            config_uri = 'config:%s#%s' % (config_file, app_name)
            config = paste.deploy.appconfig(config_uri)
         
        model.Session.configure(bind=engine)
        session = model.Session()
        
        app1 = model.Application(app_name, 
            url = config['url'],
            scope_prefix = config.get('scope_prefix'),
            title = config.get('title'))
        session.add(app1)
        
        for s in aslist(config.get('scopes')):
            session.add(model.Scope(s, app1))

        session.commit()
        return

class CreateTestData(Command):

    summary = "Create test data into database"

    # Describe positional arguments    
    max_args = 1
    min_args = 0
    usage = "CONFIG-FILE"
    
    # Describe optional (getopt-style) arguments
    parser = Command.standard_parser(verbose=True)
    
    def command(self):
        config_file = os.path.realpath(
            self.args[0] if len(self.args) else CONFIG_FILE)
        config_uri = 'config:%s#main' % (config_file)
        config = paste.deploy.appconfig(config_uri)

        if self.verbose:
            logging.basicConfig(level=logging.INFO)

        # Import command-specific modules

        import sqlalchemy
        import base64
        import helloworld.model as model

        # Populate with test data
        
        database_url = config['database.url']
        engine = sqlalchemy.create_engine(database_url, echo=self.verbose)
        logging.info('Connecting to %s', database_url)
        
        model.Session.configure(bind=engine)  
        session = model.Session()

        user1 = model.User('totos@example.com', password='totos-123', fullname='Totos')
        user2 = model.User('foo@example.com', password='foo-123', fullname='Foo')
        session.add_all([user1, user2])
        session.commit()
        
        client1 = model.Client(
            'urn:example:foo:blog-feed', 
            name = 'Blog Feeds', 
            client_type = 'public', 
            secret = base64.b64encode(os.urandom(16)),
            user=user1)
        client1.redirect_uris = [
            model.RedirectionUri(
                client1, 'urn:ietf:wg:oauth:2.0:oob'),
            model.RedirectionUri(
                client1, 'http://blog-feed.foo.internal/oauth2/callback'),
        ]
        session.add(client1)
        session.commit()



        return
   
