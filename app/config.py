# -*- coding: utf-8 -*-
"""
    **********
    config.py
    **********

    Application configuration, contains the configurations
    of all the different services used within this application.
"""
__author__ = 'Jonas Van Der Donckt'

import logging
import os
from enum import Enum
from pathlib import Path

CWD = os.path.abspath(os.path.dirname(__file__))
LEVEL = 1  # the # of directories we need to go up to find the module
parent_dir = '/'.join(CWD.split('/')[:-(LEVEL + 1)])


class AppConfig(Enum):
    """
    Contains the configurations of the Flask App
    """
    # https://stackoverflow.com/questions/22463939/demystify-flask-app-secret-key
    SECRET_KEY = 'a day with sunshine is, like you know, not night'.encode("utf8")
    STATIC_FOLDER = 'static'
    TEMPLATE_FOLDER = 'templates'

    PORT = 8090
    DEPLOY = True
    FLASK_DEBUG = False
    USE_DEMO = False

    LOG_FILE = CWD + "/application.log"
    LOG_MODE = logging.INFO
    LOG_FORMAT = "[%(asctime)s]:\t%(levelname)s: [%(funcName)s: %(filename)s, %(lineno)d]: %(message)s"

    # use case specific confs
    IAPS_DIR = Path(CWD).joinpath('static/img/iaps/')
    PISCES_DIR = Path(CWD).joinpath('static/img/PiSCES/')
    RADBOUD_DIR = Path(CWD).joinpath('static/img/Radboud/')
    DEMO_DIR = Path(CWD).joinpath('static/img/demo/')

    # rclone conf path
    RCLONE_CONF_PATH = Path(CWD).joinpath('API/rclone_conf.json')
    SYNC_INTERVAL_S = 3600 * 2

    DATA_SAVE_DIR = Path('/data/semi_guided_speech')
    MARLOES_MODULO = 5  # if this modulo equals 0 -> a marloes will be executed
    PAUSE_MODULO = 9  # if this nbr != 0 and nbr % PAUSE_MODULO == 0
    # -> participant will be instructed a pause
    INITIAL_TIMEOUT = 300000  # initial rest timeout time in ms
