from otree.api import *
import random

doc = """
抽球決定報酬，用來實現兩個 moralcost 的報酬。
"""


class C(BaseConstants):
    NAME_IN_URL = 'moralpayoff'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 2

    ADVISOR_ROLE = '推薦人'
    CLIENT_ROLE = '客戶'

    PRODUCT_A_SUCCESS_PROB = 0.6
    PRODUCT_B_SUCCESS_PROB_H = 0.8
    PRODUCT_B_SUCCESS_PROB_L = 0.4

    WAGE = 50
    COMMISSION = 15
    GOODBALL = 200
    BADBALL = 0


class Subsession(BaseSubsession):
    paying_group_id = models.IntegerField(initial=0)  # 每一回合(每個subsession)抽一組支付組

    def creating_session(self):
        # 你要保證每組都是 (who=True 的人, who=False 的人)
        if self.round_number == 1:
            # players = self.get_players()
            # advisors = [p for p in players if p.participant.who is True]
            # clients = [p for p in players if p.participant.who is False]
            # random.shuffle(advisors)
            # random.shuffle(clients)

            # # 保險：人數不平衡時，以較小者為準（實驗時你應該確保各半）
            # n = min(len(advisors), len(clients))
            # matrix = [[advisors[i], clients[i]] for i in range(n)]
            # self.set_group_matrix(matrix)
            
            players = self.get_players()
            random.shuffle(players)
            self.group_randomly()
        else:
            self.group_like_round(1)


class Group(BaseGroup):
    # outcomes (round-level)
    product_b_quality = models.StringField(blank=True, initial='')  # '高品質'/'低品質'
    product_b_good_ball_probability = models.FloatField(blank=True)
    advisor_ball_color = models.StringField(blank=True, initial='')  # '綠球'/'黃球'

    client_product = models.StringField(blank=True, initial='')  # 'X'/'Y'
    client_product_quality = models.StringField(blank=True, initial='')  # '高品質'/'低品質' or ''
    client_ball_color = models.StringField(blank=True, initial='')  # '綠球'/'黃球'

    # guard to avoid double-randomization
    outcomes_ready = models.BooleanField(initial=False)


class Player(BasePlayer):
    round_payoff = models.CurrencyField(initial=0)
    roundsum_payoff = models.CurrencyField(initial=0)

    @property
    def role(self):
        # """
        # round 1: who == True -> advisor, who == False -> client
        # round 2: 角色對調
        # """
        # if self.round_number == 1:
        #     return C.ADVISOR_ROLE if self.participant.who else C.CLIENT_ROLE
        # else:
        #     return C.CLIENT_ROLE if self.participant.who else C.ADVISOR_ROLE

        # round 1: 1=advisor, 2=client
        # round 2: 對調
        if self.round_number % 2 == 1:
            return C.ADVISOR_ROLE if self.id_in_group == 1 else C.CLIENT_ROLE
        else:
            return C.CLIENT_ROLE if self.id_in_group == 1 else C.ADVISOR_ROLE


def _get_advisor_and_participant(group: Group):
    players = group.get_players()
    advisor_player = next((pl for pl in players if pl.role == C.ADVISOR_ROLE), None)
    return advisor_player, (advisor_player.participant if advisor_player else None)


def _bonus_flags_for_round(advisor_participant, round_no: int):
    if advisor_participant is None:
        return (False, 1)

    if round_no == 1:
        rec_is_Y = getattr(advisor_participant, 'moral1_bonus_recommended_Y', False)
        x_case = getattr(advisor_participant, 'moral1_bonus_round_number', 1)
    else:
        rec_is_Y = getattr(advisor_participant, 'moral2_bonus_recommended_Y', False)
        x_case = getattr(advisor_participant, 'moral2_bonus_round_number', 1)

    return rec_is_Y, x_case


def _compute_outcomes_once(group: Group):
    """
    在同一頁面中一次產生所有 outcome：
    coin toss(決定Y品質) → advisor抽球 → client抽產品(X/Y) → client抽球
    只允許跑一次（用 outcomes_ready 擋掉重複）。
    """
    if group.outcomes_ready:
        return

    # 0) 找推薦人 participant（用來讀 moral1/moral2 的 bonus flags）
    advisor_player, advisor_participant = _get_advisor_and_participant(group)
    r = group.subsession.round_number
    rec_is_Y, x_case = _bonus_flags_for_round(advisor_participant, r)

    # 1) coin toss 決定 Product Y 品質（這裡假設 50/50）
    if group.product_b_quality == '':
        is_low = (random.random() < 0.5)
        group.product_b_quality = '低品質' if is_low else '高品質'
        group.product_b_good_ball_probability = (
            C.PRODUCT_B_SUCCESS_PROB_L if is_low else C.PRODUCT_B_SUCCESS_PROB_H
        )

    # 2) 推薦人從 Y 抽球（依品質機率）
    if group.advisor_ball_color == '':
        p_good = group.product_b_good_ball_probability or 0
        is_green = random.random() < p_good
        group.advisor_ball_color = '綠球' if is_green else '黃球'

    # 3) client 依 rec_is_Y 抽到要採用的產品 X/Y
    if group.client_product == '':
        u = random.random()
        if rec_is_Y:
            group.client_product = 'Y' if u < 0.78 else 'X'
        else:
            group.client_product = 'X' if u < 0.84 else 'Y'

        if group.client_product == 'Y':
            group.client_product_quality = group.product_b_quality
        else:
            group.client_product_quality = ''

    # 4) client 抽球：看自己拿到 X 或 Y 決定黃球機率
    if group.client_ball_color == '':
        if group.client_product == 'Y':
            if group.client_product_quality == '高品質':
                p_yellow = 1/5
            else:
                p_yellow = 3/5
        else:
            # X：看 x_case
            if x_case == 1:
                p_yellow = 0.0
            elif x_case == 2:
                p_yellow = 1/5
            elif x_case == 3:
                p_yellow = 2/5
            elif x_case == 4:
                p_yellow = 3/5
            elif x_case == 5:
                p_yellow = 1.0
            else:
                p_yellow = 0.0

        u2 = random.random()
        group.client_ball_color = '黃球' if u2 < p_yellow else '綠球'

    group.outcomes_ready = True


def set_payoffs(group: Group):
    """
    你的原邏輯：每回合抽一個支付組；只有支付組且符合條件才會有報酬。
    """
    subsession = group.subsession

    if subsession.paying_group_id == 0:
        paying_group = random.choice(subsession.get_groups())
        subsession.paying_group_id = paying_group.id_in_subsession

    is_paying_group = (group.id_in_subsession == subsession.paying_group_id)

    advisor_ball_color = group.advisor_ball_color
    client_ball_color = group.client_ball_color

    players = group.get_players()
    advisor_player = next((pl for pl in players if pl.role == C.ADVISOR_ROLE), None)
    advisor_participant = advisor_player.participant if advisor_player else None

    round_no = players[0].round_number
    if advisor_participant is not None:
        if round_no == 1:
            bonus_recommended_Y = getattr(advisor_participant, 'moral1_bonus_recommended_Y', False)
        else:
            bonus_recommended_Y = getattr(advisor_participant, 'moral2_bonus_recommended_Y', False)
    else:
        bonus_recommended_Y = False

    base_condition = (
        is_paying_group
        and bonus_recommended_Y
        and advisor_ball_color == '黃球'
    )

    for p in players:
        payoff = 0
        if base_condition:
            if p.role == C.ADVISOR_ROLE:
                payoff = 15
            else:
                if client_ball_color == '綠球':
                    payoff = 200

        p.round_payoff = cu(payoff)

        if p.round_number == 1:
            p.roundsum_payoff = p.round_payoff
        else:
            prev = p.in_round(p.round_number - 1)
            p.roundsum_payoff = prev.roundsum_payoff + p.round_payoff

        p.participant.moralpayoff = p.roundsum_payoff


def build_explanation(player: Player) -> str:
    """
    生成「本回合」的說明文字（等同你原本 RevealPage 的單回合版本）
    """
    g = player.group
    subsession = player.subsession
    paying_gid = subsession.paying_group_id
    is_paying = (g.id_in_subsession == paying_gid)

    advisor_player, advisor_participant = _get_advisor_and_participant(g)
    r = player.round_number

    if r == 1:
        bonus_Y = getattr(advisor_participant, 'moral1_bonus_recommended_Y', False) if advisor_participant else False
    else:
        bonus_Y = getattr(advisor_participant, 'moral2_bonus_recommended_Y', False) if advisor_participant else False

    advisor_ball = g.advisor_ball_color
    client_ball = g.client_ball_color

    if not is_paying:
        return "本回合您的組別未被抽中作為支付組，因此本回合報酬為 0 法幣。"

    # is paying group
    if player.role == C.ADVISOR_ROLE:
        if player.round_payoff > 0:
            return (
                f"您在本回合被抽中為推薦人。先前部分被抽中的那一次您推薦了產品 Y，"
                f"且本回合從產品中抽出的球為黃色球，因此您在本回合獲得 15 法幣。"
            )
        else:
            if not bonus_Y:
                reason = "先前被抽中的那次推薦並非產品 Y"
            elif advisor_ball != '黃球':
                reason = "本回合從產品中抽出的球不是黃色球"
            else:
                reason = "支付條件未同時滿足"
            return f"您在本回合被抽中為推薦人，但由於{reason}，因此本回合您的報酬為 0 法幣。"

    # client
    if player.round_payoff > 0:
        return (
            f"您在本回合被抽中為客戶。由於與您配對的推薦人在先前被抽中的那次推薦中選擇產品 Y，"
            f"且本回合他抽到黃色球，同時您在本回合從自己的產品中抽到綠球，因此您在本回合獲得 200 法幣。"
        )
    else:
        if (not bonus_Y) or (advisor_ball != '黃球'):
            reason = "推薦人先前的推薦與抽球結果未同時符合支付條件"
        elif client_ball != '綠球':
            reason = "您本回合從產品中抽出的球不是綠球"
        else:
            reason = "支付條件未同時滿足"
        return f"您在本回合被抽中為客戶，但由於{reason}，因此本回合您的報酬為 0 法幣。"

class InstructionPage(Page):
    @staticmethod
    def is_displayed(player):
        return player.round_number == 1

class PayoffOnePage(Page):
    """
    這一頁包含：coin toss → advisor抽球 → client抽產品 → client抽球 → payoff與說明
    一個 round 一頁，所以總共兩頁（round1, round2）
    """
    @staticmethod
    def vars_for_template(player: Player):
        g = player.group

        # 只在第一個進來的人做 randomization + payoff
        _compute_outcomes_once(g)
        set_payoffs(g)

        # 圖片對應
        product_image = 'ProductY_high.png' if g.product_b_quality == '高品質' else 'ProductY_low.png'
        advisor_ball_image = 'green_65.png' if g.advisor_ball_color == '綠球' else 'orange_0.png'
        client_ball_image = 'green_65.png' if g.client_ball_color == '綠球' else 'orange_0.png'

        # X case 圖（用推薦人的 moralX case）
        advisor_player, advisor_participant = _get_advisor_and_participant(g)
        rec_is_Y, x_case = _bonus_flags_for_round(advisor_participant, player.round_number)
        productX_image = f'ProductX{x_case}.png'

        # round title：你要的「第一部分 / 第五部分」
        title = "第一部分報酬" if player.round_number == 1 else "第五部分報酬"

        return dict(
            page_title=title,
            product_image=product_image,
            advisor_ball_image=advisor_ball_image,
            client_ball_image=client_ball_image,
            productX_image=productX_image,
            rec_is_Y=rec_is_Y,
            explanation=build_explanation(player),
            round_payoff=player.round_payoff,
            total_payoff=player.roundsum_payoff,
        )


page_sequence = [
    InstructionPage,
    PayoffOnePage,
]
