

import requests

class tg_bot():
    """
    Class for telegram bot , send messages

    """
    from .my_pass import tg_token, chat_id
    def __init__(self,message = None):
        self.message = message

    def tg_sender(self,*args):
                print("<<< Start tgbot.py >>>")
                try:
                    url = f"https://api.telegram.org/bot{self.tg_token}/sendMessage?chat_id={self.chat_id}&text={self.message}"
                    requests.get(url).json()
                except ValueError:
                    print("Error send message")
                return print(f"send message <'{self.message}'> is succesfull")


if __name__ == '__main__':
        sender = tg_bot("hi")
        sender.tg_sender()




