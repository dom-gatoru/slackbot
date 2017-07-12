"""
Plugin Program
"""
from io import BytesIO
import requests
from PIL import Image
from slackbot.bot import listen_to
from plugins.restapi import RestApi
import slackbot_settings

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
            'channels': slackbot_settings.SLACK_CHANNEL
        }

        output = BytesIO()
        image_obj = Image.open(BytesIO(staticmap_api.response_data.content), 'r')
        image_obj.save(output, 'jpeg')
        requests.post(slackbot_settings.API_URL, data=slackapi_params, files={
            'file': ('weather.jpg', output.getvalue(), 'image/jpeg')
            })

    except Exception as other:
        message.send(''.join(other.args))
        return
