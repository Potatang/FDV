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
        # 1) points 的部分：只加總「其他 app」的 points（不包含 quality 這個台幣 app）
        total_points = (
            player.participant.experiment_payoff
            + player.participant.choice_payoff
            + player.participant.moralpayoff
        )
        player.total_payoff = total_points
        player.participant.total_payoff = total_points

        # 2) who 決定匯率（用 bool() 兼容 True/False 或 1/0）
        if bool(player.participant.who):
            points_per_ntd = player.session.config['advisor_points_per_ntd']  # 2
            role = 'advisor'
        else:
            points_per_ntd = player.session.config['client_points_per_ntd']   # 4
            role = 'client'

        # 3) 先把 points -> 台幣，再加 participation fee
        participation_fee = player.session.config['participation_fee']  # 250
        twd_from_points = round(float(total_points) / points_per_ntd)

        # 4) 加上 quality app 的「台幣」金額（若沒跑到該 app 就當 0）
        qualitypayoff_twd = int(player.participant.vars.get('qualitypayoff_twd', 0))

        twd_payoff = twd_from_points + qualitypayoff_twd + participation_fee

        player.twd_payoff = twd_payoff
        player.participant.twd_payoff = twd_payoff

        return dict(
            role=role,
            points_per_ntd=points_per_ntd,
            experiment_payoff=player.participant.experiment_payoff,
            choice_payoff=player.participant.choice_payoff,
            moralpayoff=player.participant.moralpayoff,
            total_payoff=player.participant.total_payoff,
            qualitypayoff_twd=qualitypayoff_twd,
            twd_payoff=player.participant.twd_payoff,
        )

    

page_sequence = [BeforeResultPage,
                 ResultPage]
