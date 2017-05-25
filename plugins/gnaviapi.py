"""
ぐるなびAPI
"""
# -*- coding: utf-8 -*-
from requests.exceptions import RequestException
from plugins.restapi import RestApi

class GnaviApi(RestApi):
    """
    ぐるなびAPI用クラス
    """
    def __init__(self, url, key):
        super().__init__(url)
        self.key = key
        self.garea_s = None

    def create_params(self, search_word):
        """
        Slackで入力されたキーワードにより、APIのパラメータを変える。
        """
        params = {
            'format': 'json'
        }

        if search_word[0] == 'ご飯':
            params['freeword'] = search_word[2]

        elif search_word[0] == 'お店':
            params['name'] = search_word[2]

        return params

    def url_list(self):
        """
        ResponseからレストランURLのリストを作って返す。
        """
        json_data = self.response_data.json()
        if 'error' in json_data:
            raise Exception('そのキーワードじゃ見つかんなかった・・・(´・ω・｀)')

        if json_data['total_hit_count'] == '1':
            return [(json_data['rest'])['url']]
        else:
            return [rest_data['url'] for rest_data in json_data['rest']]

    def garea_middle_fech(self):
        """
        ぐるなびAPIからエリアMマスタを取得する。
        """
        garea = RestApi('https://api.gnavi.co.jp/master/GAreaMiddleSearchAPI/20150630/')
        params = {
            'keyid': self.key,
            'format': 'json',
            'lang': 'ja'
        }
        try:
            garea.api_request(params)
            self.garea_s = garea.response_data.json()
            if 'error' in self.garea_s:
                raise Exception('その場所知らない・・・(´・ω・｀)')
        except RequestException:
            raise RequestException()

    def garea_middle_search(self, area_name):
        """
        エリアMマスタ内から、area_nameに一致する値を取得する。
        （完全一致だと厳しいので、部分一致。）
        """
        result_dict = {}
        for area_s in self.garea_s['garea_middle']:
            if area_s['areaname_m'].find(area_name) >= 0:
                result_dict = {'areacode_m': area_s['areacode_m']}
                break

        return result_dict
