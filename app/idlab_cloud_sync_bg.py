# -*- coding: utf-8 -*-
"""
    ****************
    idlab_cloud_sync_bg.py
    ****************
    
    Created at 25/11/20        
"""
__author__ = 'Jonas Van Der Donckt'

import os
import time
import traceback
import shutil
from pathlib import Path

from API.hooks import a
from API.offload_data import RcloneNextcloudSync
from config import AppConfig
import threading


def sync_all_folders(interval_time_s: int = 60 * 60 * 2):
    while 1:
        t_start = time.time()
        try:
            a.info(module='offloader', info_text='trying to sync collected in background thread')
            sync = RcloneNextcloudSync(remote='idlab', remote_root_path='/speech_web_app/backup',
                                       rclone_conf_path=AppConfig.RCLONE_CONF_PATH.value, debug=False)

            # iterate over all the folders in the data dir
            folder: Path
            for folder in sorted(AppConfig.DATA_SAVE_DIR.value.iterdir(), key=os.path.getmtime, reverse=True):
                if folder.is_dir():
                    print(folder.name)
                    if not sync.check_synchronized(local_folder=folder, destination=folder.name):
                        print(f'syncing: {str(folder)}', flush=True)
                        sync.copy_to_remote(local_folder=folder, destination=folder.name)
                        sync_check = sync.check_synchronized(local_folder=folder, destination=folder.name)
                        if sync_check:
                            a.info(module='offloader', info_text=f'synchronized: {folder.name}')
                            shutil.rmtree(folder)
                        else:
                            print(f"coud not synchronize {folder.name}")
                            a.warning(module='offloader', warning_text=f'could not synchronize {folder.name}')
                    else:
                        print(f'already synced: {folder.name}')
        except:
            a.error(module='offloader', error_text=traceback.format_exc())
        t_end = time.time()
        diff_secs = t_end - t_start
        sleep_time_s = max(0, interval_time_s - int(diff_secs))
        a.info(module='offloader', info_text=f'finished data offload in {diff_secs // 3600}h{diff_secs // 60 % 60}min\n'
                                             f' will sleep  for {sleep_time_s // 3600}h{(sleep_time_s // 60) % 60}min')
        time.sleep(sleep_time_s)


if __name__ == '__main__':
    if not os.path.exists(AppConfig.DATA_SAVE_DIR.value):
        os.makedirs(AppConfig.DATA_SAVE_DIR.value)

    a.info(module='offloader', info_text='running prestart script')
    t = threading.Thread(target=sync_all_folders, kwargs=dict(interval_time_s=AppConfig.SYNC_INTERVAL_S.value))
    t.start()
