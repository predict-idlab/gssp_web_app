# -*- coding: utf-8 -*-
"""
    *******
    app.py
    *******

    The starting point of the `Flask <http://flask.pocoo.org/>`_ application.
    This module does also configure the logger.

    Note:
        The SSL certificate is self signed:
        use https://cheapsslsecurity.com/ to verify
        it by a trusted certificate authority.

    source
    ******
    `link <http://kracekumar.com/post/54437887454/ssl-for-flask-local-development/>`_
"""
__author__ = 'Jonas Van Der Donckt'

import logging

from config import AppConfig
from routes import app

# Configure the logger and start the application
if __name__ == '__main__':
    logging.basicConfig(filename=AppConfig.LOG_FILE.value, level=AppConfig.LOG_MODE.value,
                        format=AppConfig.LOG_FORMAT.value)

    # start sync background thread
    if AppConfig.DEPLOY.value:
        app.run(host='0.0.0.0', debug=True, port=80)
    else:
        app.run(debug=AppConfig.FLASK_DEBUG.value, port=AppConfig.PORT.value)
