from otree.api import *
import random

doc = """
Advisor-Client Recommendation Experiment
SEE INCENTIVE FIRST
在本實驗中，20位受試者中10位為advisor，10位為client。
每回合advisor依據產品B的品質訊息與附加的佣金訊息決定推薦A或B，
client看到advisor推薦後，直接選擇商品A或B，
最終支付則依據每回合抽球結果決定，但只有從50回合中隨機抽取的10回合會計入最終報酬。
"""

#Models

class C(BaseConstants):
    NAME_IN_URL = 'experiment'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 5

    ADVISOR_ROLE = 'advisor'
    CLIENT_ROLE = 'client'

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
    commission_product = models.StringField()
    product_b_quality = models.StringField()
    
    # def before_round_start(self):
    #     import random
    #     # 每回合重新抽取 commission_product 與 product_b_quality
    #     self.commission_product = random.choice(['產品A', '產品B'])
    #     self.product_b_quality = random.choice(['高品質', '低品質'])

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
    pass

#FUNCTION
def creating_session(subsession: Subsession):
    session = subsession.session
    import random
    #隨機決定支付回合
    if subsession.round_number == 1:
        paying_round = random.sample(range(1, C.NUM_ROUNDS + 1), 2)
        session.vars['paying_round'] = paying_round
    #每回合重新分組
    subsession.group_randomly(fixed_id_in_group=True)
    # 50-50 決定哪一個商品能獲得佣金
    commission_product = random.choice(['產品A', '產品B'])
    subsession.commission_product = commission_product
    # 50-50 決定 product B 的品質：high 或 low
    product_b_quality = random.choice(['高品質', '低品質'])
    subsession.product_b_quality = product_b_quality
    # B是低品質有40%抽中好球 B是高品質有80%抽中好球



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


class RecommendationPage(Page):

    form_model = 'group'
    form_fields = ['recommendation']

    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE
    
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

# class HistoryPage(Page):
#     pass
    
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
    RecommendationPage,
    WaitforAdvisor,
    SelectionPage,
    # HistoryPage,
    ShuffleWaitPage,
]