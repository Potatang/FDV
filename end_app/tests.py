from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        # 先進入第一頁（只是顯示說明）
        yield BeforeResultPage

        # 最後一頁只是在顯示總報酬，沒有按鈕也沒關係，
        # 但是要跟 oTree 說「不用檢查 HTML 裡有沒有 submit button」
        yield Submission(ResultPage, {}, check_html=False)
