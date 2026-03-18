from otree.api import *


doc = """
This is the fourth part of the experiment, which test participants whether they feel difference between two treatment, see incentive first or see quality first.
"""


class C(BaseConstants):
    NAME_IN_URL = 'guessproportion_IF'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    ADVISOR_ROLE = '推薦人'
    CLIENT_ROLE = '客戶'

    # Product A: 抽到 $2 的機率
    PRODUCT_A_SUCCESS_PROB = 0.6
    # Product B: 依據品質狀態決定抽到 $2 的機率
    PRODUCT_B_SUCCESS_PROB_H = 0.8
    PRODUCT_B_SUCCESS_PROB_L = 0.4

    WAGE = 50
    COMMISSION = 15
    GOODBALL = 200
    BADBALL = 0

    # probability of recommendation the incentivized product
    A_IF = 0.4
    A_QF = 0.6
    B_IF = 0.4
    B_QF = 0.6


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    belief_ai = models.IntegerField(initial=None)
    belief_bi = models.IntegerField(initial=None)
    belief_aq = models.IntegerField(initial=None)
    belief_bq = models.IntegerField(initial=None)


# PAGES
class Instruction4Page(Page):
    pass


class AIPage(Page):
    form_model = 'player'
    form_fields = ['belief_ai']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_path1='productB.png',
            image_path2='blue_65.png',
        )


class BIPage(Page):
    form_model = 'player'
    form_fields = ['belief_bi']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_path1='productB.png',
            image_path2='red_0.png',
        )


class AQPage(Page):
    form_model = 'player'
    form_fields = ['belief_aq']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_path1='productB.png',
            image_path2='blue_65.png',
        )


class BQPage(Page):
    form_model = 'player'
    form_fields = ['belief_bq']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_path1='productB.png',
            image_path2='red_0.png',
        )


class ResultsWaitPage(WaitPage):
    wait_for_all_groups = True
    body_text = "請稍候，正在等待所有人完成本部分。"


page_sequence = [
    Instruction4Page,
    AIPage,
    BIPage,
    AQPage,
    BQPage,
    ResultsWaitPage,
]