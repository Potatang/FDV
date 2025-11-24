from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):

        # --- instructions & comprehension only in round 1 ---
        if self.round_number == 1:
            yield InstructionPage
            yield ComprehensionCheck, dict(
                question1='A',
                question2='C',
                question3='C',
            )
            if self.player.role == C.ADVISOR_ROLE:
                yield AdvisorPage
            else:
                yield ClientPage

        # --- decisions ---

        if self.player.role == C.ADVISOR_ROLE:
            # 卡片排列：四張都選 Quality，避免兩紅兩黑 & Blank
            yield ChoicePage, dict(
                choice_1='Quality',
                choice_2='Quality',
                choice_3='Quality',
                choice_4='Quality',
                left_changed=0,   # 左邊沒改色
                right_changed=1,  # 右邊有改色
            )

            # information order pages
            treatment = self.player.treatment_this_round()
            if treatment == 'IF':
                yield IncentivePage1
                yield QualityPage1
            elif treatment == 'QF':
                yield QualityPage2
                yield IncentivePage2

            # recommendation
            yield RecommendationPage, dict(
                recommendation='A',
            )

        else:
            # client strategy method
            yield SelectionPage, dict(
                selection_if_A='A',
                selection_if_B='A',
            )
        yield HistoryPage