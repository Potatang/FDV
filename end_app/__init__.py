from otree.api import *


doc = """
For those not shown up, send them to here.
"""


class C(BaseConstants):
    NAME_IN_URL = 'end_app'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    total_payoff = models.CurrencyField(initial=0)
    twd_payoff = models.CurrencyField(initial=0)


# PAGES
class BeforeResultPage(Page):
    pass

class ResultPage(Page):
    form_model = 'player'

    @staticmethod
    def vars_for_template(player):
        player.total_payoff = player.participant.experiment_payoff + player.participant.qualitypayoff + player.participant.choice_payoff + player.participant.moralpayoff
        player.twd_payoff = round(float(player.total_payoff) / 5) + 250
        player.participant.total_payoff = player.total_payoff
        player.participant.twd_payoff = player.twd_payoff

        
        return dict(experiment_payoff=player.participant.experiment_payoff,
                    qualitypayoff=player.participant.qualitypayoff,
                    choice_payoff=player.participant.choice_payoff,
                    moralpayoff=player.participant.moralpayoff,
                    total_payoff=player.participant.total_payoff,
                    twd_payoff=player.participant.twd_payoff,
                    )


page_sequence = [BeforeResultPage,
                 ResultPage]
