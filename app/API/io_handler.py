# -*- coding: utf-8 -*-
"""
    **************
    io_handler.py
    **************

    
"""
__author__ = 'Jonas Van Der Donckt'

import json
import os
from datetime import datetime
from pathlib import Path
from subprocess import run, PIPE

from pytz import timezone

from config import AppConfig as Ac


class SessionIOHandler:
    @staticmethod
    def create_ts_uuid(uuid: str) -> str:
        ts = datetime.now(tz=timezone('Europe/Brussels')).replace(second=0, microsecond=0)
        return '__'.join(str(ts).split(' ') + [uuid])

    @staticmethod
    def _get_save_dir(uuid: str) -> Path:
        save_dir: Path = Ac.DATA_SAVE_DIR.value.joinpath(uuid)
        if not save_dir.exists():
            os.makedirs(save_dir)
        return save_dir

    @staticmethod
    def save_metadata(uuid: str, metadata: dict):
        save_dir = SessionIOHandler._get_save_dir(uuid)
        metadata['timestamp'] = str(datetime.now(tz=timezone('Europe/Brussels')))
        with open(save_dir.joinpath('metadata.json'), 'w') as fp:
            json.dump(metadata, fp, indent=4, sort_keys=True)

    @staticmethod
    def save_wav(uuid: str, file_path: str, data: bytes):
        file_path += '.wav' if not file_path.endswith('.wav') else ''
        save_path = SessionIOHandler._get_save_dir(uuid).joinpath(file_path)
        if not os.path.isdir(save_path.parent):
            os.makedirs(save_path.parent)
        print('save_path', save_path)
        with open(save_path, 'wb') as f:
            f.write(data)

    @staticmethod
    def save_wav_blob(uuid: str, file_path: str, data: bytes):
        file_path += '.blob' if not file_path.endswith('.blob') else ''
        save_path = SessionIOHandler._get_save_dir(uuid).joinpath(file_path)
        if not os.path.isdir(save_path.parent):
            os.makedirs(save_path.parent)
        print('save_path', save_path)
        with open(save_path, 'wb') as f:
            f.write(data)

    @staticmethod
    def save_mood_json(uuid: str, file_path: str, mood: dict):
        file_path += '.json' if not file_path.endswith('.json') else ''
        save_path = SessionIOHandler._get_save_dir(uuid).joinpath(file_path)
        if not os.path.isdir(save_path.parent):
            os.makedirs(save_path.parent)
        with open(save_path, 'w') as fp:
            json.dump(mood, fp, indent=4, sort_keys=True)
