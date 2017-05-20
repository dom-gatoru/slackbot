"""
REST API CLASS
"""
# -*- coding: utf-8 -*-
import requests
from requests.exceptions import RequestException

class RestApi():
    """
    REST API CLASS
    """
    def __init__(self, url, key):
        self.url = url
        self.key = key
        self.response_data = None

    def api_request(self, search_dict):
        """
        API呼び出し
        """
        try:
            search_dict['keyid'] = self.key
            self.response_data = requests.get(self.url, params=search_dict)
        except RequestException:
            raise Exception('APIアクセスに失敗しました')
