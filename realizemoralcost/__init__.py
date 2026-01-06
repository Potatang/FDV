from otree.api import *
import random


doc = """
抽球決定報酬，用來實現兩個 moralcost 的報酬。
"""

#Models
class C(BaseConstants):
    NAME_IN_URL = 'moralpayoff'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 2

    ADVISOR_ROLE = '推薦人'
    CLIENT_ROLE = '客戶'

    # Product A: 抽到 $2 的機率
    PRODUCT_A_SUCCESS_PROB = 0.6
    # Product Y: 依據品質狀態決定抽到 $2 的機率
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
    paying_group_id = models.IntegerField(initial=0)  # 被抽中要支付的那組


class Group(BaseGroup):

    commission_product = models.StringField(blank=True)
    product_b_quality = models.StringField(blank=True)
    product_b_good_ball_probability = models.FloatField(blank=True)
    quality_signal = models.StringField(blank=True)
    # advisor 抽球的結果：'綠球' 或 '黃球'
    advisor_ball_color = models.StringField(blank=True, initial='')
    client_product = models.StringField(
        choices=[('X', '產品X'), ('Y', '產品Y')],
        initial='',
    )
    client_product_quality = models.StringField(
        choices=[('高品質', '高品質'), ('低品質', '低品質')],
        blank=True,
    )
    # productB_quality = models.StringField(
    #     choices=[('H', '高品質'), ('L', '低品質')],
    #     initial='', 
    # )
    # 客戶在 ClientdrawPage 抽到的球顏色
    client_ball_color = models.StringField(
        choices=[('綠球', '綠球'), ('黃球', '黃球')],
        initial=''      # 一開始是空字串，還沒抽
    )

class Player(BasePlayer):
    advisor_dice = models.BooleanField(initial=False)
    advisor_ball = models.StringField(blank=True)
    client_ball = models.StringField(blank=True)

    round_payoff = models.CurrencyField(initial=0)
    roundsum_payoff = models.CurrencyField(initial=0)
    partner_payoff = models.CurrencyField(initial=0)

    @property
    def role(self):
        """
        round 1: who == True -> advisor, who == False -> client
        round 2: 角色對調
        """
        if self.round_number == 1:
            return C.ADVISOR_ROLE if self.participant.who else C.CLIENT_ROLE
        else:
            # 只有 2 回合，其他回合一律反過來
            return C.CLIENT_ROLE if self.participant.who else C.ADVISOR_ROLE


#FUNCTION
# note: this function goes at the module level, not inside the WaitPage.
def group_by_arrival_time_method(subsession, waiting_players):

    a_players = [p for p in waiting_players if p.participant.who == True]
    c_players = [p for p in waiting_players if p.participant.who == False]

    if len(a_players) >= 1 and len(c_players) >= 1:
        return [random.choice(a_players), random.choice(c_players)]
    


def set_payoffs(group: Group):
    """
    抽球實現 moral cost 的報酬：

    流程：
    1. 在本 subsession 所有 group 中隨機抽一組作為支付組 (paying_group)。
    2. 只有支付組的成員有機會拿到報酬，其餘一律 0。
    3. 在支付組中，先看「推薦人」是否同時滿足：
        (A) 前面 moral app 被抽中的那次推薦是產品 Y
        (B) 在本 app 中抽到的球是「黃球」
       若 (A)+(B) 都成立：
         - 推薦人 (advisor) 拿 15 法幣
         - 客戶 (client) 只有在「自己在 ClintdrawPage 抽到綠球」時，才拿 200 法幣
       其他情況一律 0。
    """

    subsession = group.subsession

    # 第一次進入任何一組時，隨機抽出全場唯一的「支付組」
    if subsession.paying_group_id == 0:
        import random
        paying_group = random.choice(subsession.get_groups())
        subsession.paying_group_id = paying_group.id_in_subsession

    # 判斷這一組是不是支付組
    is_paying_group = (group.id_in_subsession == subsession.paying_group_id)

    # 推薦人在本 app 抽到的球顏色（'綠球' 或 '黃球'）
    advisor_ball_color = group.advisor_ball_color
    # 客戶在本 app 抽到的球顏色（'綠球' 或 '黃球'）
    client_ball_color = group.client_ball_color

    players = group.get_players()
    # 找出本回合的推薦人
    advisor_player = next((pl for pl in players if pl.role == C.ADVISOR_ROLE), None)
    advisor_participant = advisor_player.participant if advisor_player else None

    # 先決定這一回合要看的 moral flag（全部人都看同一個回合）
    if advisor_participant is not None:
        round_no = players[0].round_number
        if round_no == 1:
            bonus_recommended_Y = getattr(
                advisor_participant, 'moral1_bonus_recommended_Y', False
            )
        elif round_no == 2:
            bonus_recommended_Y = getattr(
                advisor_participant, 'moral2_bonus_recommended_Y', False
            )
        else:
            bonus_recommended_Y = False
    else:
        bonus_recommended_Y = False

    # 只有在「支付組且推薦人推薦 Y 且推薦人抽到黃球」時，才有可能發生支付
    base_condition = (
        is_paying_group
        and bonus_recommended_Y
        and advisor_ball_color == '黃球'
    )

    for p in players:

        payoff = 0

        if base_condition:
            if p.role == C.ADVISOR_ROLE:
                # 推薦人只要滿足 base_condition 就拿 5，與 client 是否抽到綠球無關
                payoff = 15
            elif p.role == C.CLIENT_ROLE:
                # client 除了 base_condition 外，還要自己抽到綠球才拿 200
                if client_ball_color == '綠球':
                    payoff = 200

        # 非支付組、或條件不成立 → payoff = 0
        p.round_payoff = cu(payoff)

        # 兩回合累加
        if p.round_number == 1:
            p.roundsum_payoff = p.round_payoff
        else:
            prev = p.in_round(p.round_number - 1)
            p.roundsum_payoff = prev.roundsum_payoff + p.round_payoff

        # 存到 participant 讓後面可以用
        p.participant.moralpayoff = p.roundsum_payoff



#Pages
    
class InstructionPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        # 只在第一回合出現，用來第一次配對
        return player.round_number == 1

class MyWaitPage(WaitPage):
    group_by_arrival_time = True
    title_text = "請稍候"
    body_text = "正在等待其他參加者進入實驗，請耐心等候。"
    @staticmethod
    def is_displayed(player: Player):
        # 只在第一回合出現，用來第一次配對
        return player.round_number == 1

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

class DicePage(Page):
    form_model = 'player'
    form_fields = ['advisor_dice']  # 不需要受試者輸入任何東西，只是按鈕送出表單

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        group = player.group

        # advisor_dice: True = 正面, False = 反面
        is_head = player.advisor_dice

        # 正面 → 低品質；反面 → 高品質
        if is_head:
            group.product_b_quality = '低品質'
            group.product_b_good_ball_probability = C.PRODUCT_B_SUCCESS_PROB_L
        else:
            group.product_b_quality = '高品質'
            group.product_b_good_ball_probability = C.PRODUCT_B_SUCCESS_PROB_H

    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_path1='ProductY_Coin.png',
            image_path2='coin_front.png',
            image_path3='coin_back.png',
            image_path4='coin_neutral.png',
            )

    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE

class AdvisordrawPage(Page):
    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE
            
    @staticmethod
    def vars_for_template(player: Player):
        import random
        group = player.group

        # ====================
        # 1. 抽球結果（綠球/橘球）
        # ====================

        # 只要是空字串，就表示還沒抽過球，這裡抽一次
        if group.advisor_ball_color == '':
            p_good = group.product_b_good_ball_probability or 0
            is_green = random.random() < p_good
            group.advisor_ball_color = '綠球' if is_green else '黃球'

        if group.advisor_ball_color == '綠球':
            ball_image = 'green_65.png'   # 抽到綠球時的圖片
        else:
            ball_image = 'orange_0.png'   # 抽到橘球/黃球時的圖片

        # ====================
        # 2. 產品 Y 品質的圖片
        # ====================

        # 用你剛剛的邏輯：advisor_dice == True → 低品質；False → 高品質
        if player.advisor_dice:
            product_image = 'ProductY_low.png'
        else:
            product_image = 'ProductY_high.png'

        # 一次把三個變數都丟給 template
        return dict(
            ball_color    = group.advisor_ball_color,
            ball_image    = ball_image,
            product_image = product_image,
        )

class WaitforAdvisor(WaitPage):
    title_text = "請稍候"
    body_text = "正在等待推薦人，請耐心等候。"


class ProductPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.role == C.CLIENT_ROLE
    
    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        # 在 2 人一組的情況下，這個頁面只給「客戶」看，
        # 所以「推薦人」一定是同組的另一個人
        advisor = player.get_others_in_group()[0]
        adv_p = advisor.participant

        if player.round_number == 1:
            rec_is_Y = getattr(adv_p, 'moral1_bonus_recommended_Y', False)
            x_case   = getattr(adv_p, 'moral1_bonus_round_number', 1)
        else:
            rec_is_Y = getattr(adv_p, 'moral2_bonus_recommended_Y', False)
            x_case   = getattr(adv_p, 'moral2_bonus_round_number', 1)

        if group.client_product == '':
            u = random.random()
            print(f'client_product_draw: u={u}, rec_is_Y={rec_is_Y}')    

            if rec_is_Y:
                group.client_product = 'Y' if u < 0.78 else 'X'
            else:
                group.client_product = 'X' if u < 0.84 else 'Y'

            if group.client_product == 'Y':
                # ★ 品質直接沿用 DicePage 設定的 product_b_quality
                group.client_product_quality = group.product_b_quality
            else:
                group.client_product_quality = ''  # X 的品質你之後要用再加

        # X 的圖片
        productX_image = f'ProductX{x_case}.png'

        # Y 的圖片：直接看「高品質／低品質」
        if group.client_product == 'Y':
            quality = group.client_product_quality  # '高品質' 或 '低品質'
            productY_image = (
                'ProductY_high.png' if quality == '高品質' else 'ProductY_low.png'
            )
        else:
            productY_image = ''

        return dict(
            client_product=group.client_product,
            client_product_quality=group.client_product_quality,
            productX_image=productX_image,
            productY_image=productY_image,
        )


class ClientdrawPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        return player.role == C.CLIENT_ROLE

    @staticmethod
    def vars_for_template(player: Player):
        group = player.group

        # 一樣，這頁只給「客戶」，所以推薦人一定是另一位
        advisor = player.get_others_in_group()[0]
        adv_p = advisor.participant

        # 如果還沒抽過球，就抽一次
        if group.client_ball_color == '':
            # 決定黃球機率
            if group.client_product == 'Y':
                # Y：看品質
                if group.client_product_quality == '高品質':
                    p_yellow = 1/5      # 1 黃 4 綠
                else:
                    p_yellow = 3/5      # 3 黃 2 綠
            else:
                # X：看 advisor 的 moralX case
                if player.round_number == 1:
                    x_case = getattr(adv_p, 'moral1_bonus_round_number', 1)
                else:
                    x_case = getattr(adv_p, 'moral2_bonus_round_number', 1)

                if x_case == 1:
                    p_yellow = 0.0      # X1：5 綠
                elif x_case == 2:
                    p_yellow = 1/5      # X2：1 黃 4 綠
                elif x_case == 3:
                    p_yellow = 2/5      # X3：2 黃 3 綠
                elif x_case == 4:
                    p_yellow = 3/5      # X4：3 黃 2 綠
                elif x_case == 5:
                    p_yellow = 1.0      # X5：5 黃
                else:
                    p_yellow = 0.0      # 保險

            u = random.random()
            group.client_ball_color = '黃球' if u < p_yellow else '綠球'
            print(f'client_draw: product={group.client_product}, p_yellow={p_yellow}, u={u}, ball={group.client_ball_color}')

        # 跟 ProductPage 一樣，準備圖片給前端顯示
        if player.round_number == 1:
            x_case = getattr(adv_p, 'moral1_bonus_round_number', 1)
        else:
            x_case = getattr(adv_p, 'moral2_bonus_round_number', 1)

        productX_image = f'ProductX{x_case}.png'

        if group.client_product == 'Y':
            productY_image = (
                'ProductY_high.png' if group.client_product_quality == '高品質'
                else 'ProductY_low.png'
            )
        else:
            productY_image = ''

        # 對應球的顏色到圖片檔名
        if group.client_ball_color == '綠球':
            ball_image = 'green_65.png'
        else:  # '黃球'
            ball_image = 'orange_0.png'

        return dict(
            client_product=group.client_product,
            client_product_quality=group.client_product_quality,
            client_ball_color=group.client_ball_color,
            productX_image=productX_image,
            productY_image=productY_image,
            ball_image=ball_image,
        )


    
class WaitforClient(WaitPage):
    title_text = "請稍候"
    body_text = "正在等待客戶，請耐心等候。"

class ResultsWaitPage(WaitPage):    
    after_all_players_arrive = set_payoffs


class RevealPage(Page):

    @staticmethod
    def is_displayed(player: Player):
        # 只在最後一回合顯示
        return player.round_number == C.NUM_ROUNDS

    @staticmethod
    def vars_for_template(player: Player):
        subsession = player.subsession
        paying_gid = subsession.paying_group_id  # 被抽中的那組
        messages = []

        # 你的 set_payoffs 已經把累積報酬存在 roundsum_payoff
        total_payoff = player.roundsum_payoff

        ever_paying = False  # 紀錄這個玩家所在的組有沒有被抽中

        # 逐回合產生說明（現在是兩回合）
        for r in [1, 2]:
            p_r = player.in_round(r)
            g_r = p_r.group

            paying_gid_r = p_r.subsession.paying_group_id  # 用該回合的
            is_paying = (g_r.id_in_subsession == paying_gid_r)
            if not is_paying:
                # 這一回合所在的組不是支付組，先略過，最後再給統一說明
                continue

            ever_paying = True
            role_r = p_r.role                # '推薦人' 或 '客戶'
            payoff_r = p_r.round_payoff

            # 找出這一回合的推薦人
            players_r = g_r.get_players()
            advisor_r = next(pl for pl in players_r if pl.role == C.ADVISOR_ROLE)
            advisor_participant = advisor_r.participant

            # 推薦人在 moral app 中是否「被抽中的那次推薦選 Y」
            if r == 1:
                bonus_Y = getattr(advisor_participant,
                                  'moral1_bonus_recommended_Y', False)
            else:
                bonus_Y = getattr(advisor_participant,
                                  'moral2_bonus_recommended_Y', False)

            advisor_ball = g_r.advisor_ball_color   # 推薦人抽到的球
            client_ball = g_r.client_ball_color     # 客戶抽到的球

            # 根據身分與 payoff 組文字
            if role_r == C.ADVISOR_ROLE:
                if payoff_r > 0:
                    msg = (
                        f"您在第 {r} 回合被抽中為推薦人。"
                        f"在先前的道德成本部分，被抽中的那一次您推薦了產品 Y，"
                        f"且本回合從產品中抽出的球為黃色球，"
                        f"因此您在第 {r} 回合獲得 15 法幣。"
                    )
                else:
                    # 有被抽中為支付組，但條件沒成
                    if not bonus_Y:
                        reason = "先前被抽中的那次推薦並非產品 Y"
                    elif advisor_ball != '黃球':
                        reason = "本回合從產品中抽出的球不是黃色球"
                    else:
                        reason = "支付條件未同時滿足"
                    msg = (
                        f"您在第 {r} 回合被抽中為推薦人，"
                        f"但由於{reason}，因此本回合您的報酬為 0 法幣。"
                    )
            else:  # 客戶
                if payoff_r > 0:
                    msg = (
                        f"您在第 {r} 回合被抽中為客戶。"
                        f"由於與您配對的推薦人在先前被抽中的那次推薦中選擇產品 Y，"
                        f"且剛才他從產品中抽出的球為黃色球，"
                        f"同時您在本回合從自己的產品中抽到綠球，"
                        f"因此您在第 {r} 回合獲得 200 法幣。"
                    )
                else:
                    # 有被抽中為支付組，但沒拿到 200 的情況
                    if not bonus_Y or advisor_ball != '黃球':
                        reason = "推薦人先前的推薦與抽球結果未同時符合支付條件"
                    elif client_ball != '綠球':
                        reason = "您本回合從產品中抽出的球不是綠球"
                    else:
                        reason = "支付條件未同時滿足"
                    msg = (
                        f"您在第 {r} 回合被抽中為客戶，"
                        f"但由於{reason}，因此本回合您的報酬為 0 法幣。"
                    )

            messages.append(msg)

        # 如果兩回合都沒有在支付組裡
        if not ever_paying:
            messages.append(
                "在本部分中，您的組別並未被電腦抽中作為支付組，"
                "因此兩回合的報酬皆為 0 法幣。"
            )

        return dict(
            explanation_list=messages,
            total_payoff=total_payoff,
        )

    
class ShuffleWaitPage(WaitPage):
    wait_for_all_groups = True
    title_text = "請稍候"
    body_text = "正在等待所有人準備完成，請耐心等候其他參與者。"




#PageSequence
page_sequence = [
    MyWaitPage,
    InstructionPage,
    AdvisorPage,
    ClientPage,
    DicePage,
    AdvisordrawPage,
    WaitforAdvisor,
    ProductPage,
    ClientdrawPage,
    WaitforClient,
    ResultsWaitPage,
    ShuffleWaitPage,
    RevealPage,
]