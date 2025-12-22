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
        # 1) 加總 points（你目前是用 participant.*_payoff 存）
        total_points = (
            player.participant.experiment_payoff
            + player.participant.choice_payoff
            + player.participant.qualitypayoff
            + player.participant.moralpayoff
        )
        player.total_payoff = total_points
        player.participant.total_payoff = total_points

        # 2) who 決定匯率
        #    假設 who==1 是 advisor、who==0 是 client（依你現在的設計）
        if player.participant.who == 1:
            points_per_ntd = player.session.config['advisor_points_per_ntd']  # 2
            role = 'advisor'
        else:
            points_per_ntd = player.session.config['client_points_per_ntd']   # 4
            role = 'client'

        # 3) points -> NTD，再加 participation fee
        participation_fee = player.session.config['participation_fee']  # 250
        twd_payoff = round(float(total_points) / points_per_ntd) + participation_fee

        player.twd_payoff = twd_payoff
        player.participant.twd_payoff = twd_payoff

        return dict(
            role=role,
            points_per_ntd=points_per_ntd,
            experiment_payoff=player.participant.experiment_payoff,
            qualitypayoff=player.participant.qualitypayoff,
            choice_payoff=player.participant.choice_payoff,
            moralpayoff=player.participant.moralpayoff,
            total_payoff=player.participant.total_payoff,
            twd_payoff=player.participant.twd_payoff,
        )
    
# class ResultPage(Page):
#     form_model = 'player'

#     @staticmethod
#     def vars_for_template(player):
#         player.total_payoff = player.participant.experiment_payoff + player.participant.qualitypayoff + player.participant.choice_payoff + player.participant.moralpayoff
#         player.twd_payoff = round(float(player.total_payoff) / 5) + 250
#         player.participant.total_payoff = player.total_payoff
#         player.participant.twd_payoff = player.twd_payoff

        
#         return dict(experiment_payoff=player.participant.experiment_payoff,
#                     qualitypayoff=player.participant.qualitypayoff,
#                     choice_payoff=player.participant.choice_payoff,
#                     moralpayoff=player.participant.moralpayoff,
#                     total_payoff=player.participant.total_payoff,
#                     twd_payoff=player.participant.twd_payoff,
#                     )


page_sequence = [BeforeResultPage,
                 ResultPage]
