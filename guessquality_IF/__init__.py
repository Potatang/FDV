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

    WAGE = 50
    COMMISSION = 15
    GOODBALL = 200
    BADBALL = 0

    # B 的品質機率
    RED_LOW = 0.75
    BLUE_LOW = 0.33


class Subsession(BaseSubsession):
    ball_color = models.StringField(blank=True)      # "$200" or "$0"
    b_state_low = models.BooleanField()              # True=Low, False=High


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    belief_qualityred = models.IntegerField(initial=None)
    belief_qualityblue = models.IntegerField(initial=None)

    red_payoff = models.CurrencyField(initial=0)
    blue_payoff = models.CurrencyField(initial=0)
    qualitypayoff = models.CurrencyField(initial=0)
    qualitypayoff_twd = models.CurrencyField(initial=0)

    # 結果頁顯示用
    selected_row = models.IntegerField(initial=None)
    selected_row_index = models.IntegerField(initial=None)
    selected_action = models.StringField(blank=True)
    selected_belief = models.IntegerField(initial=None)
    payoff_source = models.StringField(blank=True)


# FUNCTIONS
def creating_session(subsession: Subsession):
    import random

    # 先抽真實品質：50-50
    subsession.b_state_low = random.choice([True, False])  # True=Low, False=High

    # 再依品質抽球：H=>0.8 得200；L=>0.4 得200
    prob_200 = C.PRODUCT_B_SUCCESS_PROB_L if subsession.b_state_low else C.PRODUCT_B_SUCCESS_PROB_H
    subsession.ball_color = "$200" if random.random() < prob_200 else "$0"

def set_payoffs(group: Group):
    import random
    from otree.api import cu

    PRIZE = cu(50)
    event_low = group.subsession.b_state_low  # True 表示低品質真的發生

    def mpl_payoff_from_switch(b: int):
        """
        回傳:
        {
            'payoff': cu(...),
            'selected_row': D,            # 主表該列對應的百分比，例如 80
            'selected_row_index': k,      # 主表第幾行，例如 9
            'action': 'prediction' or 'lottery',
            'belief': b,
        }
        """
        if b is None:
            return {
                'payoff': cu(0),
                'selected_row': None,
                'selected_row_index': None,
                'action': '',
                'belief': None,
            }

        b = int(b)

        # 先抽主表中的一列：0,10,...,100
        D = random.choice(range(0, 101, 10))

        # 主表第幾行
        # 0% = 第1行, 10% = 第2行, ..., 100% = 第11行
        row_index = D // 10 + 1

        # 找轉換行上界，例如 48 -> 50；50 -> 50
        boundary = b if (b % 10 == 0) else (b // 10 + 1) * 10

        # 若抽到轉換行且 b 不是 10 的倍數，做 1% 細分
        if D == boundary and (b % 10 != 0):
            T = D - random.randint(0, 9)   # 例如 D=50，則 T in [41,50]
            x = T
        else:
            x = D

        if b > x:
            action = 'prediction'
            payoff = PRIZE if event_low else cu(0)
        else:
            action = 'lottery'
            payoff = PRIZE if (random.randint(1, 100) <= x) else cu(0)

        return {
            'payoff': payoff,
            'selected_row': D,
            'selected_row_index': row_index,
            'action': action,
            'belief': b,
        }

    for p in group.get_players():
        # 依照抽到的球色決定用哪個 belief 來支付
        if group.subsession.ball_color == "$200":
            b_used = p.belief_qualityblue
            p.payoff_source = "blue"
        else:
            b_used = p.belief_qualityred
            p.payoff_source = "red"

        result = mpl_payoff_from_switch(b_used)

        p.qualitypayoff = result['payoff']
        p.selected_row = result['selected_row']
        p.selected_row_index = result['selected_row_index']
        p.selected_action = result['action']
        p.selected_belief = result['belief']

        p.participant.qualitypayoff = p.qualitypayoff

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


class BLUEPage(Page):
    form_model = 'player'
    form_fields = ['belief_qualityblue']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_path1='productB.png',
            image_path2='blue_65.png',
        )


class ResultsWaitPage(WaitPage):
    title_text = "請稍候"
    body_text = "正在等待所有人做出預測，請耐心等候。"
    after_all_players_arrive = set_payoffs

class Results(Page):
    @staticmethod
    def vars_for_template(player: Player):
        subsession = player.subsession
        ball = subsession.ball_color

        if ball == "$200":
            image_path = 'blue_65.png'
        else:
            image_path = 'red_0.png'

        qualitypayoff_twd = int(round(float(player.qualitypayoff)))
        player.participant.qualitypayoff_twd = qualitypayoff_twd

        return dict(
            qualitypayoff_twd=player.participant.qualitypayoff_twd,
            ball_color=subsession.ball_color,
            image_path=image_path,
            selected_row=player.field_maybe_none('selected_row'),
            selected_row_index=player.field_maybe_none('selected_row_index'),
            selected_action=player.field_maybe_none('selected_action'),
            selected_belief=player.field_maybe_none('selected_belief'),
            payoff_source=player.field_maybe_none('payoff_source'),
        )

class FinalWaitPage(WaitPage):
    wait_for_all_groups = True
    title_text = "請稍候"
    body_text = "正在等待所有人完成本部分。"

page_sequence = [
    Instruction2Page,
    REDPage,
    BLUEPage,
    ResultsWaitPage,
    Results,
    FinalWaitPage
]