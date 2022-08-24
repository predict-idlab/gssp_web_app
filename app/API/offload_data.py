# -*- coding: utf-8 -*-
"""
    *****************
    offload_data.py
    *****************

    
"""
__author__ = 'Jonas Van Der Donckt'

import subprocess
from pathlib import Path
from API.hooks import a
import os
import json


class RcloneNextcloudSync:
    def __init__(self, remote: str, remote_root_path: str, rclone_conf_path: Path = None, debug=False):
        """
        :param remote: remote rclone config to back up to
        :param remote_root_path: root path for back-ups on remote location
        """
        self.remote = remote
        self.backup_root_remote = remote_root_path
        self.debug = debug

        if rclone_conf_path is None:
            raise NotImplementedError
        else:
            with open(rclone_conf_path, 'r') as fp:
                conf_dict = json.load(fp)
                rclone_user = conf_dict['user']
                rclone_password = conf_dict['password']

        create_config = f'rclone config create idlab webdav url https://cloud.ilabt.imec.be/remote.php/webdav vendor ' \
                        f'nextcloud user {rclone_user} pass {rclone_password}'
        process = subprocess.Popen(create_config.split(), stdout=subprocess.PIPE)
        self.log(*process.communicate())

    def log(self, output, error):
        """Logs the output of a shell command
        """
        if self.debug:
            print(output)
        if error is not None:
            a.error(error_text=error)

    def mkdir(self, folder_path: str):
        """Makes a remote director
        
        :param folder_path: The (relative) path 
        """
        mkdir = f'rclone mkdir {self.remote}:{self.backup_root_remote}/{folder_path}/'
        process = subprocess.Popen(mkdir.split(), stdout=subprocess.PIPE)
        self.log(*process.communicate())

    def check_synchronized(self, local_folder: Path, destination: str) -> bool:
        """Checks whether the local folder is synchronized to the destination path

        :param local_folder: The Path to the local folder
        :param destination: The destination path, relative to the backup_root_remote path
        :returns: True if everything is synchronized, false otherwise
        """
        cmd = f"rclone check {str(local_folder)} {self.remote}:{self.backup_root_remote}/{destination}"

        result = subprocess.run(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stderr.decode("utf-8"))

        return not any(['File not in webdav root' in line for line in result.stderr.decode("utf-8").split('\n')])

    def copy_to_remote(self, local_folder: Path, destination: str):
        """Copies the local folder to the remote path

        :param local_folder: The local folder that will be copied to remote
        :param destination: The destination, relative to the backup_root_remote path, where the data will be copied to
        """
        self.mkdir(folder_path=destination)
        cmd = f"rclone copy {str(local_folder)} {self.remote}:{self.backup_root_remote}/{destination} -P"
        p1 = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        self.log(*p1.communicate())

# if __name__ == '__main__':
#     from API.hooks import AlertManager
#     from config import AppConfig
#
#     a = AlertManager()
#
#     sync = RcloneNextcloudSync(remote='idlab', remote_root_path='/speech_web_app/backup',
#                                rclone_conf_path=AppConfig.RCLONE_CONF_PATH.value, debug=False)
#
#     # iterate over all the folders in the data dir
#     for folder in sorted(AppConfig.DATA_SAVE_DIR.value.iterdir(), key=os.path.getmtime, reverse=True):
#         if folder.is_dir():
#             print(folder.name)
#             if not sync.check_synchronized(local_folder=folder, destination=folder.name):
#                 print(f'syncing: {str(folder)}')
#                 sync.copy_to_remote(local_folder=folder, destination=folder.name)
#                 print('rclone sync', sync.check_synchronized(local_folder=folder, destination=folder.name))
#                 a.info(module='offloader', info_text=f'synchronized: {folder.name}')
#             else:
#                 print(f'already synced: {folder.name}')
