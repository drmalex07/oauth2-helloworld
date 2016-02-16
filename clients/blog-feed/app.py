import json
import flask
import httplib2
from oauth2client import client

app = flask.Flask(__name__)

@app.route('/index')
def index():
  if 'credentials' not in flask.session:
    return flask.redirect(flask.url_for('oauth2callback'))
  credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
  if credentials.access_token_expired:
    return flask.redirect(flask.url_for('oauth2callback'))
  else:
    api_client = credentials.authorize(httplib2.Http())
    resp1, result = api_client.request('https://blog.helloworld.internal:8443/posts', 'GET')  
    resp = flask.make_response(result, 200)
    resp.headers['Content-Type'] = 'application/json'
    return resp


@app.route('/oauth2/callback')
def oauth2_callback():
  flow = client.flow_from_clientsecrets(
      'client_secrets.json',
      scope='http://blog.helloworld.internal:8443/auth/read-post',
      redirect_uri=flask.url_for('oauth2callback', _external=True))
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    return flask.redirect(auth_uri)
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    return flask.redirect(flask.url_for('index'))


if __name__ == '__main__':
  import uuid
  app.secret_key = str(uuid.uuid4())
  app.debug = True
  app.run()
