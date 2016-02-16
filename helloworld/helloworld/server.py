import flask

def make_server(global_config, debug=True, host='127.0.0.1', port=5000):
    port = int(port)
    def serve(app):
        assert isinstance(app, flask.Flask)
        app.run(debug=debug, host=host, port=port)
    return serve
