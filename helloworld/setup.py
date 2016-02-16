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
        'paste.server_factory': [
            'native=helloworld.server:make_server',
        ],
        'paste.paster_command': [
             'init-db=helloworld.commands:InitDatabase',
             'init-authz-scopes=helloworld.commands:InitAuthzScopes',
             'create-test-data=helloworld.commands:CreateTestData',
        ],
    },
    zip_safe=False)

