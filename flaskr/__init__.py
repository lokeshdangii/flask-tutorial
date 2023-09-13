import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    
    # __name__ is the name of the current Python module. The app needs to know where it’s located to set up some paths, and __name__ is a convenient way to tell it that.
    # instance_relative_config=True tells the app that configuration files are relative to the instance folder.

    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_mapping() sets some default configuration that the app will use:
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # app.config.from_pyfile() overrides the default configuration with values taken from the config.py file in the instance folder if it exists. For example, when deploying, this can be used to set a real SECRET_KEY.
        app.config.from_pyfile('config.py', silent=True)
        
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path) #os.makedirs() ensures that app.instance_path exists.
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db  # ./db.py
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    return app


# Run The Application --> $ flask --app flaskr run --debug
'''
Now you can run your application using the flask command. From the terminal, tell Flask where to find your application, then run it in debug mode. Remember, you should still be in the top-level flask-tutorial directory, not the flaskr package.

Debug mode shows an interactive debugger whenever a page raises an exception, and restarts the server whenever you make changes to the code. You can leave it running and just reload the browser page as you follow the tutorial.

$ flask --app flaskr run --debug
You’ll see output similar to this:

* Serving Flask app "flaskr"
* Debug mode: on
* Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
* Restarting with stat
* Debugger is active!
* Debugger PIN: nnn-nnn-nnn

Visit http://127.0.0.1:5000/hello in a browser and you should see the “Hello, World!” message. Congratulations, you’re now running your Flask web application!

If another program is already using port 5000, you’ll see OSError: [Errno 98] or OSError: [WinError 10013] when the server tries to start. See Address already in use for how to handle that.

'''