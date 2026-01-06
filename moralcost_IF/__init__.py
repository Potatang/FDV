from otree.api import *
import re
import random

doc = """
This is the first part of the experiment, which assesses participants' moral cost.
"""


class C(BaseConstants):
    NAME_IN_URL = 'moralcost_IF'
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
    advisor_recommendation = models.StringField(choices=[['X', '產品X'], ['Y', '產品Y']])
    client_selection = models.StringField(choice=[['X', '產品X'], ['Y', '產品Y']])
    selected_no = models.IntegerField()
    


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    recommendation1 = models.StringField(
        choices=[['X', '產品X'], ['Y', '產品Y']],
        widget=widgets.RadioSelect,
        label="請問您會推薦哪一個產品給對方？",
    )
    recommendation2 = models.StringField(
        choices=[['X', '產品X'], ['Y', '產品Y']],
        widget=widgets.RadioSelect,
        label="請問您會推薦哪一個產品給對方？",
    )
    recommendation3 = models.StringField(
        choices=[['X', '產品X'], ['Y', '產品Y']],
        widget=widgets.RadioSelect,
        label="請問您會推薦哪一個產品給對方？",
    )
    recommendation4 = models.StringField(
        choices=[['X', '產品X'], ['Y', '產品Y']],
        widget=widgets.RadioSelect,
        label="請問您會推薦哪一個產品給對方？",
    )
    recommendation5 = models.StringField(
        choices=[['X', '產品X'], ['Y', '產品Y']],
        widget=widgets.RadioSelect,
        label="請問您會推薦哪一個產品給對方？",
    )
    selected_reco = models.StringField()
    
    # chosen_advisor = models.BooleanField(initial = False)
    # chosen_client = models.BooleanField(initial = False)

    question1 = models.StringField(
        label='1. 產品 X 中有多少顆綠色的球？',
        choices=[
            ('A', '(A) 2顆'),
            ('B', '(B) 3顆'),
            ('C', '(C) 4顆'),
            ('D', '(D) 不一定'),
        ],
        widget=widgets.RadioSelect
    )

    question2 = models.StringField(
        label='2. 產品 Y 可能是高品質的機率為何？',
        choices=[
            ('A', '(A) 25%'),
            ('B', '(B) 50%'),
            ('C', '(C) 75%'),
        ],
        widget=widgets.RadioSelect
    )

    question3 = models.StringField(
        label='3. 假設您被電腦隨機指定為「客戶」，而與您配對的推薦人向您推薦「產品 X 」，請問有多大的機率電腦會替您選擇產品 X？',
        choices=[
            ('A', '(A) $84%'),
            ('B', '(B) $16%'),
            ('C', '(C) $22%'),
            ('D', '(D) $78%'),
        ],
        widget=widgets.RadioSelect
    )

    question4 = models.StringField(
        label='4. 以下敘述何者正確？',
        choices=[
            ('A', '(A) 產品 Y 包含4 顆綠色球（$200）和 1 顆黃色球（$0）（如果其為高品質），或是包含2 顆綠色球（$200）和 3 顆黃色球（$0）（如果其為低品質）。'),
            ('B', '(B) 產品 Y 包含3 顆綠色球（$200）和 2 顆黃色球（$0）（如果其為高品質），或是包含3 顆綠色球（$200）和 2 顆黃色球（$0）（如果其為低品質）。'),
            ('C', '(C) 產品 Y 包含5 顆綠色球（$200）和 0 顆黃色球（$0）（如果其為高品質），或是包含0 顆綠色球（$200）和 5 顆黃色球（$0）（如果其為低品質）。'),
        ],
        widget=widgets.RadioSelect
    )

    question5 = models.StringField(
        label='5. 假設客戶從產品中抽到黃色球，請問他的報酬為多少？',
        choices=[
            ('A', '(A) $0'),
            ('B', '(B) $15'),
            ('C', '(C) $50'),
            ('D', '(D) $200'),
        ],
        widget=widgets.RadioSelect
    )

# PAGES
class InstructionPage(Page):
    pass

class ComprehensionCheck(Page):
    form_model = 'player'
    form_fields = ['question1', 'question2', 'question3', 'question4']

    # 整頁驗證：使用 error_message 檢查是否答對
    def error_message(self, values):
        # values 是使用者在這個 form 裡填的所有欄位
        # 比如 values['question1'] 就是 question1 的答案
        correct_answers = {
            'question1': 'D',
            'question2': 'B',
            'question3': 'A',
            'question4': 'A',
            # 'question5': 'A',
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
            participant.moral1_bonus_round_number = selected_no         # 全部人共同的 scenario 編號
            participant.moral1_bonus_recommendation = selected_reco     # 這個人對應到的推薦內容
            participant.moral1_bonus_recommended_Y = (selected_reco == 'Y')

            print(f"{participant.moral1_bonus_round_number = }")
            print(f"{participant.moral1_bonus_recommendation = }")
            print(f"{participant.moral1_bonus_recommended_Y = }")

        # 設 flag，避免重複跑
        subsession.been_chosen = True

# class ChoosePage(Page):
#     form_model = 'player'
#     form_fields = ['recommendation1', 'recommendation2', 'recommendation3', 'recommendation4', 'recommendation5', 'chosen_advisor', 'chosen_client']

#     @staticmethod
#     def vars_for_template(player: Player):
#         subsession = player.subsession

#         if player.chosen_advisor:
#             # 1. 收集這位被選中的推薦人五次推薦
#             recommendations = [
#                 player.recommendation1,
#                 player.recommendation2,
#                 player.recommendation3,
#                 player.recommendation4,
#                 player.recommendation5,
#             ]
#             recommendation_numbers = [1, 2, 3, 4, 5]

#             # 2. 隨機選出其中一個當「依據」
#             selected_recommendation_number = random.choice(recommendation_numbers)
#             selected_recommendation = recommendations[selected_recommendation_number - 1]

#             # 3. 原本就有的：存到 subsession（整個 app 共用）
#             subsession.recommendation_number = selected_recommendation_number
#             subsession.advisor_recommendation = selected_recommendation

#             # 4. 新增：存到 participant.vars，讓後面 app 可以讀
#             pvars = player.participant.vars
#             pvars['moral_bonus_round_number'] = selected_recommendation_number
#             pvars['moral_bonus_recommendation'] = selected_recommendation
#             pvars['moral_bonus_recommended_Y'] = (selected_recommendation == 'Y')
#             pvars['moral_bonus_chosen_advisor'] = True

#         else:
#             # 不是被選中的推薦人，就標記成 False（後面 app 預設就不會給 5 法幣）
#             pvars = player.participant.vars
#             # 只有在還沒設定過的時候才設 False，避免之後你在別地方有改
#             if 'moral_bonus_recommended_Y' not in pvars:
#                 pvars['moral_bonus_recommended_Y'] = False
#             if 'moral_bonus_chosen_advisor' not in pvars:
#                 pvars['moral_bonus_chosen_advisor'] = False

#         return {}


# class NotChosenRevealPage(Page):
#     @staticmethod
#     def is_displayed(player):
#         return player.chosen_advisor == False and player.chosen_client == False
    
#     # @staticmethod
#     # def app_after_this_page(player, upcoming_apps):
#     #     if player.participant.seat < 11:
#     #         return 'experiment_IF' 
#     #     else:
#     #         return 'experiment_QF'

# class ChosenRevealAdvisorPage(Page):

#     # form_model = 'player'
#     # form_fields = ['recommendation1', 'recommendation2', 'recommendation3', 'recommendation4', 'recommendation5', 'chosen_advisor']

#     @staticmethod
#     def vars_for_template(player: Player):
#         # if player.chosen_advisor:
#         #     recommendations = [
#         #         player.recommendation1,
#         #         player.recommendation2,
#         #         player.recommendation3,
#         #         player.recommendation4,
#         #         player.recommendation5,
#         #     ]
#         #     recommendation_numbers = [1, 2, 3, 4, 5]
#         #     import random
#         #     selected_recommendation_number = random.choice(recommendation_numbers)
#         #     selected_recommendation = recommendations[selected_recommendation_number - 1]
#         #     print(f'{selected_recommendation_number=}')
#         #     print(f'{selected_recommendation=}')

#         #     player.subsession.recommendation_number = selected_recommendation_number
#         #     player.subsession.advisor_recommendation = selected_recommendation

#         return dict(
#             recommendation_number=player.subsession.recommendation_number,
#             advisor_recommendation=player.subsession.advisor_recommendation,
#         )   

#     @staticmethod
#     def is_displayed(player):
#         return player.chosen_advisor == True 

#     # @staticmethod
#     # def app_after_this_page(player, upcoming_apps):
#     #     if player.participant.seat < 11:
#     #         return 'experiment_IF' 
#     #     else:
#     #         return 'experiment_QF'
        
# class ChosenRevealClientPage(Page):

#     form_model = 'player'
#     form_fields = ['chosen_client']

#     @staticmethod
#     def vars_for_template(player: Player):
#         if player.chosen_client:
#             received_recommendation = player.subsession.advisor_recommendation

#             import random
#             if received_recommendation == 'X':
#                 if random.random() <= 0.84:
#                     player.subsession.client_selection = 'X'
#                 else:
#                      player.subsession.client_selection = 'Y'
#             elif received_recommendation == 'Y':
#                 if random.random() <= 0.78:
#                     player.subsession.client_selection= 'Y'
#                 else:
#                     player.subsession.client_selection = 'X'
#             else:
#                 print('WTF')     

#         return dict(
#             received_recommendation=player.subsession.advisor_recommendation,
#             selection=player.subsession.client_selection,
#         )   
    
#     @staticmethod
#     def is_displayed(player):
#         return player.chosen_client == True

    # @staticmethod
    # def app_after_this_page(player, upcoming_apps):
    #     if player.participant.seat < 11:
    #         return 'experiment_IF' 
    #     else:
    #         return 'experiment_QF'
        

page_sequence = [InstructionPage,
                ComprehensionCheck,
                RecommendationPage,
                MoralWaitPage,
                ]