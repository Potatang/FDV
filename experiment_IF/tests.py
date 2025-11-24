from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):

        # --- Instr. & comprehension ---
        if self.round_number == 1:
            yield InstructionPage2
            yield ComprehensionCheck, dict(
                question1='B',
                question2='B',
                question3='A',
                question4='C',
                question5='A',
            )
            if self.player.role == C.ADVISOR_ROLE:
                yield AdvisorPage
            else:
                yield ClientPage

        if self.round_number == 11:
            yield InstructionPage3

        # --- Main decisions ---

        if self.player.role == C.ADVISOR_ROLE:
            # info-order pages（is_displayed 會自己判斷）
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