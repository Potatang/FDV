from otree.api import *


doc = """
Belief of Quality: Assesses participants' ability to perform Bayesian updating.
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
    WAGE = 50
    # commission price
    COMMISSION = 15
    # 球的價值
    GOODBALL = 200
    BADBALL = 0

    # Ｂ的品質機率
    RED_LOW = 0.75
    BLUE_LOW = 0.33

class Subsession(BaseSubsession):
    ball_color = models.StringField(blank=True)      # "$200" or "$0"
    b_state_low = models.BooleanField()              # True=Low, False=High



class Group(BaseGroup):
    pass


class Player(BasePlayer):
    page_RED_first = models.BooleanField(initial = None)

    belief_qualityred = models.IntegerField(initial = None)
    belief_qualityblue = models.IntegerField(initial = None)

    red_payoff = models.CurrencyField(initial=0)
    blue_payoff = models.CurrencyField(initial=0)
    qualitypayoff = models.CurrencyField(initial=0)
    qualitypayoff_twd = models.CurrencyField(initial=0)

#FUNCTION
def creating_session(subsession: Subsession):
    import random

    # 每個人決定紅頁先或藍頁先（你原本的設計保留）
    for p in subsession.get_players():
        p.page_RED_first = random.choice([True, False])

    # 1) 先抽真實品質：50-50
    subsession.b_state_low = random.choice([True, False])  # True=Low, False=High

    # 2) 再依品質抽球：H=>0.8 得200；L=>0.4 得200
    prob_200 = C.PRODUCT_B_SUCCESS_PROB_L if subsession.b_state_low else C.PRODUCT_B_SUCCESS_PROB_H
    subsession.ball_color = "$200" if random.random() < prob_200 else "$0"


def set_payoffs(group: Group):
    import random
    from otree.api import cu

    PRIZE = cu(50)

    # 真實事件：B 是否為低品質（你要求先抽 state）
    event_low = group.subsession.b_state_low  # True 表示「低品質」真的發生

    def mpl_payoff_from_switch(b: int) -> 'Currency':
        """
        b: 0~100 的整數（例如 48），代表切換點在 40-50 且更精確為 48%
        規則：
        - 先抽 11 行之一：D ∈ {0,10,...,100}
        - 若抽中轉換那一行（上界十分位），再抽更精確 T ∈ {D-9,...,D}
        - 在任一被抽到的機率 x（D 或 T）下：
            若 b > x -> 選「預測」：事件(低品質)發生才得 PRIZE
            否則 -> 選「福袋」：以 x% 機率得 PRIZE
        """
        if b is None:
            return cu(0)
        b = int(b)

        # 抽 11 行
        D = random.choice(range(0, 101, 10))
        print(f"Debug MPL: b={b}, D={D}")

        # 找轉換行上界（例如 48 -> 50；50 -> 50）
        boundary = b if (b % 10 == 0) else (b // 10 + 1) * 10

        # 若抽到轉換行且 b 不是 10 的倍數，做 1% 細分
        if D == boundary and (b % 10 != 0):
            T = D - random.randint(0, 9)  # [D-9, D]
            x = T
        else:
            x = D

        # 用 x 決定預測/福袋
        if b > x:
            return PRIZE if event_low else cu(0)
        else:
            return PRIZE if (random.randint(1, 100) <= x) else cu(0)

    for p in group.get_players():
        # 你這個 app 只有一個真實 state，因此「預測」的事件就是同一個：低品質是否發生
        # 所以 red/blue 頁面其實都在問同一個事件，只是資訊呈現不同（如果你是這樣設計）
        # 因此 payoff 可以用其中一個 belief 或你指定要用哪個作為支付依據。

        # 如果你要「依照抽到的球色」來決定支付用哪個信念（你原本的邏輯）
        if group.subsession.ball_color == "$200":
            b_used = p.belief_qualityblue
        else:
            b_used = p.belief_qualityred

        p.qualitypayoff = mpl_payoff_from_switch(b_used)
        p.participant.qualitypayoff = p.qualitypayoff


# def set_payoffs(group: Group): 
#     import random  
#     for p in group.get_players():
#             p.red_payoff = cu(0)
#             stoobid = random.choice(range(0, 101, 1))
#             # print(stoobid)
#             if p.belief_qualityred > stoobid:
#                 if random.random() <= C.RED_LOW:
#                     p.red_payoff = cu(50)
#             else:
#                 import math
#                 if random.random() <= math.floor(stoobid / 10) / 10:
#                     p.red_payoff = cu(50)

#             p.blue_payoff = cu(0)
#             stoobid = random.choice(range(0, 101, 1))

#             if p.belief_qualityblue > stoobid:
#                 if random.random() <= C.BLUE_LOW:
#                         p.blue_payoff = cu(50)
#             else:
#                 import math
#                 if random.random() <= math.floor(stoobid / 10) / 10:
#                         p.blue_payoff = cu(50)

#             for p in group.get_players():
#                 if p.subsession.ball_color == "$200":
#                     p.qualitypayoff = p.blue_payoff
#                 else:
#                     p.qualitypayoff = p.red_payoff

#             p.participant.qualitypayoff = p.qualitypayoff

    

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
    title_text = "請稍候"
    body_text = "正在等待所有人做出預測，請耐心等候。"
    after_all_players_arrive = set_payoffs

class Results(Page):

    @staticmethod
    def vars_for_template(player:Player):
        subsession = player.subsession
        ball = player.subsession.ball_color
        if ball == "$200":
            image_path = 'blue_65.png'
        else:
            image_path = 'red_0.png'

        # 這個 app 的 qualitypayoff 視為「新台幣金額」
        # 若 qualitypayoff 是 oTree Currency/points，float() 可轉成數值
        qualitypayoff_twd = int(round(float(player.qualitypayoff)))

        # 存到 participant 的「台幣專用欄位」（建議不要覆蓋原本 participant.qualitypayoff）
        player.participant.qualitypayoff_twd = qualitypayoff_twd

        return dict(
            qualitypayoff_twd=player.participant.qualitypayoff_twd,
            ball_color=subsession.ball_color,
            image_path=image_path,
        )


page_sequence = [Instruction2Page, 
                 REDPage,
                 BLUEPage,
                 RED_copyPage,
                 ResultsWaitPage,
                 Results
                    ]
