from otree.api import *
import random


doc = """
Advisor-Client Recommendation Experiment
Choice experiment
在本實驗中，20 位受試者中 10 位為 advisor，10 位為 client。
每回合 advisor 依據產品 B 的品質訊息與附加的佣金訊息決定推薦 A 或 B，
client 看到 advisor 推薦後，直接選擇商品 A 或 B，
最終支付則依據每回合抽球結果決定，並且所有 10 回合都會計入最終報酬。
"""

#Models
class C(BaseConstants):
    NAME_IN_URL = 'choice'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 10

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
    # 全選 Quality 或全選 Incentive 的扣除額
    CHOICE_DECUCTION = 5

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
    # 看起來沒用到
    # advisor_preference = models.StringField(blank=True)
    client_selection = models.StringField(blank=True)
    round_payoff = models.CurrencyField(initial=0)
    roundsum_payoff = models.CurrencyField(initial=0)
    partner_payoff = models.CurrencyField(initial=0)

    choice_1 = models.StringField(choices=['Quality','Incentive'], initial='Quality')
    choice_2 = models.StringField(choices=['Quality','Incentive'], initial='Quality')
    choice_3 = models.StringField(choices=['Quality','Incentive'], initial='Incentive')
    choice_4 = models.StringField(choices=['Quality','Incentive'], initial='Incentive')

    def treatment_this_round(self):
        # o = self.participant.vars.get('order')
        # if o is None:
        #     # This participant is not an advisor (or not assigned). Decide how to handle:
        #     return None
        # if self.round_number <= 10:
        #     return 'IF' if o == 1 else 'QF'
        # else:
        #     return 'QF' if o == 1 else 'IF'

        choices = [self.choice_1, self.choice_2, self.choice_3, self.choice_4]
        chosen_choice = random.choice(choices)

        if chosen_choice == 'Quality':
            return 'QF'
        elif chosen_choice == 'Incentive':
            return 'IF'

    
#FUNCTION
# note: this function goes at the module level, not inside the WaitPage.
def group_by_arrival_time_method(subsession, waiting_players):
    print('in group_by_arrival_time_method')

    # print(f"{waiting_players = }")
    
    # for p in waiting_players:
    #     print(f"{p.participant.who = }")
    #     if p.participant.who == True: p.role == C.ADVISOR_ROLE
    #     else: p.role == C.CLIENT_ROLE

    a_players = [p for p in waiting_players if p.participant.who == True]
    c_players = [p for p in waiting_players if p.participant.who == False]

    if len(a_players) >= 1 and len(c_players) >= 1:
        return [random.choice(a_players), random.choice(c_players)]
    

def creating_session(subsession: Subsession):
    import random

    if subsession.round_number == 1:
        for p in subsession.get_players():
            # 給每個 participant 都一個獨立的 order（若已存在就不覆寫）
            p.participant.vars.setdefault('order', random.randint(0, 1))
            print(f"[order-assign] PID={p.participant.id_in_session} order={p.participant.vars['order']}")
            
        # # optionally propagate to clients (if they need it)
        # for c in [p for p in g.get_players() if not is_advisor(p)]:
        #     # tie client to their group's advisor order (pick the first advisor in the group)
        #     c.participant.vars['advisor_order'] = advisors[0].participant.vars['order']

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
        subsession.quality_signal = "$65"
    else:
        subsession.quality_signal = "$0"
        
def set_payoffs(group: Group):
    subsession = group.subsession
    
    for p in group.get_players():
        p.advisor_recommendation = p.group.recommendation
        p.client_selection = p.group.selection
        if p.role == C.ADVISOR_ROLE:
            # Advisor 固定報酬 $15
            payoff = C.WAGE
            # 若 advisor 的推薦與當回合電腦決定的佣金產品相符，額外加 $5
            if p.advisor_recommendation == subsession.commission_product.replace("產品", ""):
                payoff += C.COMMISSION
            
            # 如果都是 Quality 或都是 Incentive，扣 $5
            choices = set([p.choice_1, p.choice_2, p.choice_3, p.choice_4])
            if len(choices) == 1:
                # print(f"set_payoff: all the same choice! deducting {C.CHOICE_DECUCTION}")
                payoff -= C.CHOICE_DECUCTION
            
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

        # Compute cumulative (round sum) payoff.
        if p.round_number == 1:
            p.roundsum_payoff = p.round_payoff
        else:
            previous_round = p.in_round(p.round_number - 1)
            p.roundsum_payoff = previous_round.roundsum_payoff + p.round_payoff
        
        p.participant.experiment_payoff = p.roundsum_payoff

    for p in group.get_players():
        partner = p.get_others_in_group()[0] if p.get_others_in_group() else None
        p.partner_payoff = partner.round_payoff if partner else None


#Pages
    
class MyWaitPage(WaitPage):
    group_by_arrival_time = True
    title_text = "請稍候"
    body_text = "正在等待其他參加者進入實驗，請耐心等候。"

    
class AdvisorPage(Page):
    form_model = 'player'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(player_in_previous_rounds=player.in_previous_rounds()) 
    
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.role == C.ADVISOR_ROLE

    
class ClientPage(Page):
    form_model = 'player'

    @staticmethod
    def vars_for_template(player: Player):
        return dict(player_in_previous_rounds=player.in_previous_rounds()) 
    
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1 and player.role == C.CLIENT_ROLE

    
class ChoicePage(Page):
    form_model = 'player'
    form_fields = ['choice_1','choice_2','choice_3','choice_4']

    @staticmethod
    def vars_for_template(player: Player):
        choices = dict(choice_1='Quality', choice_2='Quality',
                       choice_3='Incentive', choice_4='Incentive')
        if player.round_number == 1:
            current_sum = 0
        else:
            current_sum = player.in_round(player.round_number - 1).roundsum_payoff
        return dict(choices=choices,
                    current_sum=current_sum
                )
    
    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE


class IncentivePage1(Page):

    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE and player.treatment_this_round() == 'IF'
    
    @staticmethod
    def vars_for_template(player: Player):
        subsession = player.subsession
        return dict(commission_product=subsession.commission_product)

class QualityPage1(Page):

    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE and player.treatment_this_round() == 'IF'
    
    @staticmethod
    def vars_for_template(player: Player):
        subsession = player.subsession
        quality = player.subsession.quality_signal
        if quality == "$65":
            image_path = 'blue_65.png'
        else:
            image_path = 'red_0.png'

        return dict(
            quality_signal=subsession.quality_signal,
            product_b_good_ball_probability=subsession.product_b_good_ball_probability,
            image_path=image_path)

class QualityPage2(Page):

    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE and player.treatment_this_round() == 'QF'
    
    @staticmethod
    def vars_for_template(player: Player):
        subsession = player.subsession
        quality = player.subsession.quality_signal
        if quality == "$65":
            image_path = 'blue_65.png'
        else:
            image_path = 'red_0.png'

        return dict(
            quality_signal=subsession.quality_signal,
            product_b_good_ball_probability=subsession.product_b_good_ball_probability,
            image_path=image_path)

class IncentivePage2(Page):

    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE and player.treatment_this_round() == 'QF'
    
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
                "quality_signal": p.subsession.quality_signal,
                "round_payoff": p.round_payoff,
                "roundsum_payoff": p.roundsum_payoff,
                "quality_image": 'ProductB_high.png' if p.subsession.product_b_quality == "高品質" else 'ProductB_low.png',
                "signal_image": 'blue_65.png' if p.subsession.quality_signal == "$65" else 'red_0.png',
                "producta_image": 'ProductA.png',
                "partner_payoff": p.partner_payoff,
            }
            for p in player.in_previous_rounds()
        }
        
        return dict(commission_product=subsession.commission_product,
                    previous_decision_record=previous_decision_record,
                    )

class WaitforAdvisor(WaitPage):
    title_text = "請稍候"
    body_text = "正在等待推薦人做出推薦，請耐心等候。"

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
                "quality_signal": p.subsession.quality_signal,
                "round_payoff": p.round_payoff,
                "roundsum_payoff": p.roundsum_payoff,
                "quality_image": 'ProductB_high.png' if p.subsession.product_b_quality == "高品質" else 'ProductB_low.png',
                "signal_image": 'blue_65.png' if p.subsession.quality_signal == "$65" else 'red_0.png',
                "producta_image": 'ProductA.png',
                "partner_payoff": p.partner_payoff,
            }
            for p in player.in_previous_rounds()
        }

        return dict(recommendation=group.recommendation, 
                    previous_decision_record=previous_decision_record,
                    )
    
class WaitforClient(WaitPage):
    title_text = "請稍候"
    body_text = "正在等待客戶做出選擇，請耐心等候。"

class ResultsWaitPage(WaitPage):    
    after_all_players_arrive = set_payoffs

class HistoryPage(Page):
    
    # def before_next_page(player: Player):
    #     import time
    #     player.round_duration = time.time() - player.round_start_time

    @staticmethod
    def vars_for_template(player: Player):

        decision_record = {
            (p.round_number, p.id_in_group): {
                "round_number": p.round_number,
                "id_in_group": p.id_in_group,
                "advisor_recommendation": p.advisor_recommendation,
                "client_selection": p.client_selection,
                "commission_product": p.subsession.commission_product,
                "product_b_quality": p.subsession.product_b_quality,
                "quality_signal": p.subsession.quality_signal,
                "round_payoff": p.round_payoff,
                "roundsum_payoff": p.roundsum_payoff,
                "quality_image": 'ProductB_high.png' if p.subsession.product_b_quality == "高品質" else 'ProductB_low.png',
                "signal_image": 'blue_65.png' if p.subsession.quality_signal == "$65" else 'red_0.png',
                "producta_image": 'ProductA.png',
                "partner_payoff": p.partner_payoff,
            }
            for p in player.in_all_rounds()
        }
        # print(decision_record)        

        return dict(decision_record=decision_record)
    

    
class ShuffleWaitPage(WaitPage):
    wait_for_all_groups = True
    title_text = "請稍候"
    body_text = "正在等待所有人準備完成，請耐心等候其他參與者。"



#PageSequence
page_sequence = [
    MyWaitPage,
    AdvisorPage,
    ClientPage,
    ChoicePage,
    IncentivePage1,
    QualityPage1,
    QualityPage2,
    IncentivePage2,
    RecommendationPage,
    WaitforAdvisor,
    SelectionPage,
    WaitforClient,
    ResultsWaitPage,
    HistoryPage,
    ShuffleWaitPage,
]