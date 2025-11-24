from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        # 說明頁（一定會顯示）
        yield Instruction4Page

        # 在第一次 yield 之後，再重新抓一次 self.player
        player = self.player

        # Case 1: showA = True → A 情境
        if player.showA:
            # 1A: 先 Incentive (AIPage) 再 Quality (AQPage)
            if player.show_ai_first:
                yield AIPage, dict(
                    belief_ai=50,   # 0–100 給個固定值就好
                )
                yield AQPage, dict(
                    belief_aq=60,
                )
            # 1B: 先 Quality (AQPage) 再 Incentive (AIPagecopy)
            else:
                yield AQPage, dict(
                    belief_aq=60,
                )
                yield AIPagecopy, dict(
                    belief_ai=50,
                )

        # Case 2: showA = False → B 情境
        else:
            # 2A: 先 Incentive (BIPage) 再 Quality (BQPage)
            if player.show_bi_first:
                yield BIPage, dict(
                    belief_bi=40,
                )
                yield BQPage, dict(
                    belief_bq=70,
                )
            # 2B: 先 Quality (BQPage) 再 Incentive (BIPagecopy)
            else:
                yield BQPage, dict(
                    belief_bq=70,
                )
                yield BIPagecopy, dict(
                    belief_bi=40,
                )

        # WaitPage 不用 yield，oTree 會自己處理
        yield Results
