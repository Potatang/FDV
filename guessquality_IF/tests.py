from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):

        # 先走說明頁
        yield Instruction2Page

        # 根據 page_RED_first 決定順序
        if self.player.page_RED_first:
            # 情況 1：先紅後藍
            yield REDPage, dict(
                belief_qualityred=50,   # 給一個合理的數字 0–100
            )
            yield BLUEPage, dict(
                belief_qualityblue=50,
            )
        else:
            # 情況 2：先藍後紅(copy)
            yield BLUEPage, dict(
                belief_qualityblue=50,
            )
            yield RED_copyPage, dict(
                belief_qualityred=50,
            )

        # WaitPage 不用 yield，oTree 會自己處理
        yield Results
