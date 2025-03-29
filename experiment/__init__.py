from otree.api import *
import random

doc = """
Advisor-Client Recommendation Experiment
SEE INCENTIVE FIRST
在本實驗中，20 位受試者中 10 位為 advisor，10 位為 client。
每回合 advisor 依據產品 B 的品質訊息與附加的佣金訊息決定推薦 A 或 B，
client 看到 advisor 推薦後，直接選擇商品 A 或 B，
最終支付則依據每回合抽球結果決定，並且所有 50 回合都會計入最終報酬。
"""

#Models
class C(BaseConstants):
    NAME_IN_URL = 'experiment'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 5

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
    commission_product = models.StringField(blank=True)
    product_b_quality = models.StringField(blank=True)
    product_b_good_ball_probability = models.FloatField(blank=True)
    quality_signal = models.StringField(blank=True)

class Group(BaseGroup):
    recommendation = models.StringField(
        choices=[['A', '產品A'], ['B', '產品B']],
        widget=widgets.RadioSelect,
        label="我推薦：",
    )
    selection = models.StringField(
        choices=[['A', '產品A'], ['B', '產品B']],
        widget=widgets.RadioSelect,
        label="我選擇：",
    )

class Player(BasePlayer):
    advisor_recommendation = models.StringField(blank=True)
    client_selection = models.StringField(blank=True)
    round_payoff = models.CurrencyField(initial=0)
    seat = models.IntegerField(label='請輸入座位電腦號碼', min=1, max=34)

#FUNCTION
def creating_session(subsession: Subsession):
    import random

    #每回合重新分組
    subsession.group_randomly(fixed_id_in_group=True)

    # 50-50 決定哪一個商品能獲得佣金
    commission_product = random.choice(['產品A', '產品B'])
    subsession.commission_product = commission_product

    # 50-50 決定 product B 的品質：high 或 low
    product_b_quality = random.choice(['高品質', '低品質'])
    subsession.product_b_quality = product_b_quality

    # 根據產品B的品質設定抽中好球的機率：
    # 低品質：40% 機率抽中好球；高品質：80% 機率抽中好球
    if product_b_quality == '低品質':
        subsession.product_b_good_ball_probability = 0.4
    else:
        subsession.product_b_good_ball_probability = 0.8

    # 進行抽球，根據設定的機率決定抽中好球("$2")還是壞球("$0")
    draw = random.random()  # 生成 0 到 1 的隨機數
    if draw < subsession.product_b_good_ball_probability:
        subsession.quality_signal = "$2"
    else:
        subsession.quality_signal = "$0"
        
def set_payoffs(group: Group):
    subsession = group.subsession
    # session = group.session

    # p1 = group.get_player_by_id(1)
    # p2 = group.get_player_by_id(2)

    # p1.advisor_recommendation = p1.group.recommendation
    # p1.client_selection = p1.group.selection
    # p2.advisor_recommendation = p2.group.recommendation
    # p2.client_selection = p2.group.selection
    
    for p in group.get_players():
        p.advisor_recommendation = p.group.recommendation
        p.client_selection = p.group.selection
        if p.role == C.ADVISOR_ROLE:
            # Advisor 固定報酬 $15
            payoff = C.WAGE
            # 若 advisor 的推薦與當回合電腦決定的佣金產品相符，額外加 $5
            if p.advisor_recommendation == subsession.commission_product.replace("產品", ""):
                payoff += C.COMMISSION
        elif p.role == C.CLIENT_ROLE:
            # Client 固定報酬為參與費
            payoff = 0
            rnd = random.random()  # 生成 0～1 的隨機數
            if p.client_selection == 'A':
                # 產品 A：60% 機率得到 $65
                if rnd <= 0.6:
                    payoff += C.GOODBALL
            elif p.client_selection == 'B':
                # 產品 B：根據產品 B 的品質決定
                if subsession.product_b_quality == '低品質':
                    if rnd <= 0.4:
                        payoff += C.GOODBALL
                elif subsession.product_b_quality == '高品質':
                    if rnd <= 0.8:
                        payoff += C.GOODBALL

            # print(f"{rnd = }")
        # 記錄當回合報酬（轉換為 Currency 型態）
        p.round_payoff = cu(payoff)


#Pages
class ComputerPage(Page):
    form_model = 'player'
    form_fields = ['seat']

class AdvisorPage(Page):
    form_model = 'player'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(player_in_previous_rounds=player.in_previous_rounds()) 
    
    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE       
    
class ClientPage(Page):
    form_model = 'player'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(player_in_previous_rounds=player.in_previous_rounds()) 
    
    @staticmethod
    def is_displayed(player):
        return player.role == C.CLIENT_ROLE    
    
class IncentivePage(Page):

    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE
    
    @staticmethod
    def vars_for_template(player: Player):
        subsession = player.subsession
        return dict(commission_product=subsession.commission_product)

class QualityPage(Page):

    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE
    
    @staticmethod
    def vars_for_template(player: Player):
        subsession = player.subsession
        return dict(
            quality_signal=subsession.quality_signal,
            product_b_good_ball_probability=subsession.product_b_good_ball_probability)

class RecommendationPage(Page):

    form_model = 'group'
    form_fields = ['recommendation']

    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE
    
    @staticmethod
    def vars_for_template(player: Player):
        subsession = player.subsession
        
        previous_decision_record = {
            (p.round_number, p.id_in_group): {
                "round_number": p.round_number,
                "id_in_group": p.id_in_group,
                "advisor_recommendation": p.advisor_recommendation,
                "client_selection": p.client_selection,
                "commission_product": p.subsession.commission_product,
                "product_b_quality": p.subsession.product_b_quality,
                "round_payoff": p.round_payoff,
            }
            for p in player.in_previous_rounds()
        }
        
        return dict(commission_product=subsession.commission_product, previous_decision_record=previous_decision_record)

class WaitforAdvisor(WaitPage):
    pass

class SelectionPage(Page):

    form_model = 'group'
    form_fields = ['selection']
    
    @staticmethod
    def is_displayed(player):
        return player.role == C.CLIENT_ROLE

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        previous_decision_record = {
            (p.round_number, p.id_in_group): {
                "round_number": p.round_number,
                "id_in_group": p.id_in_group,
                "advisor_recommendation": p.advisor_recommendation,
                "client_selection": p.client_selection,
                "commission_product": p.subsession.commission_product,
                "product_b_quality": p.subsession.product_b_quality,
                "round_payoff": p.round_payoff,
            }
            for p in player.in_previous_rounds()
        }

        return dict(recommendation=group.recommendation, previous_decision_record=previous_decision_record)
    
class WaitforClient(WaitPage):
    pass

class ResultsWaitPage(WaitPage):    
    after_all_players_arrive = set_payoffs

class HistoryPage(Page):
    @staticmethod
    def vars_for_template(player: Player):
        # player.advisor_recommendation = player.group.recommendation
        # player.client_selection = player.group.selection

        # print(f"{player = }")
        # print(f"{player.in_all_rounds() = }")

        decision_record = {
            (p.round_number, p.id_in_group): {
                "round_number": p.round_number,
                "id_in_group": p.id_in_group,
                "advisor_recommendation": p.advisor_recommendation,
                "client_selection": p.client_selection,
                "commission_product": p.subsession.commission_product,
                "product_b_quality": p.subsession.product_b_quality,
                "round_payoff": p.round_payoff,
            }
            for p in player.in_all_rounds()
        }
        # print(decision_record)

        return dict(decision_record=decision_record)

class ShuffleWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        subsession.group_randomly(fixed_id_in_group=True)

#PageSequence
page_sequence = [
    ComputerPage,
    AdvisorPage,
    ClientPage,
    IncentivePage,
    QualityPage,
    RecommendationPage,
    WaitforAdvisor,
    SelectionPage,
    WaitforClient,
    ResultsWaitPage,
    HistoryPage,
    ShuffleWaitPage,
]