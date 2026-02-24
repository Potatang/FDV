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

    # Demographics
    gender = models.StringField(
        label="請問您的生理性別為?",
        choices=[("Male", "男性"), ("Female", "女性"), ("Other", "不便透露")],
        widget=widgets.RadioSelect
    )
    age = models.IntegerField(label="請問您的年齡為?", min=10, max=120)
    ethnicity = models.LongStringField(label="請問您的族裔為?")

    # Difficulty / feedback
    difficulty = models.StringField(
        label="您在理解實驗說明時是否遇到困難?",
        choices=[("Yes", "有"), ("No", "沒有")],
        widget=widgets.RadioSelect
    )
    unclear = models.LongStringField(label="如果有，請問哪裡不清楚?", blank=True)
    comments = models.LongStringField(label="請在此留下任何意見或建議（可選填）。", blank=True)

    difference = models.StringField(
        label="在本場實驗抽球的過程中，請問您對於\"參加者親自抽取\"與\"電腦代抽\"這兩者是否有差別？",
        choices=[("有差別", "有差別"), ("沒有差別", "沒有差別")],
        widget=widgets.RadioSelect
    )
    difference_reason = models.LongStringField(
        label="請簡單說明您認為兩者有／沒有差別的主要原因或考量是什麼？"
    )

    # Role-specific questions
    advisor_decision_rule = models.LongStringField(
        label="當您必須在產品 A 和產品 B 之間做出選擇時，您是如何決定要推薦哪一個的？"
    )

    advisor_decision_reason = models.LongStringField(
        label="請簡單說明您做出上述推薦決策的主要原因／考量是什麼？"
    )

    client_follow_advice = models.StringField(
        label="整體而言您是否會按照收到的推薦進行選擇？",
        choices=[("會", "會"), ("不會", "不會")],
        widget=widgets.RadioSelect
    )

    client_follow_reason = models.LongStringField(
        label="請簡單說明您是否會按照推薦選擇的主要原因／考量是什麼？"
    )

# PAGES
class BeforeResultPage(Page):
    pass

class ResultPage(Page):
    form_model = 'player'
    @staticmethod
    def is_displayed(player):
        return player.participant.seat < 99
    
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
            points_per_ntd = player.session.config['advisor_points_per_ntd']  # 6
            role = 'advisor'
        else:
            points_per_ntd = player.session.config['client_points_per_ntd']   # 12
            role = 'client'

        # 3) 先把 points -> 台幣，再加 participation fee
        participation_fee = player.session.config['participation_fee']  # 250
        twd_from_points = round(float(total_points) / points_per_ntd)

        # 4) 加上 quality app 的「台幣」金額（若沒跑到該 app 就當 0）
        qualitypayoff_twd = int(player.participant.vars.get('qualitypayoff_twd', 0))

        twd_payoff = twd_from_points + qualitypayoff_twd + participation_fee

        player.twd_payoff = twd_payoff
        player.participant.twd_payoff = twd_payoff

        # 固定使用同一個 Qualtrics 連結（不分 treatment）
        qualtrics_url = (
            "https://tassel.syd1.qualtrics.com/jfe/form/SV_0lENJGFC0hpxcB8"
            f"?label={player.participant.seat}&payoff={player.participant.twd_payoff}"
        )

        return dict(
            role=role,
            points_per_ntd=points_per_ntd,
            experiment_payoff=player.participant.experiment_payoff,
            choice_payoff=player.participant.choice_payoff,
            moralpayoff=player.participant.moralpayoff,
            total_payoff=player.participant.total_payoff,
            qualitypayoff_twd=qualitypayoff_twd,
            twd_payoff=player.participant.twd_payoff,
            qualtrics_url=qualtrics_url,        # 建議 template 用這個
        )

class DemographicsPage(Page):
    form_model = 'player'

    @staticmethod
    def is_displayed(player):
        return player.participant.seat < 99

    @staticmethod
    def get_form_fields(player):
        role = 'advisor' if bool(player.participant.who) else 'client'
        base = ['gender', 'age', 'ethnicity', 'difficulty', 'unclear', 'comments', 'difference', 'difference_reason']

        if role == 'advisor':
            base += ['advisor_decision_rule', 'advisor_decision_reason']
        else:
            base += ['client_follow_advice', 'client_follow_reason']

        return base

    @staticmethod
    def vars_for_template(player):
        role = 'advisor' if bool(player.participant.who) else 'client'
        return dict(role=role)

    
class OutPage(Page):
    @staticmethod
    def is_displayed(player):
        return player.participant.seat == 99

page_sequence = [BeforeResultPage,
                 DemographicsPage,
                 ResultPage,                 
                 OutPage]
