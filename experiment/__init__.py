from otree.api import *
import random

doc = """
Advisor-Client Recommendation Experiment
SEE INCENTIVE FIRST
在本實驗中，20位受試者中10位為advisor，10位為client。
每回合advisor依據產品B的品質訊息與附加的佣金訊息決定推薦A或B，
client看到advisor推薦後，直接選擇商品A或B，
最終支付則依據每回合抽球結果決定，並且所有50回合都會計入最終報酬。
"""

#Models
class C(BaseConstants):
    NAME_IN_URL = 'experiment'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 5

    ADVISOR_ROLE = 'advisor'
    CLIENT_ROLE = 'client'

    #車馬費
    PARTICIPATION_FEE = 250
    # Product A: 抽到 $2 的機率
    PRODUCT_A_SUCCESS_PROB = 0.6
    # Product B: 依據品質狀態決定抽到 $2 的機率
    PRODUCT_B_SUCCESS_PROB_H = 0.8
    PRODUCT_B_SUCCESS_PROB_L = 0.4
    # commission price
    COMMISSION = 10
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
    round_payoff = models.CurrencyField(initial=0)

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
    
    # 取得該組中兩位玩家
    advisor = group.get_player_by_role(C.ADVISOR_ROLE)
    client = group.get_player_by_role(C.CLIENT_ROLE)
    
    # ---------------------------
    # Advisor 報酬計算：
    # 固定： participation_fee + $15
    # 額外：若 advisor 推薦的商品與 subsession.commission_product 相符，再加 $5
    # ---------------------------
    advisor_payoff = C.PARTICIPATION_FEE + 15
    if group.recommendation == subsession.commission_product:
        advisor_payoff += 5
    advisor.round_payoff = cu(advisor_payoff)
    
    # ---------------------------
    # Client 報酬計算：
    # 固定： participation_fee
    # 額外：根據所選產品抽球決定
    # 產品 A：60% 機率得到 $65
    # 產品 B：若品質為 '低品質' 40% 機率得到 $65；若品質為 '高品質' 80% 機率得到 $65
    # ---------------------------
    client_payoff = C.PARTICIPATION_FEE
    rnd = random.random()  # 0～1 的隨機數
    if group.selection == 'A':
        if rnd < 0.6:
            client_payoff += 65
    elif group.selection == 'B':
        if subsession.product_b_quality == '低品質':
            if rnd < 0.4:
                client_payoff += 65
        elif subsession.product_b_quality == '高品質':
            if rnd < 0.8:
                client_payoff += 65
    client.round_payoff = cu(client_payoff)

# def set_payoffs(group: Group):
#     subsession = group.subsession
#     # 取得該回合電腦隨機決定的變數
#     commission_product = subsession.commission_product  # 例如 "產品A" 或 "產品B"
#     product_b_quality = subsession.product_b_quality    # 例如 "高品質" 或 "低品質"
    
#     # 取得組內兩位玩家
#     advisor = None
#     client = None
#     for p in group.get_players():
#         if p.role == C.ADVISOR_ROLE:
#             advisor = p
#         elif p.role == C.CLIENT_ROLE:
#             client = p
    
#     # 設定推薦人的報酬
#     if advisor:
#         # 轉換 advisor 的推薦 ( 'A' 對應 "產品A"， 'B' 對應 "產品B" )
#         if (group.recommendation == 'A' and commission_product == '產品A') or \
#            (group.recommendation == 'B' and commission_product == '產品B'):
#             advisor.payoff = cu(C.COMMISSION)
#         else:
#             advisor.payoff = cu(0)
    
#     # 設定客戶的報酬
#     if client:
#         if group.selection == 'A':
#             # 若選擇產品A：60% 機率獲得 GOODBALL（$65）
#             client.payoff = cu(C.GOODBALL) if random.random() < 0.6 else cu(C.BADBALL)
#         elif group.selection == 'B':
#             if product_b_quality == '低品質':
#                 # 產品B低品質：40% 機率獲得 GOODBALL
#                 client.payoff = cu(C.GOODBALL) if random.random() < 0.4 else cu(C.BADBALL)
#             elif product_b_quality == '高品質':
#                 # 產品B高品質：80% 機率獲得 GOODBALL
#                 client.payoff = cu(C.GOODBALL) if random.random() < 0.8 else cu(C.BADBALL)
#             else:
#                 # 如果產品B品質未設定，預設為 $0
#                 client.payoff = cu(C.BADBALL)


#Pages
class AdvisorPage(Page):
    form_model = 'player'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            player_in_previous_rounds=player.in_previous_rounds(),
            # commission_product=player.subsession.commission_product,
            # product_b_quality=player.subsession.product_b_quality
            ) 
    
    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE       
    
class ClientPage(Page):
    form_model = 'player'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            player_in_previous_rounds=player.in_previous_rounds(),
            # commission_product=player.subsession.commission_product,
            # product_b_quality=player.subsession.product_b_quality
            ) 
    
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
        return dict(commission_product=subsession.commission_product)

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
        return dict(recommendation=group.recommendation)
    
class WaitforClient(WaitPage):
    pass

class HistoryPage(Page):
    @staticmethod
    def vars_for_template(player: Player):
        rounds_data = []
        # 只取已完成的回合資料（in_previous_rounds 不包含當前回合）
        for p in player.in_previous_rounds():
            group = p.group
            rounds_data.append({
                'round_number': p.round_number,
                'commission_product': p.subsession.commission_product,
                'product_b_quality': p.subsession.product_b_quality,
                'quality_signal': p.subsession.quality_signal,
                'recommendation': group.recommendation,
                'selection': group.selection,
                'round_payoff': p.round_payoff,
            })
        return dict(rounds_data=rounds_data)

class ShuffleWaitPage(WaitPage):
    wait_for_all_groups = True

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        subsession.group_randomly(fixed_id_in_group=True)

#PageSequence
page_sequence = [
    AdvisorPage,
    ClientPage,
    IncentivePage,
    QualityPage,
    RecommendationPage,
    WaitforAdvisor,
    SelectionPage,
    WaitforClient,
    HistoryPage,
    ShuffleWaitPage,
]