from otree.api import Bot
from . import (
    C,
    AdvisorPage,
    ClientPage,
    DicePage,
    AdvisordrawPage,
    ProductPage,
    ClientdrawPage,
    RevealPage,
)


class PlayerBot(Bot):
    def play_round(self):
        # MyWaitPage, WaitforAdvisor, WaitforClient, ResultsWaitPage, ShuffleWaitPage
        # 都是 WaitPage，不用 yield

        # 這裡直接用 self.player，不要先存成 player 再跨 yield 用
        if self.player.role == C.ADVISOR_ROLE:
            # 推薦人流程：AdvisorPage → DicePage → AdvisordrawPage
            yield AdvisorPage

            # 隨便給一個骰子結果（True=正面, False=反面）
            yield DicePage, dict(advisor_dice=True)

            yield AdvisordrawPage

        else:
            # 客戶流程：ClientPage → ProductPage → ClientdrawPage
            yield ClientPage
            yield ProductPage
            yield ClientdrawPage

        # 最後一回合才會看到 RevealPage
        # 注意：這裡用 self.round_number，不要用 self.player.round_number
        if self.round_number == C.NUM_ROUNDS:
            yield RevealPage
