"""
plugin test
"""
from slackbot.bot import respond_to
from slackbot.bot import listen_to

@respond_to('腹減った')
@respond_to('お腹すいた')
@respond_to('お腹ペッコリーニ')
def gohan(message):
    """
    decoraterの引数にマッチするメッセージを受信すると
    """
    message.reply('ご飯作るかい？')

@listen_to('まだ')
@listen_to('諦める')
def sendo(message):
    """
    仙道さん！
    """
    message.send('まだ慌てるような時間じゃない。')

@listen_to('いいか')
def reaction(message):
    """
    いいね！
    """
    message.react('+1')
