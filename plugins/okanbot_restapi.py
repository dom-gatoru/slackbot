"""
Plugin Program
"""
from io import BytesIO
import requests
from requests.exceptions import RequestException
from PIL import Image
from slackbot.bot import listen_to
from plugins.restapi import RestApi
from plugins.gnaviapi import GnaviApi
import slackbot_settings

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

@listen_to('雨')
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

    geocoder_api = RestApi(url_geocoder)
    staticmap_api = RestApi(url_staticmap)

    search_word = message.body['text'].split()

    try:
        if len(search_word) < 2:
            raise Exception('なんかキーワード足りない？(´・ω・｀)')

        geocoder_api_params = {
            'appid': key_yahoo,
            'query': search_word[1],
            'output': 'json'
        }
        geocoder_api.api_request(geocoder_api_params)
        geocoder_json = geocoder_api.response_data.json()
        if 'Error' in geocoder_json:
            raise Exception('その場所知らない・・・(´・ω・｀)')
        print(geocoder_json)
        coordinates = (((geocoder_json['Feature'])[0])['Geometry'])['Coordinates']

        staticmap_api_params = {
            'appid': key_yahoo,
            'lon': (coordinates.split(','))[0],
            'lat': (coordinates.split(','))[1],
            'overlay': 'type:rainfall',
            'output': 'jpg',
            'z': '13'
        }
        staticmap_api.api_request(staticmap_api_params)

        slackapi_params = {
            'token': slackbot_settings.API_TOKEN,
            'channels': 'C5CJE5YBA'
        }

        image_obj = Image.open(BytesIO(staticmap_api.response_data.content), 'r')
        image_obj.save('/tmp/weather.jpg')
        with open('/tmp/weather.jpg', 'rb') as weatherfile:
            requests.post(url_slackapi, data=slackapi_params, files={
                'file': ('weather.jpg', weatherfile, 'image/jpeg')})

    except Exception as other:
        message.send(''.join(other.args))
        return

@listen_to('世界地図')
def search_places(message):
    """
    受信メッセージを元にGoogle Places APIから緯度経度を取得する。
    緯度経度を中心に元にスタティックマップAPIから雨雲レーダーの画像を返す。
    場所：住所(query)
    """
    url_places = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
    key_places = 'AIzaSyBPxh9zt6piucgIM9kk_mfZLDR_60AHKpo-'

    #url_slackapi = 'https://slack.com/api/files.upload'

    places_api = RestApi(url_places)

    search_word = message.body['text'].split()

    try:
        if len(search_word) < 2:
            raise Exception('なんかキーワード足りない？(´・ω・｀)')

        places_api_params = {
            'query': '+'.join(search_word[1:]),
            'key': key_places
        }

        places_api.api_request(places_api_params)

        places_json = places_api.response_data.json()
        if 'status' in places_json:
            raise Exception('ダメっぽい・・・(´・ω・｀)')
        print(places_json)

    except Exception as other:
        message.send(''.join(other.args))
        return
