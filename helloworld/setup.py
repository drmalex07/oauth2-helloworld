from setuptools import setup

setup(
    name='helloworld',
    version='0.1',
    description='An example of an OAuth2-capable authorization/resource server',
    url='http://github.com/drmalex07/oauth2-helloworld/helloworld',
    author='Michail Alexakis',
    author_email='malex@example.com',
    license='MIT',
    packages=['helloworld'],
    install_requires=[
        # Note: Moved under requirements.txt
    ],
    setup_requires=[
    ],
    entry_points = {
        'paste.app_factory': [
            'accounts=helloworld.accounts.app:make_app',
            'blog=helloworld.blog.app:make_app',
        ],
        'paste.filter_factory': [
            'session=helloworld.filters:make_session_filter',
            'who=helloworld.filters:make_who_filter',
            'static=helloworld.filters:make_static_filter',
        ],
        'paste.server_factory': [
            'native=helloworld.servers:make_server',
        ],
        'paste.paster_command': [
             'init-db=helloworld.commands:InitDatabase',
             'init-authz-scopes=helloworld.commands:InitAuthzScopes',
             'create-test-data=helloworld.commands:CreateTestData',
        ],
    },
    zip_safe=False)

