from otree.api import *


doc = """
This is the second part of the experiment, which assesses participants' ability to perform Bayesian updating.
"""


class C(BaseConstants):
    NAME_IN_URL = 'guessquality_IF'
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

    # Ｂ的品質機率
    LOW = 0.75
    HIGH = 0.25

class Subsession(BaseSubsession):
    ball_color = models.StringField(blank=True)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    page_RED_first = models.BooleanField(initial = None)

    belief_qualityred = models.IntegerField(initial = None)
    belief_qualityblue = models.IntegerField(initial = None)

    red_payoff = models.CurrencyField(initial=0)
    blue_payoff = models.CurrencyField(initial=0)
    part2_payoff = models.CurrencyField(initial=0)

#FUNCTION
def creating_session(subsession:Subsession):
    import random
  
    for p in subsession.get_players():
        p.page_RED_first = random.choice([True, False])

    draw = random.random()  # 生成 0 到 1 的隨機數
    if draw < 0.5:
        subsession.ball_color = "$65"
    else:
        subsession.ball_color = "$0"


def set_payoffs(group: Group): 
    import random  
    for p in group.get_players():
        p.red_payoff = cu(0)
        stoobid = random.choice(range(0, 101, 1))
        # print(f'{stoobid=}')

        if p.belief_qualityred > stoobid:
            if random.random() <= C.LOW:
                p.red_payoff = cu(150)
        else:
            import math
            # print(f"{math.floor(stoobid / 10) / 10 = }")
            if random.random() <= math.floor(stoobid / 10) / 10:
                p.red_payoff = cu(150)

    for p in group.get_players():
        p.blue_payoff = cu(0)
        stoobid = random.choice(range(0, 101, 1))
        # print(f'{stoobid=}')

        if p.belief_qualityblue > stoobid:
            if random.random() <= C.LOW:
                p.blue_payoff = cu(150)
        else:
            import math
            # print(f"{math.floor(stoobid / 10) / 10 = }")
            if random.random() <= math.floor(stoobid / 10) / 10:
                p.blue_payoff = cu(150)

    if p.subsession.ball_color == "65":
        p.part2_payoff = p.blue_payoff
    else:
        p.part2_payoff = p.red_payoff

    p.participant.part2_payoff = p.part2_payoff

    

# PAGES
class Instruction2Page(Page):
    pass

class REDPage(Page):

    form_model = 'player'
    form_fields = ['belief_qualityred']
    
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_path1='productB.png',
            image_path2='red_0.png',
        )
    
    @staticmethod
    def is_displayed(player):
        return player.page_RED_first
    
class BLUEPage(Page):

    form_model = 'player'
    form_fields = ['belief_qualityblue']
    
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_path1='productB.png',
            image_path2='blue_65.png',
        )
    
class RED_copyPage(Page):

    form_model = 'player'
    form_fields = ['belief_qualityred']
    
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_path1='productB.png',
            image_path2='red_0.png',
        )

    @staticmethod
    def is_displayed(player):
        return not player.page_RED_first

class ResultsWaitPage(WaitPage):    
    after_all_players_arrive = set_payoffs

class Results(Page):

    @staticmethod
    def vars_for_template(player:Player):
        subsession = player.subsession
        ball = player.subsession.ball_color
        if ball == "$65":
            image_path = 'blue_65.png'
        else:
            image_path = 'red_0.png'
        player.participant.part2_payoff = player.part2_payoff

        
        return dict(part2_payoff = player.participant.part2_payoff,
                    ball_color=subsession.ball_color,
                    image_path=image_path
                    )


page_sequence = [Instruction2Page, 
                 REDPage,
                 BLUEPage,
                 RED_copyPage,
                 ResultsWaitPage,
                 Results
                    ]
