"""JTS Study Meeting Slack Bot Program."""
# coding: utf-8

from slackbot.bot import Bot

def main():
    """
    Slackbot
    """
    print("main() start")
    bot = Bot()
    bot.run()
    print("main() end")

if __name__ == '__main__':
    print("if文")
    main()
