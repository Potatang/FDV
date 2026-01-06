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
    WAGE = 50
    # commission price
    COMMISSION = 15
    # 球的價值
    GOODBALL = 200
    BADBALL = 0   
    # 全選 Quality 或全選 Incentive 的扣除額
    # CHOICE_DECUCTION = 5
    # 新規則：點擊左右卡片的費用（每點一次）
    CARD_CLICK_FEE = 5

class Subsession(BaseSubsession):
    pass
    # commission_product = models.StringField(blank=True)
    # product_b_quality = models.StringField(blank=True)
    # product_b_good_ball_probability = models.FloatField(blank=True)
    # quality_signal = models.StringField(blank=True)

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
    commission_product = models.StringField(blank=True)
    product_b_quality = models.StringField(blank=True)
    product_b_good_ball_probability = models.FloatField(blank=True)
    quality_signal = models.StringField(blank=True)


class Player(BasePlayer):
    advisor_recommendation = models.StringField(blank=True)
    # 看起來沒用到
    # advisor_preference = models.StringField(blank=True)
    client_selection = models.StringField(blank=True)
    selection_if_A = models.StringField(
        choices=[['A','產品A'], ['B','產品B']],
        widget=widgets.RadioSelect,
        label='1. 如果這回合推薦人推薦「產品A」，你會選擇哪一個產品？'
    )
    selection_if_B = models.StringField(
        choices=[['A','產品A'], ['B','產品B']],
        widget=widgets.RadioSelect,
        label='2. 如果這回合推薦人推薦「產品B」，你會選擇哪一個產品？'
    )
    round_payoff = models.CurrencyField(initial=0)
    roundsum_payoff = models.CurrencyField(initial=0)
    partner_payoff = models.CurrencyField(initial=0)

    # --- Player fields ---
    left_changed  = models.IntegerField(initial=0)   # 左卡是否不同於原色（0/1）
    right_changed = models.IntegerField(initial=0)   # 右卡是否不同於原色（0/1})

    choice_1 = models.StringField(choices=['Quality','Incentive'], initial='Incentive')  # 左
    choice_2 = models.StringField(choices=['Quality','Incentive','Blank'], initial='Blank')   # 中左
    choice_3 = models.StringField(choices=['Quality','Incentive','Blank'], initial='Blank')   # 中右
    choice_4 = models.StringField(choices=['Quality','Incentive'], initial='Quality')    # 右
    def treatment_this_round(self):
        choices = [self.choice_1, self.choice_2, self.choice_3, self.choice_4]
        chosen_choice = random.choice(choices)

        if chosen_choice == 'Quality':
            return 'QF'
        elif chosen_choice == 'Incentive':
            return 'IF'
        
    question1 = models.StringField(
        label='1. 紅色卡片代表接下來出現的兩則資訊的順序為何？',
        choices=[
            ('A', '(A) 先看到「產品指派資訊」，再看到「抽球結果資訊」'),
            ('B', '(B) 先看到「抽球結果資訊」，再看到「產品指派資訊」'),
        ],
        widget=widgets.RadioSelect
    )

    question2 = models.StringField(
        label='2. 假設有一個人選擇將四張卡片調整為「紅紅紅黑」，請問他待會先看到「產品指派資訊」的機率為何？',
        choices=[
            ('A', '(A) 25%'),
            ('B', '(B) 50%'),
            ('C', '(C) 75%'),
        ],
        widget=widgets.RadioSelect
    )

    question3 = models.StringField(
        label='3. 假設有一個人選擇將四張卡片調整為四張黑色，請問他需要支付額外法幣嗎？若是需要，請問支付多少法幣？',
        choices=[
            ('A', '(A) 不需要'),
            ('B', '(B) 需要。 支付 5 法幣'),
            ('C', '(C) 需要。 支付 10 法幣'),
        ],
        widget=widgets.RadioSelect
    )
    
#FUNCTION
# note: this function goes at the module level, not inside the WaitPage.
def group_by_arrival_time_method(subsession, waiting_players):    
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
            # print(f"[order-assign] PID={p.participant.id_in_session} order={p.participant.vars['order']}")
            
        # # optionally propagate to clients (if they need it)
        # for c in [p for p in g.get_players() if not is_advisor(p)]:
        #     # tie client to their group's advisor order (pick the first advisor in the group)
        #     c.participant.vars['advisor_order'] = advisors[0].participant.vars['order']

    # # 50-50 決定哪一個商品能獲得佣金
    # commission_product = random.choice(['產品A', '產品B'])
    # subsession.commission_product = commission_product

    # # 50-50 決定 product B 的品質：high 或 low
    # product_b_quality = random.choice(['高品質', '低品質'])
    # subsession.product_b_quality = product_b_quality

    # # 根據產品B的品質設定抽中好球的機率：
    # # 低品質：40% 機率抽中好球；高品質：80% 機率抽中好球
    # if product_b_quality == '低品質':
    #     subsession.product_b_good_ball_probability = 0.4
    # else:
    #     subsession.product_b_good_ball_probability = 0.8

    # # 進行抽球，根據設定的機率決定抽中好球("$2")還是壞球("$0")
    # draw = random.random()  # 生成 0 到 1 的隨機數
    # if draw < subsession.product_b_good_ball_probability:
    #     subsession.quality_signal = "$200"
    # else:
    #     subsession.quality_signal = "$0"

def set_payoffs(group: Group):
    subsession = group.subsession

    # === 先根據推薦把客戶的實現選擇決定出來（strategy method）===
    players = group.get_players()
    advisor = next((p for p in players if p.role == C.ADVISOR_ROLE), None)
    client  = next((p for p in players if p.role == C.CLIENT_ROLE), None)

    if advisor and client:
        # advisor_recommendation 由 RecommendationPage 決定：group.recommendation
        realized_selection = client.selection_if_A if group.recommendation == 'A' else client.selection_if_B

        # 設定 group 與雙方 player 的當回合「行為」紀錄
        group.selection = realized_selection
        advisor.advisor_recommendation = group.recommendation
        client.client_selection = realized_selection

    # === 以下維持你原本的計算（含卡片費）===
    for p in group.get_players():
        p.advisor_recommendation = group.recommendation
        p.client_selection = group.selection

        if p.role == C.ADVISOR_ROLE:
            payoff = C.WAGE
            # 小心：commission_product 是 '產品A'/'產品B'，recommendation 是 'A'/'B'
            if p.advisor_recommendation == group.commission_product.replace("產品", ""):
                payoff += C.COMMISSION

            # 依是否改色計費（最多 2 邊）
            left_once  = 1 if getattr(p, "left_changed", 0)  else 0
            right_once = 1 if getattr(p, "right_changed", 0) else 0
            fee_sides = left_once + right_once
            payoff -= C.CARD_CLICK_FEE * fee_sides

        elif p.role == C.CLIENT_ROLE:
            payoff = 0
            rnd = random.random()
            if p.client_selection == 'A':
                if rnd <= 0.6:
                    payoff += C.GOODBALL
            elif p.client_selection == 'B':
                if group.product_b_quality == '低品質':
                    if rnd <= 0.4:
                        payoff += C.GOODBALL
                elif group.product_b_quality == '高品質':
                    if rnd <= 0.8:
                        payoff += C.GOODBALL

        p.round_payoff = cu(payoff)

        if p.round_number == 1:
            p.roundsum_payoff = p.round_payoff
        else:
            previous_round = p.in_round(p.round_number - 1)
            p.roundsum_payoff = previous_round.roundsum_payoff + p.round_payoff

        # 對應你原本的命名
        p.participant.choice_payoff = p.roundsum_payoff

    # 記錄對手報酬（用於歷史顯示）
    for p in group.get_players():
        partner = p.get_others_in_group()[0] if p.get_others_in_group() else None
        p.partner_payoff = partner.round_payoff if partner else None


#Pages
    
class MyWaitPage(WaitPage):
    group_by_arrival_time = True
    title_text = "請稍候"
    body_text = "正在等待其他參加者進入實驗，請耐心等候。"
    @staticmethod
    def after_all_players_arrive(group: Group):
        import random

        # 50-50 決定哪一個商品能獲得佣金
        commission_product = random.choice(['產品A', '產品B'])
        group.commission_product = commission_product

        # 50-50 決定 product B 的品質：高或低
        product_b_quality = random.choice(['高品質', '低品質'])
        group.product_b_quality = product_b_quality

        # 根據產品 B 的品質設定抽中好球的機率
        if product_b_quality == '低品質':
            group.product_b_good_ball_probability = 0.4
        else:
            group.product_b_good_ball_probability = 0.8

        # 抽 quality signal：$200 或 $0
        draw = random.random()
        if draw < group.product_b_good_ball_probability:
            group.quality_signal = "$200"
        else:
            group.quality_signal = "$0"

class InstructionPage(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class ComprehensionCheck(Page):
    form_model = 'player'
    form_fields = ['question1', 'question2', 'question3']

    # 整頁驗證：使用 error_message 檢查是否答對
    def error_message(self, values):
        # values 是使用者在這個 form 裡填的所有欄位
        # 比如 values['question1'] 就是 question1 的答案
        correct_answers = {
            'question1': 'A',
            'question2': 'C',
            'question3': 'B',
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

    
class ChoicePage(Page):
    form_model = 'player'
    form_fields = ['choice_1','choice_2','choice_3','choice_4','left_changed','right_changed']
    # form_invalid_message = "請做出選擇，再按下一頁。"

    @staticmethod  
    def error_message(player, values):
        # 先擋「中間有 Blank」
        if values.get('choice_2') == 'Blank' or values.get('choice_3') == 'Blank':
            return "請做出選擇"

        # 再擋「兩紅兩黑」（紅=Incentive，黑=Quality；Blank 不計）
        labels = [values.get(f'choice_{i}') for i in range(1, 5)]
        red_cnt   = sum(x == 'Incentive' for x in labels)
        black_cnt = sum(x == 'Quality'   for x in labels)
        if red_cnt == 2 and black_cnt == 2:
            return "不得為兩紅兩黑，請修改卡片組合。"

    # def error_message(player, values):
    #     # Count "Quality" among the 4 choices
    #     q = sum(1 for i in range(1, 5) if values.get(f'choice_{i}') == 'Quality')
    #     # exactly 2 Quality and 2 Incentive is not allowed
    #     if q == 2:
    #         return "目前是兩張紅與兩張黑，請調整卡片後再繼續。"
    
    @staticmethod
    def vars_for_template(player: Player):
        # 左=Quality(紅)、右=Incentive(黑)、中兩張空白
        choices = dict(choice_1='Quality', choice_2='Blank', choice_3='Blank', choice_4='Incentive')
        if player.round_number == 1:
            current_sum = 0
        else:
            current_sum = player.in_round(player.round_number - 1).roundsum_payoff
        return dict(choices=choices, current_sum=current_sum)
    # @staticmethod
    # def vars_for_template(player: Player):
    #     choices = dict(choice_1='Quality', choice_2='Quality',
    #                    choice_3='Incentive', choice_4='Incentive')
    #     if player.round_number == 1:
    #         current_sum = 0
    #     else:
    #         current_sum = player.in_round(player.round_number - 1).roundsum_payoff
    #     return dict(choices=choices,
    #                 current_sum=current_sum
    #             )
    
    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE


class IncentivePage1(Page):

    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE and player.treatment_this_round() == 'IF'
    
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(commission_product=group.commission_product)

class QualityPage1(Page):

    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE and player.treatment_this_round() == 'IF'
    
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        quality = player.group.quality_signal
        if quality == "$200":
            image_path = 'blue_65.png'
        else:
            image_path = 'red_0.png'

        return dict(
            quality_signal=group.quality_signal,
            product_b_good_ball_probability=group.product_b_good_ball_probability,
            image_path=image_path)

class QualityPage2(Page):

    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE and player.treatment_this_round() == 'QF'
    
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        quality = player.group.quality_signal
        if quality == "$200":
            image_path = 'blue_65.png'
        else:
            image_path = 'red_0.png'

        return dict(
            quality_signal=group.quality_signal,
            product_b_good_ball_probability=group.product_b_good_ball_probability,
            image_path=image_path)

class IncentivePage2(Page):

    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE and player.treatment_this_round() == 'QF'
    
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        return dict(commission_product=group.commission_product)
    
class RecommendationPage(Page):
    form_model = 'group'
    form_fields = ['recommendation']

    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        history_records = [
            {
                "round_number": p.round_number,
                "id_in_group": p.id_in_group,
                "advisor_recommendation": p.advisor_recommendation,
                "client_selection": p.client_selection,
                "commission_product": p.group.commission_product,
                "product_b_quality": p.group.product_b_quality,
                "quality_signal": p.group.quality_signal,
                "round_payoff": p.round_payoff,
                "roundsum_payoff": p.roundsum_payoff,
                "quality_image": 'ProductB_high.png' if p.group.product_b_quality == "高品質" else 'ProductB_low.png',
                "signal_image": 'blue_65.png' if p.group.quality_signal == "$200" else 'red_0.png',
                "producta_image": 'ProductA.png',
                "partner_payoff": p.partner_payoff,
            }
            for p in player.in_previous_rounds()
        ]

        # 依回合倒序：最新的在最上面
        history_records.sort(key=lambda r: r["round_number"], reverse=True)

        return dict(
            commission_product=group.commission_product,
            history_records=history_records,
        )

# class RecommendationPage(Page):

#     form_model = 'group'
#     form_fields = ['recommendation']

#     @staticmethod
#     def is_displayed(player):
#         return player.role == C.ADVISOR_ROLE
    

#     @staticmethod
#     def vars_for_template(player: Player):
#         group = player.group
        
#         previous_decision_record = {
#             (p.round_number, p.id_in_group): {
#                 "round_number": p.round_number,
#                 "id_in_group": p.id_in_group,
#                 "advisor_recommendation": p.advisor_recommendation,
#                 "client_selection": p.client_selection,
#                 "commission_product": p.group.commission_product,
#                 "product_b_quality": p.group.product_b_quality,
#                 "quality_signal": p.group.quality_signal,
#                 "round_payoff": p.round_payoff,
#                 "roundsum_payoff": p.roundsum_payoff,
#                 "quality_image": 'ProductB_high.png' if p.group.product_b_quality == "高品質" else 'ProductB_low.png',
#                 "signal_image": 'blue_65.png' if p.group.quality_signal == "$65" else 'red_0.png',
#                 "producta_image": 'ProductA.png',
#                 "partner_payoff": p.partner_payoff,
#             }
#             for p in player.in_previous_rounds()
#         }
        
#         return dict(commission_product=group.commission_product,
#                     previous_decision_record=previous_decision_record,
#                     )

class WaitforAdvisor(WaitPage):
    title_text = "請稍候"
    body_text = "正在等待推薦人做出推薦，請耐心等候。"

class SelectionPage(Page):
    form_model = 'player'
    form_fields = ['selection_if_A', 'selection_if_B']

    @staticmethod
    def is_displayed(player):
        return player.role == C.CLIENT_ROLE

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        history_records = [
            {
                "round_number": p.round_number,
                "id_in_group": p.id_in_group,
                "advisor_recommendation": p.advisor_recommendation,
                "client_selection": p.client_selection,
                "commission_product": p.group.commission_product,
                "product_b_quality": p.group.product_b_quality,
                "quality_signal": p.group.quality_signal,
                "round_payoff": p.round_payoff,
                "roundsum_payoff": p.roundsum_payoff,
                "quality_image": 'ProductB_high.png' if p.group.product_b_quality == "高品質" else 'ProductB_low.png',
                "signal_image": 'blue_65.png' if p.group.quality_signal == "$200" else 'red_0.png',
                "producta_image": 'ProductA.png',
                "partner_payoff": p.partner_payoff,
            }
            for p in player.in_previous_rounds()
        ]

        history_records.sort(key=lambda r: r["round_number"], reverse=True)

        return dict(
            recommendation=group.recommendation,
            history_records=history_records,
        )

    
class WaitforClient(WaitPage):
    title_text = "請稍候"
    body_text = "正在等待客戶做出選擇，請耐心等候。"

class ResultsWaitPage(WaitPage):    
    after_all_players_arrive = set_payoffs

class HistoryPage(Page):

    @staticmethod
    def vars_for_template(player: Player):

        history_records = [
            {
                "round_number": p.round_number,
                "id_in_group": p.id_in_group,
                "advisor_recommendation": p.advisor_recommendation,
                "client_selection": p.client_selection,
                "commission_product": p.group.commission_product,
                "product_b_quality": p.group.product_b_quality,
                "quality_signal": p.group.quality_signal,
                "round_payoff": p.round_payoff,
                "roundsum_payoff": p.roundsum_payoff,
                "quality_image": 'ProductB_high.png' if p.group.product_b_quality == "高品質" else 'ProductB_low.png',
                "signal_image": 'blue_65.png' if p.group.quality_signal == "$200" else 'red_0.png',
                "producta_image": 'ProductA.png',
                "partner_payoff": p.partner_payoff,
            }
            for p in player.in_all_rounds()
        ]

        # 回合倒序（最新在上）
        history_records.sort(key=lambda r: r["round_number"], reverse=True)

        return dict(history_records=history_records)


class ShuffleWaitPage(WaitPage):
    wait_for_all_groups = True
    title_text = "請稍候"
    body_text = "正在等待所有人準備完成，請耐心等候其他參與者。"



#PageSequence
page_sequence = [
    MyWaitPage,
    InstructionPage,
    ComprehensionCheck,
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