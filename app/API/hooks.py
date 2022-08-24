# -*- coding: utf-8 -*-
"""
    ************
    hooks.py
    ************


"""
__author__ = 'Bram Steenwinckel, Jonas Van Der Donckt'

from mattermostdriver import Driver


class AlertManager():
    def __init__(self):
        self.foo = Driver({
            'url': 'mattermost.ilabt.imec.be',
            'scheme': 'https',
            'port': False,
            # 'verify': True
        })
        # https://mattermost.com/blog/mattermost-integrations-incoming-webhooks/
        self.hook = "p1tp56ithiyy9kkfckrgukyzgh"

    def warning(self, module, warning_text,
                icon="http://icons.iconarchive.com/icons/google/noto-emoji-symbols/256/73028-warning-icon.png"):
        self.foo.webhooks.call_webhook(self.hook, options={"attachments": [{
            "fallback": "Warning",
            "color": "#FFF933",
            "pretext": "A warning message was generated for the following code:",
            "text": warning_text,
            "author_name": module,
            "author_icon": icon,
            "title": "Warning message",
        }]})

    def info(self, module, info_text,
                icon="https://icons.iconarchive.com/icons/graphicloads/100-flat-2/256/information-icon.png"):
        self.foo.webhooks.call_webhook(self.hook, options={"attachments": [{
            "fallback": "Info",
            "color": "#1167b1",
            "pretext": "A Info message message was generated for the following code:",
            "text": info_text,
            "author_name": module,
            "author_icon": icon,
            "title": "Info message",
        }]})

    def error(self, module, error_text, icon="https://www.iconsdb.com/icons/preview/red/error-xxl.png"):
        self.foo.webhooks.call_webhook(self.hook, options={"attachments": [{
            "fallback": "Error",
            "color": "#EA0000",
            "pretext": "An error was generated for the following code:",
            "text": error_text,
            "author_name": module,
            "author_icon": icon,
            "title": "Error message",
        }]})


a = AlertManager()