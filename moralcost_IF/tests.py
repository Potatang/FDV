from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):

        if self.round_number == 1:
            yield InstructionPage

            yield ComprehensionCheck, dict(
                question1='D',
                question2='B',
                question3='A',
                question4='A',
                question5='A',
            )

            yield RecommendationPage, dict(
                recommendation1='X',
                recommendation2='Y',
                recommendation3='X',
                recommendation4='Y',
                recommendation5='X',
            )
