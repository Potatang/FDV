from otree.api import Bot
from . import *


class PlayerBot(Bot):
    def play_round(self):
        seat = self.player.id_in_subsession
        is_advisor = (seat % 2 == 1)

        yield ComputerPage, dict(
            seat=seat,
            who=is_advisor,
        )
