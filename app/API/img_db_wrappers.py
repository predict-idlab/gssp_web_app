# -*- coding: utf-8 -*-
"""
    ************
    img_db_wrappers.py
    ************

    
"""
__author__ = 'Jonas Van Der Donckt'

from pathlib import Path
from config import AppConfig as Ac
from typing import List, Tuple
import random


class ImageDBWrapper:
    def __init__(self, img_db_folder: Path, db_name: str, img_extension='jpg'):
        self.img_dir = img_db_folder
        self.db_name = db_name
        assert self.img_dir.is_dir()

        self.images: List[str] = list(map(lambda x: x.name, self.img_dir.glob(f'*.{img_extension}')))

    def get_shuffled_images(self) -> List[str]:
        shuffled_images = self.images.copy()
        random.shuffle(shuffled_images)
        return shuffled_images

    # todo -> some custom logic still
    def get_img_path(self, img_name: str) -> str:
        return str(self.img_dir.joinpath(img_name))


IAPS_DB = ImageDBWrapper(Ac.IAPS_DIR.value, db_name='IAPS', img_extension='jpg')
PISCES_DB = ImageDBWrapper(Ac.PISCES_DIR.value, db_name='PisCES', img_extension='jpg')
RADBOUD_DB = ImageDBWrapper(Ac.RADBOUD_DIR.value, db_name='Radboud', img_extension='jpg')
DEMO_DB = ImageDBWrapper(Ac.DEMO_DIR.value, db_name='demo', img_extension='jpg')


class ImageDBRegistry:
    def __init__(self, image_dbs: List[ImageDBWrapper], shuffle_method: str = 'merged'):
        """
        :param image_dbs: The list of databases that will be
        :param shuffle_method: Must be either of:
            * `merged`: first merges both dataframes
            * `one_by_one`: shuffles both databases
            * `chronological`: shuffles the databases and appends them as fed to the regitry
        """
        self.shuffle_method = shuffle_method
        self.db_registry = {}
        for image_db in image_dbs:
            self.db_registry[image_db.db_name] = image_db

    def get_shuffled_images(self) -> List[Tuple[str, str]]:
        shuffled_img_list: List[Tuple[str, str]] = []  # first key is img name, second key in db_name
        if self.shuffle_method == 'merged':
            for db_name, img_db in self.db_registry.items():
                shuffled_img_list += [(img_name, db_name) for img_name in img_db.get_shuffled_images()]
                random.shuffle(shuffled_img_list)
        elif self.shuffle_method == 'one_by_one':
            tmp_list: List[List[Tuple[str, str]]] = []  # withholds the list of tuples
            for db_name, img_db in self.db_registry.items():
                tmp_list.append([(img_name, db_name) for img_name in img_db.get_shuffled_images()])

            for idx in range(0, max(list(map(len, tmp_list)))):
                for shuffled_db in tmp_list:
                    shuffled_img_list += [shuffled_db[idx]] if idx < len(shuffled_db) else []
        else:
            raise ValueError(f'shuffle method: {self.shuffle_method} not supported!')
        return shuffled_img_list

    def get_img_path(self, db_name: str, img_name: str) -> str:
        return self.db_registry[db_name].get_img_path(img_name)


PISCES_RADBOUD_BD = ImageDBRegistry([PISCES_DB, RADBOUD_DB], shuffle_method='one_by_one')
