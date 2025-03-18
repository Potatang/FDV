from otree.api import *
import random

doc = """
Advisor-Client Recommendation Experiment

在本實驗中，12位受試者中6位為advisor，6位為client。
每回合advisor依據產品B的品質訊息與回饋訊息決定推薦A或B，
client看到advisor推薦後，直接選擇商品A或B，
最終支付則依據每回合抽球結果決定，但只有從50回合中隨機抽取的10回合會計入最終報酬。
"""

# =============================================================================
# CONSTANTS
# =============================================================================
class C(BaseConstants):
    NAME_IN_URL = 'experiment'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 50
    INCENTIVE_AMOUNT = cu(10)
    TREATMENT_OPTIONS = ['see_quality_first', 'see_incentive_first']
    ADVISOR_ROLE = 'advisor'
    CLIENT_ROLE = 'client'
    ADVISOR_COUNT = 6  # 6 advisors out of 12 participants

    # Product A: 抽到 $2 的機率
    PRODUCT_A_SUCCESS_PROB = 0.6
    # Product B: 依據品質狀態θ決定抽到 $2 的機率
    PRODUCT_B_SUCCESS_PROB_H = 0.8
    PRODUCT_B_SUCCESS_PROB_L = 0.4


# =============================================================================
# SUBSESSION 與 分組設定
# =============================================================================
class Subsession(BaseSubsession):
    def creating_session(self):
        # 第一回合：將前6位指定為 advisor，其餘為 client，
        # 並隨機為advisor指派 treatment。
        if self.round_number == 1:
            players = self.get_players()
            for i, p in enumerate(players):
                if i < C.ADVISOR_COUNT:
                    p.participant.vars['role'] = C.ADVISOR_ROLE
                    p.treatment = random.choice(C.TREATMENT_OPTIONS)
                else:
                    p.participant.vars['role'] = C.CLIENT_ROLE

        # 每回合皆進行隨機配對
        advisors = [p for p in self.get_players() if p.participant.vars.get('role') == C.ADVISOR_ROLE]
        clients = [p for p in self.get_players() if p.participant.vars.get('role') == C.CLIENT_ROLE]

        random.shuffle(advisors)
        random.shuffle(clients)

        group_matrix = []
        for adv, cli in zip(advisors, clients):
            group_matrix.append([adv, cli])
        self.set_group_matrix(group_matrix)

        # 為每位advisor模擬本回合訊息
        for p in self.get_players():
            if p.participant.vars.get('role') == C.ADVISOR_ROLE:
                # 模擬產品B的品質狀態θ（H或L）
                p.theta = random.choice(['H', 'L'])
                # 根據θ模擬抽到的品質訊息（2 或 0）
                if p.theta == 'H':
                    p.quality_signal = 2 if random.random() < C.PRODUCT_B_SUCCESS_PROB_H else 0
                else:
                    p.quality_signal = 2 if random.random() < C.PRODUCT_B_SUCCESS_PROB_L else 0
                # 隨機決定回饋訊息，表示推薦該產品是否有額外回饋
                p.incentive_product = random.choice(['A', 'B'])
                # 判斷是否存在利益衝突：
                # 若 incentive 為 B 且品質訊息為 0，
                # 或 incentive 為 A 且品質訊息為 2，則發生衝突。
                p.conflict = ((p.incentive_product == 'B' and p.quality_signal == 0) or
                              (p.incentive_product == 'A' and p.quality_signal == 2))


# =============================================================================
# GROUP 與 PLAYER 模型
# =============================================================================
class Group(BaseGroup):
    pass


class Player(BasePlayer):
    # ===== Advisor 相關變數 =====
    treatment = models.StringField(blank=True)  # 'see_quality_first' 或 'see_incentive_first'
    theta = models.StringField(blank=True)        # 產品B品質狀態：'H' 或 'L'
    quality_signal = models.IntegerField(blank=True)  # 從產品B抽球結果：2 或 0
    incentive_product = models.StringField(
        blank=True,
        choices=['A', 'B'],
        doc="回饋訊息：推薦該產品是否可獲得額外回饋"
    )
    advisor_recommendation = models.StringField(
        blank=True,
        choices=['A', 'B'],
        widget=widgets.RadioSelect,
        doc="Advisor 的推薦決策"
    )
    conflict = models.BooleanField(blank=True, doc="是否存在利益衝突")

    # ===== Client 相關變數 =====
    # 由於改為直接選擇商品，因此不再使用 follow_recommendation
    chosen_product = models.StringField(
        blank=True,
        choices=['A', 'B'],
        widget=widgets.RadioSelect,
        doc="客戶最終選擇的產品"
    )

    def role(self):
        return self.participant.vars.get('role', '')

    def set_payoffs(self):
        """
        根據玩家角色計算每回合支付：
        - Client依據最終選擇之產品抽球決定支付
        - Advisor若推薦與incentive一致則獲得額外激勵金
        """
        if self.role() == C.CLIENT_ROLE:
            if self.chosen_product == 'A':
                payoff = 2 if random.random() < C.PRODUCT_A_SUCCESS_PROB else 0
                self.payoff = cu(payoff)
            elif self.chosen_product == 'B':
                # 從本組取得advisor，並依據其品質狀態決定支付
                advisor = [p for p in self.group.get_players() if p.role() == C.ADVISOR_ROLE][0]
                if advisor.theta == 'H':
                    payoff = 2 if random.random() < C.PRODUCT_B_SUCCESS_PROB_H else 0
                else:
                    payoff = 2 if random.random() < C.PRODUCT_B_SUCCESS_PROB_L else 0
                self.payoff = cu(payoff)
        elif self.role() == C.ADVISOR_ROLE:
            if self.advisor_recommendation == self.incentive_product:
                self.payoff = C.INCENTIVE_AMOUNT
            else:
                self.payoff = cu(0)


# =============================================================================
# Advisor 決策頁面
# =============================================================================
class AdvisorDecision(Page):
    form_model = 'player'
    form_fields = ['advisor_recommendation']

    def is_displayed(self):
        return self.role() == C.ADVISOR_ROLE

    def vars_for_template(self):
        treatment = self.player.treatment
        quality_signal = self.player.quality_signal
        incentive = self.player.incentive_product

        # 根據 treatment 決定訊息呈現順序
        if treatment == 'see_quality_first':
            first_info = {'label': '品質訊息（從產品B抽球）', 'value': quality_signal}
            second_info = {'label': '回饋訊息（推薦該產品可獲得額外回饋）', 'value': incentive}
        else:  # 'see_incentive_first'
            first_info = {'label': '回饋訊息（推薦該產品可獲得額外回饋）', 'value': incentive}
            second_info = {'label': '品質訊息（從產品B抽球）', 'value': quality_signal}

        return {
            'first_info': first_info,
            'second_info': second_info,
            'treatment': treatment,
            'conflict': self.player.conflict,
            'round_number': self.round_number,
        }


# =============================================================================
# 等待頁：等待 advisor 決策完成
# =============================================================================
class WaitForAdvisor(WaitPage):
    def is_displayed(self):
        return self.role() == C.CLIENT_ROLE

    wait_for_all_groups = True


# =============================================================================
# Client 決策頁面（改為直接選擇商品）
# =============================================================================
class ClientDecision(Page):
    form_model = 'player'
    form_fields = ['chosen_product']

    def is_displayed(self):
        return self.role() == C.CLIENT_ROLE

    def vars_for_template(self):
        # 取得本組advisor的推薦決策
        advisor = [p for p in self.group.get_players() if p.role() == C.ADVISOR_ROLE][0]
        
        # 修改為強調客戶自主選擇而非「跟隨」建議
        question_text = (
            f"推薦人向您推薦商品 <b>{advisor.advisor_recommendation}</b>。<br><br>"
            "請根據您的判斷，選擇您想要購買的商品："
        )
        
        return {
            'advisor_recommendation': advisor.advisor_recommendation,
            'question_text': question_text,
            'round_number': self.round_number,
        }


# =============================================================================
# 等待頁：所有玩家完成決策後計算每回合支付
# =============================================================================
class ResultsWaitPage(WaitPage):
    wait_for_all_groups = True

    def after_all_players_arrive(self):
        for p in self.subsession.get_players():
            p.set_payoffs()


# =============================================================================
# 結果頁面：呈現本回合結果資訊與支付
# =============================================================================
class Results(Page):
    def vars_for_template(self):
        result = {'round_number': self.round_number}
        
        if self.role() == C.ADVISOR_ROLE:
            result['treatment'] = self.player.treatment
            result['quality_signal'] = self.player.quality_signal
            result['incentive_product'] = self.player.incentive_product
            result['advisor_recommendation'] = self.player.advisor_recommendation
            result['conflict'] = self.player.conflict
            
            # 取得本組client的決策
            client = [p for p in self.group.get_players() if p.role() == C.CLIENT_ROLE][0]
            result['client_choice'] = client.chosen_product
            # 改為「客戶選擇與您推薦一致」而非「客戶跟隨您建議」
            result['client_agreed'] = client.chosen_product == self.player.advisor_recommendation
        else:  # client
            advisor = [p for p in self.group.get_players() if p.role() == C.ADVISOR_ROLE][0]
            result['advisor_recommendation'] = advisor.advisor_recommendation
            result['chosen_product'] = self.player.chosen_product
            # 改為「您的選擇與推薦一致」而非「您跟隨了建議」
            result['agreed_with_recommendation'] = self.player.chosen_product == advisor.advisor_recommendation
            
        result['payoff'] = self.player.payoff
        return result


# =============================================================================
# 最終結果頁面：在最後一回合隨機選取10回合作為報酬
# =============================================================================
class FinalResults(Page):
    def is_displayed(self):
        return self.round_number == C.NUM_ROUNDS

    def before_next_page(self):
        # 隨機抽取10個回合作為計算最終報酬的回合
        selected_rounds = random.sample(range(1, C.NUM_ROUNDS + 1), 10)
        # 計算這些回合的總支付
        total_payoff = sum([p.payoff for p in self.player.in_rounds() if p.round_number in selected_rounds])
        self.player.participant.payoff = total_payoff
        self.player.participant.vars['selected_rounds'] = selected_rounds

    def vars_for_template(self):
        selected_rounds = self.player.participant.vars.get('selected_rounds', [])
        
        # 獲取選中回合的詳細信息
        selected_rounds_details = []
        for round_num in selected_rounds:
            round_player = self.player.in_round(round_num)
            round_detail = {
                'round_number': round_num,
                'payoff': round_player.payoff
            }
            selected_rounds_details.append(round_detail)
            
        return {
            'selected_rounds': selected_rounds,
            'selected_rounds_details': selected_rounds_details,
            'final_payoff': self.player.participant.payoff,
            'role': self.player.role(),
        }


# =============================================================================
# Page Sequence
# =============================================================================
page_sequence = [
    AdvisorDecision,
    WaitForAdvisor,
    ClientDecision,
    ResultsWaitPage,
    Results,
    FinalResults,  # 僅在第50回合顯示
]