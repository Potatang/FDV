from otree.api import *
import re
import random

doc = """
This is the first part of the experiment, which assesses participants' moral cost.
"""


class C(BaseConstants):
    NAME_IN_URL = 'moralcost2'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1

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
    #probability of recommend product B in pilot test
    PRO_RB = 0.7



class Subsession(BaseSubsession):
    been_chosen = models.BooleanField(initial=False)
    recommendation_number = models.IntegerField()  # 全場共用：1~5
    advisor_recommendation = models.StringField(choices=[['X', '產品 X'], ['Y', '產品 Y']])
    client_selection = models.StringField(choice=[['X', '產品 X'], ['Y', '產品 Y']])
    selected_no = models.IntegerField()
    


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    recommendation1 = models.StringField(
        choices=[['X', '產品 X'], ['Y', '產品 Y']],
        widget=widgets.RadioSelect,
        label="請問您會推薦哪一個產品給對方？",
    )
    recommendation2 = models.StringField(
        choices=[['X', '產品 X'], ['Y', '產品 Y']],
        widget=widgets.RadioSelect,
        label="請問您會推薦哪一個產品給對方？",
    )
    recommendation3 = models.StringField(
        choices=[['X', '產品 X'], ['Y', '產品 Y']],
        widget=widgets.RadioSelect,
        label="請問您會推薦哪一個產品給對方？",
    )
    recommendation4 = models.StringField(
        choices=[['X', '產品 X'], ['Y', '產品 Y']],
        widget=widgets.RadioSelect,
        label="請問您會推薦哪一個產品給對方？",
    )
    recommendation5 = models.StringField(
        choices=[['X', '產品 X'], ['Y', '產品 Y']],
        widget=widgets.RadioSelect,
        label="請問您會推薦哪一個產品給對方？",
    )
    selected_reco = models.StringField()

# PAGES
class InstructionPage(Page):
    pass

class RecommendationPage(Page):

    form_model = 'player'
    form_fields = ['recommendation1', 'recommendation2', 'recommendation3', 'recommendation4', 'recommendation5']
    
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            image_path1='moral_1.png',
            image_path2='moral_2.png',
            image_path3='moral_3.png',
            image_path4='moral_4.png',
            image_path5='moral_5.png',
            image_path6='orange_0.png'
        )

class MoralWaitPage(WaitPage):
    wait_for_all_groups = True
    title_text = "請稍候"
    body_text = "正在等待所有人準備完成，請耐心等候其他參與者。"

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        import random

        # 確保只做一次
        if subsession.been_chosen:
            return

        # 1. 全場只抽一次：從 1~5 中抽一個
        selected_no = random.randint(1, 5)
        subsession.recommendation_number = selected_no

        # 2. 對每一個 player，用這個 selected_no 去抓他自己的第 selected_no 個推薦
        for player in subsession.get_players():
            recommendations = [
                player.recommendation1,
                player.recommendation2,
                player.recommendation3,
                player.recommendation4,
                player.recommendation5,
            ]

            # 這個人對應到的推薦（X 或 Y）
            selected_reco = recommendations[selected_no - 1]

            # 如果你想存在 player 裡，這裡才給 selected_reco 賦值
            player.selected_reco = selected_reco

            # 3. 存到 participant，給後面 app 用
            participant = player.participant
            participant.moral2_bonus_round_number = selected_no         # 全部人共同的 scenario 編號
            participant.moral2_bonus_recommendation = selected_reco     # 這個人對應到的推薦內容
            participant.moral2_bonus_recommended_Y = (selected_reco == 'Y')

            # print(f"{participant.moral2_bonus_round_number = }")
            # print(f"{participant.moral2_bonus_recommendation = }")
            # print(f"{participant.moral2_bonus_recommended_Y = }")

        # 設 flag，避免重複跑
        subsession.been_chosen = True

page_sequence = [InstructionPage,
                RecommendationPage,
                MoralWaitPage,
                ]