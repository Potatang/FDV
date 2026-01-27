from otree.api import *
import random


doc = """
Advisor-Client Recommendation Experiment
在本實驗中，一半是 advisor，一半是 client。
每回合 advisor 依據產品 B 的品質訊息與附加的佣金訊息決定推薦 A 或 B，
client 看到 advisor 推薦後，直接選擇商品 A 或 B，
最終支付則依據每回合抽球結果決定，並且所有回合都會計入最終報酬。
"""

#Models
class C(BaseConstants):
    NAME_IN_URL = 'experiment_IF'
    PLAYERS_PER_GROUP = 2
    BLOCK_SIZE = 10  # 每段 10 回合
    NUM_ROUNDS = 20

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
    # 每一組自己的佣金商品/品質/訊號
    commission_product = models.StringField(blank=True)
    product_b_quality = models.StringField(blank=True)
    product_b_good_ball_probability = models.FloatField(blank=True)
    quality_signal = models.StringField(blank=True)

class Player(BasePlayer):
    advisor_recommendation = models.StringField(blank=True)
    client_selection = models.StringField(blank=True)
    selection_if_A = models.StringField(
        choices=[['A','產品A'], ['B','產品B']],
        widget=widgets.RadioSelect,
        label='1. 如果這回合推薦人向您推薦「產品A」，你會選擇哪一個產品？'
    )
    selection_if_B = models.StringField(
        choices=[['A','產品A'], ['B','產品B']],
        widget=widgets.RadioSelect,
        label='2. 如果這回合推薦人向您推薦「產品B」，你會選擇哪一個產品？'
    )

    round_payoff = models.CurrencyField(initial=0)
    roundsum_payoff = models.CurrencyField(initial=0)
    partner_payoff = models.CurrencyField(initial=0)

    question1 = models.StringField(
        label='1. 產品 A 中有多少顆藍色的球？',
        choices=[
            ('A', '(A) 2顆'),
            ('B', '(B) 3顆'),
            ('C', '(C) 4顆'),
        ],
        widget=widgets.RadioSelect
    )

    question2 = models.StringField(
        label='2. 產品 B 可能是高品質的機率為何？',
        choices=[
            ('A', '(A) 25%'),
            ('B', '(B) 50%'),
            ('C', '(C) 75%'),
        ],
        widget=widgets.RadioSelect
    )

    question3 = models.StringField(
        label='3. 假設電腦從客戶選擇的產品中抽到紅色球，請問該客戶的報酬為多少？',
        choices=[
            ('A', '(A) $0'),
            ('B', '(B) $15'),
            ('C', '(C) $50'),
            ('D', '(D) $200'),
        ],
        widget=widgets.RadioSelect
    )

    question4 = models.StringField(
        label='4. 假設有一位客戶選擇了產品 A，請問他獲得 $200（即抽到藍色球）的機率是多少？',
        choices=[
            ('A', '(A) 20%，因為產品 A 中 5 顆球中有 1 顆是藍色球（$200）。'),
            ('B', '(B) 40%，因為產品 A 中 5 顆球中有 2 顆是藍色球（$200）。'),
            ('C', '(C) 60%，因為產品 A 中 5 顆球中有 3 顆是藍色球（$200）。'),
            ('D', '(D) 100%，因為產品 A 中 5 顆球中有 5 顆是藍色球（$200）。'),
        ],
        widget=widgets.RadioSelect
    )

    question5 = models.StringField(
        label='5. 以下敘述何者正確？',
        choices=[
            ('A', '(A) 產品 B 包含 4 顆藍色球（$200）和 1 顆紅色球（$0）（如果其為高品質），或是包含 2 顆藍色球（$200）和 3 顆紅色球（$0）（如果其為低品質）。'),
            ('B', '(B) 產品 B 包含 3 顆藍色球（$200）和 2 顆紅色球（$0）（如果其為高品質），或是包含 3 顆藍色球（$200）和 2 顆紅色球（$0）（如果其為低品質）。'),
            ('C', '(C) 產品 B 包含 5 顆藍色球（$200）和 0 顆紅色球（$0）（如果其為高品質），或是包含 0 顆藍色球（$200）和 5 顆紅色球（$0）（如果其為低品質）。'),
        ],
        widget=widgets.RadioSelect
    )

    def treatment_this_round(self):
        o = self.participant.vars.get('order')
        if o is None:
            # This participant is not an advisor (or not assigned). Decide how to handle:
            return None
        if self.round_number <= 10:
            return 'IF' if o == 1 else 'QF'
        else:
            return 'QF' if o == 1 else 'IF'

def display_round_no(round_number: int) -> int:
    return ((round_number - 1) % C.BLOCK_SIZE) + 1

def block_index(round_number: int) -> int:
    # 第 1 段=1（1–10 回合），第 2 段=2（11–20 回合）
    return ((round_number - 1) // C.BLOCK_SIZE) + 1
    
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
        # 從 session.config 讀你指定的順序（預設 1 = IF 先）
        order_global = int(subsession.session.config.get('order_global', 1))
        subsession.session.vars['order_global'] = order_global  # 可留存一份在 session.vars

        for p in subsession.get_players():
            p.participant.vars['order'] = order_global
            print(f"[order-assign] PID={p.participant.id_in_session} order={order_global}")


def set_payoffs(group: Group):
    # subsession = group.subsession

    # === 先根據推薦把客戶的實現選擇決定出來 ===
    # 找到本組的 advisor 與 client
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

    # === 以下維持你原本的計算 ===
    for p in group.get_players():
        p.advisor_recommendation = group.recommendation
        p.client_selection = group.selection

        if p.role == C.ADVISOR_ROLE:
            payoff = C.WAGE
            # 小心：你的 commission_product 是 '產品A'/'產品B'，而 recommendation 是 'A'/'B'
            if p.advisor_recommendation == group.commission_product.replace("產品", ""):
                payoff += C.COMMISSION
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

        p.participant.experiment_payoff = p.roundsum_payoff

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

class InstructionPage2(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1
    
class InstructionPage3(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 11

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
        quality = group.quality_signal
        if quality == "$200":
            image_path = 'blue_65.png'
        else:
            image_path = 'red_0.png'

        return dict(
            quality_signal=group.quality_signal,
            product_b_good_ball_probability=group.product_b_good_ball_probability,
            image_path=image_path,
        )

class QualityPage2(Page):

    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE and player.treatment_this_round() == 'QF'
    
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        quality = group.quality_signal
        if quality == "$200":
            image_path = 'blue_65.png'
        else:
            image_path = 'red_0.png'

        return dict(
            quality_signal=group.quality_signal,
            product_b_good_ball_probability=group.product_b_good_ball_probability,
            image_path=image_path,
        )

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

        window_start = ((player.round_number - 1) // C.BLOCK_SIZE) * C.BLOCK_SIZE + 1
        window_end   = min(window_start + C.BLOCK_SIZE - 1, C.NUM_ROUNDS)

        # 只取「上一輪之前」且位於該視窗的回合
        prev_in_window = [
            p for p in player.in_previous_rounds()
            if window_start <= p.round_number <= window_end
        ]
        # 倒序（新 → 舊）
        prev_in_window.sort(key=lambda r: r.round_number, reverse=True)

        decision_list = []
        for p in prev_in_window:
            decision_list.append({
                "round_number": display_round_no(p.round_number),  # 顯示 1–10
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
            })

        return dict(
            commission_product=group.commission_product,
            decision_list=decision_list,
            # window_start=window_start,
            # window_end=window_end,
            display_round = display_round_no(player.round_number),
            block_idx = block_index(player.round_number),
            window_start = window_start,
            window_end = window_end,
        )


class WaitforAdvisor(WaitPage):
    title_text = "請稍候"
    body_text = "正在等待推薦人做出推薦，請耐心等候。"
    template_name = "choice/WaitforAdvisor.html"

    @staticmethod
    def vars_for_template(player: Player):
        history_records = [
            {
                "round_number": p.round_number,
                "advisor_recommendation": p.advisor_recommendation,
                "client_selection": p.client_selection,
                "commission_product": p.group.commission_product,
                "product_b_quality": p.group.product_b_quality,
                "quality_signal": p.group.quality_signal,
                "round_payoff": p.round_payoff,
                "roundsum_payoff": p.roundsum_payoff,
                "partner_payoff": p.partner_payoff,
                "quality_image": 'ProductB_high.png' if p.group.product_b_quality == "高品質" else 'ProductB_low.png',
                "signal_image": 'blue_65.png' if p.group.quality_signal == "$200" else 'red_0.png',
                "producta_image": 'ProductA.png',
            }
            for p in player.in_previous_rounds()
        ]
        history_records.sort(key=lambda r: r["round_number"], reverse=True)
        return dict(history_records=history_records,
                                is_advisor = (player.role == C.ADVISOR_ROLE),  # 或 '推薦人'
                                is_client = (player.role == C.CLIENT_ROLE),    # 或 '客戶'
                               )

class SelectionPage(Page):

    form_model = 'player'
    form_fields = ['selection_if_A', 'selection_if_B']
    
    @staticmethod
    def is_displayed(player):
        return player.role == C.CLIENT_ROLE

    @staticmethod
    def vars_for_template(player: Player):
        # === 十回合視窗 + 倒序（跟你前面一致） ===
        window_start = ((player.round_number - 1) // C.BLOCK_SIZE) * C.BLOCK_SIZE + 1
        window_end   = min(window_start + C.BLOCK_SIZE - 1, C.NUM_ROUNDS)

        prev_in_window = [
            p for p in player.in_previous_rounds()
            if window_start <= p.round_number <= window_end
        ]
        prev_in_window.sort(key=lambda r: r.round_number, reverse=True)

        decision_list = []
        for p in prev_in_window:
            decision_list.append({
                "round_number": display_round_no(p.round_number),  # 顯示 1–10
                "id_in_group": p.id_in_group,
                "advisor_recommendation": p.advisor_recommendation,
                "client_selection": p.client_selection,  # 這是已「實現」的選擇
                "commission_product": p.group.commission_product,
                "product_b_quality": p.group.product_b_quality,
                "quality_signal": p.group.quality_signal,
                "round_payoff": p.round_payoff,
                "roundsum_payoff": p.roundsum_payoff,
                "quality_image": 'ProductB_high.png' if p.group.product_b_quality == "高品質" else 'ProductB_low.png',
                "signal_image": 'blue_65.png' if p.group.quality_signal == "$200" else 'red_0.png',
                "producta_image": 'ProductA.png',
                "partner_payoff": p.partner_payoff,
            })

        return dict(
            decision_list=decision_list,
            display_round = display_round_no(player.round_number),
            block_idx = block_index(player.round_number),
            window_start = window_start,
            window_end = window_end,
        )
    
class WaitforClient(WaitPage):
    title_text = "請稍候"
    body_text = "正在等待客戶做出選擇，請耐心等候。"
    template_name = "choice/WaitforClient.html"
    @staticmethod
    def vars_for_template(player: Player):
        history_records = [
            {
                "round_number": p.round_number,
                "advisor_recommendation": p.advisor_recommendation,
                "client_selection": p.client_selection,
                "commission_product": p.group.commission_product,
                "product_b_quality": p.group.product_b_quality,
                "quality_signal": p.group.quality_signal,
                "round_payoff": p.round_payoff,
                "roundsum_payoff": p.roundsum_payoff,
                "partner_payoff": p.partner_payoff,
                "quality_image": 'ProductB_high.png' if p.group.product_b_quality == "高品質" else 'ProductB_low.png',
                "signal_image": 'blue_65.png' if p.group.quality_signal == "$200" else 'red_0.png',
                "producta_image": 'ProductA.png',
            }
            for p in player.in_previous_rounds()
        ]
        history_records.sort(key=lambda r: r["round_number"], reverse=True)
        return dict(history_records=history_records,
                    is_advisor=(player.role == C.ADVISOR_ROLE),  # 或 '推薦人'
                    is_client=(player.role == C.CLIENT_ROLE),    # 或 '客戶'
                   )

class ResultsWaitPage(WaitPage):    
    after_all_players_arrive = set_payoffs

class HistoryPage(Page):

    @staticmethod
    def vars_for_template(player: Player):
        window_start = ((player.round_number - 1) // C.BLOCK_SIZE) * C.BLOCK_SIZE + 1
        window_end   = min(window_start + C.BLOCK_SIZE - 1, C.NUM_ROUNDS)

        rounds_in_window = [
            p for p in player.in_all_rounds()
            if window_start <= p.round_number <= window_end
        ]
        rounds_in_window.sort(key=lambda r: r.round_number, reverse=True)

        decision_list = []
        for p in rounds_in_window:
            decision_list.append({
                "round_number": display_round_no(p.round_number),
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
            })

        # ✅ 本回合 record：欄位結構跟 decision_list 每列完全一致
        this_round_record = {
            "round_number": display_round_no(player.round_number),
            "quality_image": 'ProductB_high.png' if player.group.product_b_quality == "高品質" else 'ProductB_low.png',
            "commission_product": player.group.commission_product,
            "signal_image": 'blue_65.png' if player.group.quality_signal == "$200" else 'red_0.png',
            "advisor_recommendation": player.advisor_recommendation,
            "client_selection": player.client_selection,
            "round_payoff": player.round_payoff,
            "partner_payoff": player.partner_payoff,
        }


        return dict(
        decision_list=decision_list,
        this_round_record=this_round_record,  # ✅ 新增
        display_round=display_round_no(player.round_number),
        block_idx=block_index(player.round_number),
        window_start=window_start,
        window_end=window_end,
    )

    
    
class ShuffleWaitPage(WaitPage):
    wait_for_all_groups = True
    title_text = "請稍候"
    body_text = "正在等待所有人準備完成，請耐心等候其他參與者。"
    template_name = "choice/WaitforAll.html"
    @staticmethod
    def vars_for_template(player: Player):
        history_records = [
            {
                "round_number": p.round_number,
                "advisor_recommendation": p.advisor_recommendation,
                "client_selection": p.client_selection,
                "commission_product": p.group.commission_product,
                "product_b_quality": p.group.product_b_quality,
                "quality_signal": p.group.quality_signal,
                "round_payoff": p.round_payoff,
                "roundsum_payoff": p.roundsum_payoff,
                "partner_payoff": p.partner_payoff,
                "quality_image": 'ProductB_high.png' if p.group.product_b_quality == "高品質" else 'ProductB_low.png',
                "signal_image": 'blue_65.png' if p.group.quality_signal == "$200" else 'red_0.png',
                "producta_image": 'ProductA.png',
            }
            for p in player.in_all_rounds()
        ]
        history_records.sort(key=lambda r: r["round_number"], reverse=True)
        return dict(history_records=history_records,
                                is_advisor = (player.role == C.ADVISOR_ROLE),  # 或 '推薦人'
                                is_client = (player.role == C.CLIENT_ROLE),    # 或 '客戶'
                               )


#PageSequence
page_sequence = [
    MyWaitPage,
    InstructionPage2,
    InstructionPage3,
    ComprehensionCheck,
    AdvisorPage,
    ClientPage,
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
    # ShufflePage
]