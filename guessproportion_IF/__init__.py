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
    # wage
    WAGE = 15
    # commission price
    COMMISSION = 5
    # 球的價值
    GOODBALL = 65
    BADBALL = 0  

    # probability of recommendation the "right" product, i.e. best advice for client, from the last experiment (two treatment).
    A_IF = 0.4
    A_QF = 0.6
    B_IF = 0.4
    B_QF = 0.6


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    showA = models.BooleanField(initial = None)
    show_ai_first = models.BooleanField(initial = None)
    show_bi_first = models.BooleanField(initial = None)

    belief_ai = models.IntegerField(initial = None)
    belief_aq = models.IntegerField(initial = None)
    belief_bi = models.IntegerField(initial = None)   
    belief_bq = models.IntegerField(initial = None)

    ai_payoff = models.CurrencyField(initial=0)
    aq_payoff = models.CurrencyField(initial=0)
    bi_payoff = models.CurrencyField(initial=0)
    bq_payoff = models.CurrencyField(initial=0)
    part4_payoff = models.CurrencyField(initial=0)

def creating_session(subsession:Subsession):
    import random
  
    for p in subsession.get_players():
        p.showA = random.choice([True, False])
        p.show_ai_first = random.choice([True, False])
        p.show_bi_first = random.choice([True, False])

# def set_payoffs(group: Group): 
#     import random  
#     for p in group.get_players():
#         p.ai_payoff = cu(0)
#         stoobid = random.choice(range(0, 101, 1))
#         # print(f'{stoobid=}')

#         if p.belief_ai > stoobid:
#             if random.random() <= C.LOW:
#                 p.ai_payoff = cu(150)
#         else:
#             import math
#             # print(f"{math.floor(stoobid / 10) / 10 = }")
#             if random.random() <= math.floor(stoobid / 10) / 10:
#                 p.ai_payoff = cu(150)

#     for p in group.get_players():
#         p.aq_payoff = cu(0)
#         stoobid = random.choice(range(0, 101, 1))
#         # print(f'{stoobid=}')

#         if p.belief_aq > stoobid:
#             if random.random() <= C.LOW:
#                 p.aq_payoff = cu(150)
#         else:
#             import math
#             # print(f"{math.floor(stoobid / 10) / 10 = }")
#             if random.random() <= math.floor(stoobid / 10) / 10:
#                 p.aq_payoff = cu(150)

#     for p in group.get_players():
#         p.bi_payoff = cu(0)
#         stoobid = random.choice(range(0, 101, 1))
#         # print(f'{stoobid=}')

#         if p.belief_bi > stoobid:
#             if random.random() <= C.LOW:
#                 p.bi_payoff = cu(150)
#         else:
#             import math
#             # print(f"{math.floor(stoobid / 10) / 10 = }")
#             if random.random() <= math.floor(stoobid / 10) / 10:
#                 p.bi_payoff = cu(150)

#     for p in group.get_players():
#         p.bq_payoff = cu(0)
#         stoobid = random.choice(range(0, 101, 1))
#         # print(f'{stoobid=}')

#         if p.belief_bq > stoobid:
#             if random.random() <= C.LOW:
#                 p.bq_payoff = cu(150)
#         else:
#             import math
#             # print(f"{math.floor(stoobid / 10) / 10 = }")
#             if random.random() <= math.floor(stoobid / 10) / 10:
#                 p.bq_payoff = cu(150)

#     if p.subsession.ball_color == "65":
#         p.part2_payoff = p.blue_payoff
#     else:
#         p.part2_payoff = p.red_payoff

#     p.participant.part2_payoff = p.part2_payoff

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
            image_path2='red_0.png',
        )
    
    @staticmethod
    def is_displayed(player):
        return player.showA and player.show_ai_first

class AQPage(Page):

    form_model = 'player'
    form_fields = ['belief_aq']
    
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_path1='productB.png',
            image_path2='red_0.png',
        )
    
    @staticmethod
    def is_displayed(player):
        return player.showA 

class AIPagecopy(Page):

    form_model = 'player'
    form_fields = ['belief_ai']
    
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_path1='productB.png',
            image_path2='red_0.png',
        )
    
    @staticmethod
    def is_displayed(player):
        return player.showA and not player.show_ai_first
    
class BIPage(Page):

    form_model = 'player'
    form_fields = ['belief_bi']
    
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_path1='productB.png',
            image_path2='blue_65.png',
        )
    
    @staticmethod
    def is_displayed(player):
        return player.show_bi_first and not player.showA

class BQPage(Page):

    form_model = 'player'
    form_fields = ['belief_bq']
    
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_path1='productB.png',
            image_path2='blue_65.png',
        )
    
    @staticmethod
    def is_displayed(player):
        return not player.showA 

class BIPagecopy(Page):

    form_model = 'player'
    form_fields = ['belief_bi']
    
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_path1='productB.png',
            image_path2='blue_65.png',
        )
    
    @staticmethod
    def is_displayed(player):
        return not player.showA and player.show_bi_first
    
# class ResultsWaitPage(WaitPage):    
#     after_all_players_arrive = set_payoffs

class Results(Page):
    pass


page_sequence = [Instruction4Page,
                AIPage,
                AQPage,
                AIPagecopy,
                BIPage,
                BQPage,
                BIPagecopy,
                Results]
