"""
Plugin Program
"""
from io import StringIO
import requests
from requests.exceptions import RequestException
from PIL import Image
from slackbot.bot import listen_to
from plugins.restapi import RestApi
from plugins.gnaviapi import GnaviApi

@listen_to('ご飯')
@listen_to('お店')
def search_restraunt(message):
    """
    受信メッセージを元にぐるなびを検索してURLを返す。
    場所：エリアMマスタコード(areacode_m) or 住所(address)
    キーワード：フリーワード(freeword) or 店舗名(name)
    """
    url = 'https://api.gnavi.co.jp/RestSearchAPI/20150630/'
    key = '18692ae7852ec7131e8cb8bed64e5519'

    gnavi = GnaviApi(url, key)

    search_word = message.body['text'].split()

    if len(search_word) >= 3:
        try:
            params = gnavi.create_params(search_word)

            gnavi.garea_middle_fech()
            search_area = gnavi.garea_middle_search(search_word[1])
            if len(search_area) == 0:
                search_area = {'address': search_word[1]}

            params.update(search_area)
            gnavi.api_request(params)

            for rest_url in gnavi.url_list():
                message.send(rest_url)
        except RequestException:
            message.send('ぐるなびに繋がんなかったから、後でまた探してくれ・・・( ´Д`)y━･~~')
            return
        except Exception as other:
            message.send(''.join(other.args))
            return
    else:
        message.send('↓こんな感じで検索してほしい・・・(￣Д￣)ﾉ')
        message.send('ご飯　場所　キーワード（文字はスペース区切り）')
        message.send('例）ご飯　品川　焼き鳥')

@listen_to('天気')
def search_weather(message):
    """
    受信メッセージを元にジオコーダAPIから緯度経度を取得する。
    緯度経度を中心に元にスタティックマップAPIから雨雲レーダーの画像を返す。
    場所：住所(query)
    """
    url_geocoder = 'https://map.yahooapis.jp/geocode/V1/geoCoder'
    url_staticmap = 'https://map.yahooapis.jp/map/V1/static'
    key_yahoo = 'dj0zaiZpPXJFMENYVGNCV1VtdCZzPWNvbnN1bWVyc2VjcmV0Jng9OTc-'

    url_slackapi = 'https://slack.com/api/files.upload'
    key_slackbot = 'xoxb-149014797505-Z1LUJAnUOYTUuB44ekZxaLx5'

    geocoder_api = RestApi(url_geocoder)
    staticmap_api = RestApi(url_staticmap)

    search_word = message.body['text'].split()

    try:
        geocoder_api_params = {
            'appid': key_yahoo,
            'query': search_word[1],
            'output': 'json'
        }
        geocoder_api.api_request(geocoder_api_params)
        geocoder_json = geocoder_api.response_data.json()
        if 'Error' in geocoder_json:
            raise Exception('その場所知らない・・・(´・ω・｀)')
        coordinates = (((geocoder_json['Feature'])[0])['Geometry'])['Coordinates']

        staticmap_api_params = {
            'appid': key_yahoo,
            'lat': (coordinates.split(','))[0],
            'lon': (coordinates.split(','))[1],
            'overlay': 'type:rainfall'
        }
        staticmap_api.api_request(staticmap_api_params)

        slackapi_params = {
            'token': key_slackbot,
            'channels': 'C5CJE5YBA'
        }
        print(StringIO(staticmap_api.response_data.content))
        requests.post(
            url_slackapi, params=slackapi_params,
            files={'file': Image.open(StringIO(staticmap_api.response_data.content))})
        print('requestは投げた')
        #message.send(staticmap_api.response_data.apparent_encoding())
    except Exception as other:
        message.send(''.join(other.args))
        return

