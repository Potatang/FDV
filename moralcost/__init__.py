from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'moral cost'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

    ADVISOR_ROLE = '推薦人'
    CLIENT_ROLE = '客戶'

    # Product A: 抽到 $2 的機率
    PRODUCT_A_SUCCESS_PROB = 0.6
    # Product B: 依據品質狀態決定抽到 $2 的機率
    PRODUCT_B_SUCCESS_PROB_H = 0.8
    PRODUCT_B_SUCCESS_PROB_L = 0.4
    # wage
    WAGE = 15
    # commission price
    COMMISSION = 5
    # 球的價值
    GOODBALL = 65
    BADBALL = 0   


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class MyPage(Page):
    pass


class ResultsWaitPage(WaitPage):
    pass


class Results(Page):
    pass


page_sequence = [MyPage, ResultsWaitPage, Results]
