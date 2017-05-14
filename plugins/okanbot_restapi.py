"""
Plugin Program
"""
from requests.exceptions import RequestException
from slackbot.bot import listen_to
from plugins.gnaviapi import GnaviApi

@listen_to('ご飯')
def search_restraunt(message):
    """
        受信メッセージを元にぐるなびを検索してURLを返す
    """
    gnavi = GnaviApi('https://api.gnavi.co.jp/RestSearchAPI/20150630/')
    key = '18692ae7852ec7131e8cb8bed64e5519'

    search_word = message.body['text'].split()

    if len(search_word) == 3:
        params = {
            'keyid': key,
            'format': 'json',
            'address': search_word[1],
            'freeword': search_word[2]
        }
        try:
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
