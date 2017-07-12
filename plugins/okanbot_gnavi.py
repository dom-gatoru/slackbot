"""
Plugin Program
"""
from requests.exceptions import RequestException
from slackbot.bot import listen_to
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
