## README

### What is here?

We refer to roles defined at http://tools.ietf.org/html/rfc6749#section-1.1

 1. The `helloworld` folder represents a resource domain and holds examples for
    the followinf roles:
    * `Autherization-Server` (eg. http://accounts.helloworld.localdomain): 
      authenticate owners, authorize access and issue tokens to 3rd party 
      clients.
    * `Resource-Server` (eg. http://photoalbum.helloworld.localdomain): 
      host user's (aka owner's) protected resources, serve those resources
      responding to properly authorized (token-based) requests.

 2. The `clients` folder contains several client examples (i.e. the `Client` role),
    that follow the OAuth2 authorization flow and request resources from the 
    `helloworld` resource domain.

 3. The `repoze-plugins` folder is an external repository that holds repoze.who 
    plugins. 

