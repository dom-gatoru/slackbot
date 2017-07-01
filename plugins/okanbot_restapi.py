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
    gnavi = GnaviApi(slackbot_settings.GNAVI_RESTSERACH_URL, slackbot_settings.GNAVI_API_TOKEN)

    search_word = message.body['text'].split()

    if len(search_word) >= 3:
        try:
            params = {
                'format': 'json'
            }
            if search_word[0] == 'ご飯':
                params['freeword'] = search_word[2]

            elif search_word[0] == 'お店':
                params['name'] = search_word[2]

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
    geocoder_api = RestApi(slackbot_settings.YAHOO_GEOCODER_URL)
    staticmap_api = RestApi(slackbot_settings.YAHOO_STATICMAP_URL)

    search_word = message.body['text'].split()

    try:
        if len(search_word) < 2:
            raise Exception('なんかキーワード足りない？(´・ω・｀)')

        geocoder_api_params = {
            'appid': slackbot_settings.YAHOO_API_TOKEN,
            'query': search_word[1],
            'output': 'json'
        }
        geocoder_api.api_request(geocoder_api_params)
        geocoder_json = geocoder_api.response_data.json()
        if 'Error' in geocoder_json:
            raise Exception('その場所知らない・・・(´・ω・｀)')

        coordinates = (((geocoder_json['Feature'])[0])['Geometry'])['Coordinates']

        staticmap_api_params = {
            'appid': slackbot_settings.YAHOO_API_TOKEN,
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

        output = BytesIO()
        image_obj = Image.open(BytesIO(staticmap_api.response_data.content), 'r')
        image_obj.save(output, 'jpeg')
        requests.post(slackbot_settings.API_URL, data=slackapi_params, files={
            'file': ('weather.jpg', output.getvalue(), 'image/jpeg')
            })

        #image_obj = Image.open(BytesIO(staticmap_api.response_data.content), 'r')
        #image_obj.save('/tmp/weather.jpg')
        #with open('/tmp/weather.jpg', 'rb') as weatherfile:
        #    requests.post(slackbot_settings.API_URL, data=slackapi_params, files={
        #        'file': ('weather.jpg', weatherfile, 'image/jpeg')})

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
    places_api = RestApi(slackbot_settings.GOOGLE_PLACES_URL)
    staticmap_api = RestApi(slackbot_settings.YAHOO_STATICMAP_URL)

    search_word = message.body['text'].split()

    try:
        if len(search_word) < 2:
            raise Exception('なんかキーワード足りない？(´・ω・｀)')

        places_api_params = {
            'query': '+'.join(search_word[1:]),
            'key': slackbot_settings.GOOGLE_API_TOKEN
        }
        places_api.api_request(places_api_params)

        places_json = places_api.response_data.json()

        if places_json['status'] != 'OK':
            raise Exception('なんか見つかんなかった(´・ω・｀)')

        staticmap_api_params = {
            'appid': slackbot_settings.YAHOO_API_TOKEN,
            'lat': ((places_json['results'])[0])['geometry']['location']['lat'],
            'lon': ((places_json['results'])[0])['geometry']['location']['lng'],
            'output': 'jpg',
            'z': '13'
        }
        staticmap_api.api_request(staticmap_api_params)

        slackapi_params = {
            'token': slackbot_settings.API_TOKEN,
            'channels': 'C5CJE5YBA'
        }

        image_obj = Image.open(BytesIO(staticmap_api.response_data.content), 'r')
        image_obj.save('/tmp/worldmap.jpg')

        with open('/tmp/worldmap.jpg', 'rb') as weatherfile:
            requests.post(slackbot_settings.API_URL, data=slackapi_params, files={
                'file': ('worldmap.jpg', weatherfile, 'image/jpeg')})

    except Exception as other:
        message.send(''.join(other.args))
        return
