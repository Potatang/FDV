from otree.api import *
import random
import time

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
    NAME_IN_URL = 'experiment_IF'
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
    roundsum_payoff = models.CurrencyField(initial=0)
    # seat = models.IntegerField(blank = False, label='請輸入座位電腦號碼', min=1, max=34)
    partner_payoff = models.CurrencyField(initial=0)

    question1 = models.StringField(
        label='1. 產品A中有多少顆藍色的球？',
        choices=[
            ('A', '(A) 2顆'),
            ('B', '(B) 3顆'),
            ('C', '(C) 4顆'),
        ],
        widget=widgets.RadioSelect
    )

    question2 = models.StringField(
        label='2. 產品B可能是高品質的機率為何？',
        choices=[
            ('A', '(A) 25%'),
            ('B', '(B) 50%'),
            ('C', '(C) 75%'),
        ],
        widget=widgets.RadioSelect
    )

    question3 = models.StringField(
        label='3. 假設電腦從客戶選擇的產品中抽到紅色球，請問他的報酬為多少？',
        choices=[
            ('A', '(A) $0'),
            ('B', '(B) $5'),
            ('C', '(C) $15'),
            ('D', '(D) $65'),
        ],
        widget=widgets.RadioSelect
    )

    question4 = models.StringField(
        label='4. 假設客戶選擇了產品 A，客戶獲得 $65（即抽到藍色球）的機率是多少？',
        choices=[
            ('A', '(A) 20%，因為產品 A 中 5 顆球中有 1 顆是藍色球（$65）。'),
            ('B', '(B) 40%，因為產品 A 中 5 顆球中有 2 顆是藍色球（$65）。'),
            ('C', '(C) 60%，因為產品 A 中 5 顆球中有 3 顆是藍色球（$65）。'),
            ('D', '(D) 100%，因為產品 A 中 5 顆球中有 5 顆是藍色球（$65）。'),
        ],
        widget=widgets.RadioSelect
    )

    question5 = models.StringField(
        label='5. 以下敘述何者正確？',
        choices=[
            ('A', '(A) 產品B包含4 顆藍色球（$65）和 1 顆紅色球（$0）（如果其為高品質），或是包含2 顆藍色球（$65）和 3 顆紅色球（$0）（如果其為低品質）。'),
            ('B', '(B) 產品B包含3 顆藍色球（$65）和 2 顆紅色球（$0）（如果其為高品質），或是包含3 顆藍色球（$65）和 2 顆紅色球（$0）（如果其為低品質）。'),
            ('C', '(C) 產品B包含5 顆藍色球（$65）和 0 顆紅色球（$0）（如果其為高品質），或是包含0 顆藍色球（$65）和 5 顆紅色球（$0）（如果其為低品質）。'),
        ],
        widget=widgets.RadioSelect
    )


    
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

    #每回合重新分組
    # subsession.group_randomly(fixed_id_in_group=True)
    # group_by_arrival_time = True

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

class ComprehensionCheck(Page):
    form_model = 'player'
    form_fields = ['question1', 'question2', 'question3', 'question4', 'question5']

    # 整頁驗證：使用 error_message 檢查是否答對
    def error_message(self, values):
        # values 是使用者在這個 form 裡填的所有欄位
        # 比如 values['question1'] 就是 question1 的答案
        correct_answers = {
            'question1': 'B',
            'question2': 'B',
            'question3': 'A',
            'question4': 'C',
            'question5': 'A'
        }
        errors = []
        for q_name, correct_ans in correct_answers.items():
            if values[q_name] != correct_ans:
                errors.append(q_name)

        if errors:
            return "有一題或以上答錯了，請仔細閱讀實驗說明並修正答案，若有任何問題請舉手，實驗人員會過去協助。"

    @staticmethod
    def is_displayed(player):
        return player.round_number == 1
    
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
        quality = player.subsession.quality_signal
        if quality == "$65":
            image_path = 'blue_65.png'
        else:
            image_path = 'red_0.png'

        return dict(
            quality_signal=subsession.quality_signal,
            product_b_good_ball_probability=subsession.product_b_good_ball_probability,
            image_path=image_path)

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

    # group_by_arrival_time = True

    # @staticmethod
    # def after_all_players_arrive(subsession: Subsession):
    #     # # subsession.group_randomly(fixed_id_in_group=True)
    #     pass


# class ShufflePage(Page):
#     group_by_arrival_time = True

#     @staticmethod
#     def is_displayed(player):
#         return player.round_number > 1

#PageSequence
page_sequence = [
    # ComputerPage,
    MyWaitPage,
    ComprehensionCheck,
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
    # ShufflePage
]