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


class Group(BaseGroup):
    recommendation = models.StringField(
        choices=[['A', '產品 A'], ['B', '產品 B']],
        widget=widgets.RadioSelect,
        label="我推薦：",
    )
    selection = models.StringField(
        choices=[['A', '產品 A'], ['B', '產品 B']],
        widget=widgets.RadioSelect,
        label="我選擇：",
    )
    commission_product = models.StringField(blank=True)
    product_b_quality = models.StringField(blank=True)
    product_b_good_ball_probability = models.FloatField(blank=True)
    quality_signal = models.StringField(blank=True)
    # ✅ 新增：客戶「實際抽球結果」用來顯示圖片
    client_draw_result = models.StringField(blank=True)  # "$200" or "$0"
    client_draw_image  = models.StringField(blank=True)  # 'blue_65.png' or 'red_0.png'


class Player(BasePlayer):
    advisor_recommendation = models.StringField(blank=True)
    # 看起來沒用到
    # advisor_preference = models.StringField(blank=True)
    client_selection = models.StringField(blank=True)
    selection_if_A = models.StringField(
        choices=[['A','產品 A'], ['B','產品 B']],
        widget=widgets.RadioSelect,
        label='1. 如果這回合推薦人推薦「產品 A」，你會選擇哪一個產品？'
    )
    selection_if_B = models.StringField(
        choices=[['A','產品 A'], ['B','產品 B']],
        widget=widgets.RadioSelect,
        label='2. 如果這回合推薦人推薦「產品 B」，你會選擇哪一個產品？'
    )

    round_payoff = models.CurrencyField(initial=0)          # 該回合原始實現報酬
    paid_round_payoff = models.CurrencyField(initial=0)     # 真正計入支付的報酬
    roundsum_payoff = models.CurrencyField(initial=0)       # 累積「實際支付」報酬
    partner_payoff = models.CurrencyField(initial=0)

    is_selected_for_payment = models.BooleanField(initial=False)  # client 該回合是否被抽中計酬

    # --- Player fields ---
    left_changed  = models.IntegerField(initial=0)   # 左卡是否不同於原色（0/1）
    right_changed = models.IntegerField(initial=0)   # 右卡是否不同於原色（0/1})

    choice_1 = models.StringField(choices=['Quality','Incentive'], initial='Incentive')  # 左
    choice_2 = models.StringField(choices=['Quality','Incentive'], blank=True)
    choice_3 = models.StringField(choices=['Quality','Incentive'], blank=True)
    choice_4 = models.StringField(choices=['Quality','Incentive'], initial='Quality')    # 右
    # 存「這回合」抽到的資訊順序：'IF' 或 'QF'
    treatment_draw = models.StringField(blank=True)

    # 顯示用：推薦人「未扣翻牌成本」的本回合報酬（50 or 65）
    gross_payoff = models.CurrencyField(initial=0)

    # 推薦人翻牌成本（每邊最多算一次，你目前用 left_changed/right_changed 0/1）
    flip_cost = models.CurrencyField(initial=0)


    def treatment_this_round(self):
        # 不要在這裡抽籤，這裡只回傳已經存好的結果
        return self.treatment_draw
    # def treatment_this_round(self):
    #     choices = [self.choice_1, self.choice_2, self.choice_3, self.choice_4]
    #     # print(choices)
    #     chosen_choice = random.choice(choices)
    #     # print(chosen_choice)

    #     if chosen_choice == 'Quality':
    #         return 'QF'
    #     elif chosen_choice == 'Incentive':
    #         return 'IF'
        
    question1 = models.StringField(
        label='1. 如何決定本回合兩則資訊的實際呈現順序？',
        choices=[
            ('A', '(A) 由推薦人自行選定一張卡片作為結果'),
            ('B', '(B) 由電腦從四張卡片中隨機抽出一張並依其顏色決定順序'),
            ('C', '(C) 由客戶自行選定一張卡片作為結果'),
            ('D', '(D) 依照最左邊那張卡片的顏色決定順序'),
        ],
        widget=widgets.RadioSelect
    )

    question2 = models.StringField(
        label='2. 假設有一個人將四張卡片調整為「紅紅紅黑」，請問他先看到「產品指派資訊」的機率為何？',
        choices=[
            ('A', '(A) 25%'),
            ('B', '(B) 50%'),
            ('C', '(C) 75%'),
        ],
        widget=widgets.RadioSelect
    )

    question3 = models.StringField(
        label='3. 假設有一個人將四張卡片調整為四張黑色，請問他需要支付額外法幣嗎？若是需要，請問支付多少法幣？',
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

def select_paid_rounds_for_client(player: Player):
    """
    對 client 隨機抽出 10 回合中的 5 回合作為計酬回合，
    並把結果寫進每一回合的 is_selected_for_payment。
    """
    if player.role != C.CLIENT_ROLE:
        return

    selected_round_numbers = random.sample(range(1, C.NUM_ROUNDS + 1), 5)

    for p in player.in_all_rounds():
        p.is_selected_for_payment = (p.round_number in selected_round_numbers)

def set_payoffs(group: Group):
    # === 先根據推薦把客戶的實現選擇決定出來（strategy method）===
    players = group.get_players()
    advisor = next((p for p in players if p.role == C.ADVISOR_ROLE), None)
    client  = next((p for p in players if p.role == C.CLIENT_ROLE), None)

    if advisor and client:
        realized_selection = client.selection_if_A if group.recommendation == 'A' else client.selection_if_B
        group.selection = realized_selection
        advisor.advisor_recommendation = group.recommendation
        client.client_selection = realized_selection

    # === 先算本回合原始 payoff ===
    for p in group.get_players():
        p.advisor_recommendation = group.recommendation
        p.client_selection = group.selection

        # -------------------------
        # Advisor payoff
        # -------------------------
        if p.role == C.ADVISOR_ROLE:
            gross = C.WAGE
            if p.advisor_recommendation == group.commission_product.replace("產品 ", ""):
                gross += C.COMMISSION

            left_once  = 1 if getattr(p, "left_changed", 0) else 0
            right_once = 1 if getattr(p, "right_changed", 0) else 0
            fee_sides = left_once + right_once
            flip_fee = C.CARD_CLICK_FEE * fee_sides

            net = gross - flip_fee

            p.gross_payoff = cu(gross)
            p.flip_cost = cu(flip_fee)

            # advisor 每回合都支付
            p.round_payoff = cu(net)
            p.paid_round_payoff = p.round_payoff
            p.is_selected_for_payment = True

        # -------------------------
        # Client payoff
        # -------------------------
        elif p.role == C.CLIENT_ROLE:
            payoff = 0
            rnd = random.random()
            won = False

            if p.client_selection == 'A':
                won = (rnd <= C.PRODUCT_A_SUCCESS_PROB)
            elif p.client_selection == 'B':
                prob = C.PRODUCT_B_SUCCESS_PROB_H if group.product_b_quality == '高品質' else C.PRODUCT_B_SUCCESS_PROB_L
                won = (rnd <= prob)

            if won:
                payoff += C.GOODBALL

            group.client_draw_result = "$200" if won else "$0"
            group.client_draw_image  = 'blue_65.png' if won else 'red_0.png'

            p.gross_payoff = cu(payoff)
            p.flip_cost = cu(0)

            # 先記錄原始 payoff；是否真的支付，等第 10 回合再決定
            p.round_payoff = cu(payoff)
            p.paid_round_payoff = cu(0)

    # === 到最後一回合時，對 client 抽 5/10 計酬，並寫進資料庫 ===
    any_player = group.get_players()[0]
    if any_player.round_number == C.NUM_ROUNDS:
        for p in group.get_players():
            if p.role == C.CLIENT_ROLE:
                select_paid_rounds_for_client(p)

                for rp in p.in_all_rounds():
                    if rp.is_selected_for_payment:
                        rp.paid_round_payoff = rp.round_payoff
                    else:
                        rp.paid_round_payoff = cu(0)

    # === 重算 cumulative payoff ===
    for p in group.get_players():
        all_rounds = p.in_rounds(1, p.round_number)
        p.roundsum_payoff = sum((rp.paid_round_payoff for rp in all_rounds), cu(0))
        p.participant.choice_payoff = p.roundsum_payoff

    # === partner payoff ===
    for p in group.get_players():
        partner = p.get_others_in_group()[0] if p.get_others_in_group() else None
        p.partner_payoff = partner.paid_round_payoff if partner else None

def payoff_headers_for(viewer: Player):
    # viewer = 目前正在看 table 的那個人
    if viewer.role == C.ADVISOR_ROLE:
        return ("推薦人推薦產品的報酬", "客戶選擇產品的報酬")
    else:
        return ("客戶選擇產品的報酬", "推薦人推薦產品的報酬")


def roles_in_round(p_in_round: Player):
    """給任何一個 round 裡的 player，回傳 (advisor_player, client_player)。"""
    ps = p_in_round.group.get_players()
    advisor = next((pp for pp in ps if pp.role == C.ADVISOR_ROLE), None)
    client  = next((pp for pp in ps if pp.role == C.CLIENT_ROLE), None)
    return advisor, client


def payoff_and_flip_for_round(viewer: Player, p_in_round: Player):
    """
    回傳 (payoff_col_1, payoff_col_2, flip_cost)
    - payoff 使用 gross_payoff（未扣翻牌成本）作為顯示
    - flip_cost 永遠顯示推薦人該回合 flip_cost（client 看也要顯示）
    """
    advisor, client = roles_in_round(p_in_round)

    flip_cost = advisor.flip_cost if advisor else None

    if viewer.role == C.ADVISOR_ROLE:
        # advisor view: (advisor gross, client gross, flip_cost 放中間由模板決定位置)
        return (
            advisor.gross_payoff if advisor else None,
            client.gross_payoff if client else None,
            flip_cost,
        )
    else:
        # client view: (client gross, advisor gross, flip_cost)
        return (
            client.gross_payoff if client else None,
            advisor.gross_payoff if advisor else None,
            flip_cost,
        )


def build_history_rows(viewer: Player, rounds_list):
    """
    rounds_list 必須是 Player list（例如 player.in_previous_rounds() / in_all_rounds()）
    回傳 list[dict]，每列都含 payoff_col_1/2 + flip_cost，模板可依角色排欄位順序。
    """
    rows = []
    for p in rounds_list:
        payoff_col_1, payoff_col_2, flip_cost = payoff_and_flip_for_round(viewer, p)

        rows.append({
            "round_number": p.round_number,
            "advisor_recommendation": p.advisor_recommendation,
            "client_selection": p.client_selection,
            "commission_product": p.group.commission_product,
            "product_b_quality": p.group.product_b_quality,
            "quality_signal": p.group.quality_signal,
            "quality_image": 'ProductB_high.png' if p.group.product_b_quality == "高品質" else 'ProductB_low.png',
            "signal_image": 'blue_65.png' if p.group.quality_signal == "$200" else 'red_0.png',
            "client_draw_image": p.group.client_draw_image,

            # ✅ 三個關鍵欄位
            "payoff_col_1": payoff_col_1,
            "payoff_col_2": payoff_col_2,
            "flip_cost": flip_cost,
        })

    rows.sort(key=lambda r: r["round_number"], reverse=True)
    return rows

#Pages
    
class MyWaitPage(WaitPage):
    group_by_arrival_time = True
    title_text = "請稍候"
    body_text = "正在等待其他參加者進入實驗，請耐心等候。"

    @staticmethod
    def after_all_players_arrive(group: Group):
        import random

        # 50-50 決定哪一個商品能獲得佣金
        commission_product = random.choice(['產品 A', '產品 B'])
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

    @staticmethod
    def vars_for_template(player: Player):
        prior_history = player.participant.vars.get('part23_history', [])
        prior_role = player.participant.vars.get('part23_role', player.role)

        part2_history = [row for row in prior_history if row.get("block_idx") == 1]
        part3_history = [row for row in prior_history if row.get("block_idx") == 2]

        # 跟 Part2/3 的 history table 一樣，依最近回合在上面
        part2_history.sort(key=lambda r: r["display_round_number"], reverse=True)
        part3_history.sort(key=lambda r: r["display_round_number"], reverse=True)

        if prior_role == C.ADVISOR_ROLE:
            payoff_col_1_label = "推薦人推薦產品的報酬"
            payoff_col_2_label = "客戶選擇產品的報酬"
        else:
            payoff_col_1_label = "客戶選擇產品的報酬"
            payoff_col_2_label = "推薦人推薦產品的報酬"

        return dict(
            part2_history=part2_history,
            part3_history=part3_history,
            prior_role=prior_role,
            payoff_col_1_label=payoff_col_1_label,
            payoff_col_2_label=payoff_col_2_label,
            is_advisor=(prior_role == C.ADVISOR_ROLE),
        )

class ComprehensionCheck(Page):
    form_model = 'player'
    form_fields = ['question1', 'question2', 'question3']

    # 整頁驗證：使用 error_message 檢查是否答對
    def error_message(self, values):
        # values 是使用者在這個 form 裡填的所有欄位
        # 比如 values['question1'] 就是 question1 的答案
        correct_answers = {
            'question1': 'B',
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

    @staticmethod
    def error_message(player, values):
        if not values.get('choice_2') or not values.get('choice_3'):
            return "請選擇中間兩張卡片要放入兩張紅色或兩張黑色。"

        labels = [values.get(f'choice_{i}') for i in range(1, 5)]
        red_cnt = sum(x == 'Incentive' for x in labels)
        black_cnt = sum(x == 'Quality' for x in labels)

        if red_cnt == 2 and black_cnt == 2:
            return "不得為兩紅兩黑，請修改卡片組合。"

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # 走到這裡代表：已經通過 error_message，choice_2/3 不會是 Blank
        cards = [player.choice_1, player.choice_2, player.choice_3, player.choice_4]

        # 等機率抽一張卡（random.choices 會回傳 list，所以取 [0]）
        picked = random.choices(cards, k=1)[0]

        # 把結果存起來，後面頁面只讀這個值
        player.treatment_draw = 'IF' if picked == 'Incentive' else 'QF'
    
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

        payoff_col_1_label, payoff_col_2_label = payoff_headers_for(player)
        history_records = build_history_rows(player, player.in_previous_rounds())

        return dict(
            history_records=history_records,
            payoff_col_1_label=payoff_col_1_label,
            payoff_col_2_label=payoff_col_2_label,
            is_advisor=(player.role == C.ADVISOR_ROLE),
        )


class WaitforAdvisor(WaitPage):
    title_text = "請稍候"
    body_text = "正在等待推薦人做出推薦，請耐心等候。"
    template_name = "choice/WaitforAdvisor.html"

    @staticmethod
    def vars_for_template(player: Player):
        payoff_col_1_label, payoff_col_2_label = payoff_headers_for(player)
        history_records = build_history_rows(player, player.in_previous_rounds())
        return dict(
            history_records=history_records,
            payoff_col_1_label=payoff_col_1_label,
            payoff_col_2_label=payoff_col_2_label,
            is_advisor=(player.role == C.ADVISOR_ROLE),
        )


class SelectionPage(Page):
    form_model = 'player'
    form_fields = ['selection_if_A', 'selection_if_B']

    @staticmethod
    def is_displayed(player):
        return player.role == C.CLIENT_ROLE

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group
        payoff_col_1_label, payoff_col_2_label = payoff_headers_for(player)
        history_records = build_history_rows(player, player.in_previous_rounds())

        return dict(
            history_records=history_records,
            payoff_col_1_label=payoff_col_1_label,
            payoff_col_2_label=payoff_col_2_label,
            is_advisor=(player.role == C.ADVISOR_ROLE),
        )

class WaitforClient(WaitPage):
    title_text = "請稍候"
    body_text = "正在等待客戶做出選擇，請耐心等候。"
    template_name = "choice/WaitforClient.html"

    @staticmethod
    def vars_for_template(player: Player):
        payoff_col_1_label, payoff_col_2_label = payoff_headers_for(player)
        history_records = build_history_rows(player, player.in_previous_rounds())
        return dict(
            history_records=history_records,
            payoff_col_1_label=payoff_col_1_label,
            payoff_col_2_label=payoff_col_2_label,
            is_advisor=(player.role == C.ADVISOR_ROLE),
        )

class DecisionWaitPage(WaitPage):
    title_text = "請稍候"
    body_text = "正在等待另一位參與者完成本回合決策，請耐心等候。"
    template_name = "choice/WaitforAll.html"

    @staticmethod
    def vars_for_template(player: Player):
        payoff_col_1_label, payoff_col_2_label = payoff_headers_for(player)
        history_records = build_history_rows(player, player.in_previous_rounds())
        return dict(
            history_records=history_records,
            payoff_col_1_label=payoff_col_1_label,
            payoff_col_2_label=payoff_col_2_label,
            is_advisor=(player.role == C.ADVISOR_ROLE),
        )
    
class ResultsWaitPage(WaitPage):    
    after_all_players_arrive = set_payoffs

class HistoryPage(Page):

    @staticmethod
    def vars_for_template(player: Player):
        payoff_col_1_label, payoff_col_2_label = payoff_headers_for(player)

        history_records = build_history_rows(player, player.in_all_rounds())

        # 本回合 record：用同一個 helper
        payoff_col_1, payoff_col_2, flip_cost = payoff_and_flip_for_round(player, player)
        this_round_record = {
            "round_number": player.round_number,
            "quality_image": 'ProductB_high.png' if player.group.product_b_quality == "高品質" else 'ProductB_low.png',
            "commission_product": player.group.commission_product,
            "signal_image": 'blue_65.png' if player.group.quality_signal == "$200" else 'red_0.png',
            "advisor_recommendation": player.advisor_recommendation,
            "client_selection": player.client_selection,
            "client_draw_image": player.group.client_draw_image,

            "payoff_col_1": payoff_col_1,
            "payoff_col_2": payoff_col_2,
            "flip_cost": flip_cost,
        }

        return dict(
            history_records=history_records,
            this_round_record=this_round_record,
            payoff_col_1_label=payoff_col_1_label,
            payoff_col_2_label=payoff_col_2_label,
            is_advisor=(player.role == C.ADVISOR_ROLE),
        )

class ShuffleWaitPage(WaitPage):
    wait_for_all_groups = True
    title_text = "請稍候"
    body_text = "正在等待所有人完成，請耐心等候其他參與者。"
    template_name = "choice/WaitforAll.html"

    @staticmethod
    def vars_for_template(player: Player):
        payoff_col_1_label, payoff_col_2_label = payoff_headers_for(player)
        history_records = build_history_rows(player, player.in_all_rounds())
        return dict(
            history_records=history_records,
            payoff_col_1_label=payoff_col_1_label,
            payoff_col_2_label=payoff_col_2_label,
            is_advisor=(player.role == C.ADVISOR_ROLE),
        )



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
    SelectionPage,
    DecisionWaitPage,
    ResultsWaitPage,
    HistoryPage,
    ShuffleWaitPage,
]