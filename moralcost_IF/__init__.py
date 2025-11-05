from otree.api import *
import re
import random

doc = """
This is the third part of the experiment, which assesses participants' moral cost.
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
    WAGE = 15
    # commission price
    COMMISSION = 5
    # 球的價值
    GOODBALL = 65
    BADBALL = 0   
    #probability of recommend product B in pilot test
    PRO_RB = 0.7



class Subsession(BaseSubsession):
    been_chosen = models.BooleanField(initial=False)
    recommendation_number = models.IntegerField()
    advisor_recommendation = models.StringField(choices=[['X', '產品X'], ['Y', '產品Y']])
    client_selection = models.StringField(choice=[['X', '產品X'], ['Y', '產品Y']])
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    recommendation1 = models.StringField(
        choices=[['X', '產品X'], ['Y', '產品Y']],
        widget=widgets.RadioSelect,
        label="我推薦：",
    )
    recommendation2 = models.StringField(
        choices=[['X', '產品X'], ['Y', '產品Y']],
        widget=widgets.RadioSelect,
        label="我推薦：",
    )
    recommendation3 = models.StringField(
        choices=[['X', '產品X'], ['Y', '產品Y']],
        widget=widgets.RadioSelect,
        label="我推薦：",
    )
    recommendation4 = models.StringField(
        choices=[['X', '產品X'], ['Y', '產品Y']],
        widget=widgets.RadioSelect,
        label="我推薦：",
    )
    recommendation5 = models.StringField(
        choices=[['X', '產品X'], ['Y', '產品Y']],
        widget=widgets.RadioSelect,
        label="我推薦：",
    )

    chosen_advisor = models.BooleanField(initial = False)
    chosen_client = models.BooleanField(initial = False)

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
        label='3. 假設您被電腦隨機指定為「客戶」，而與您配對的推薦人向您推薦「產品 X 」，請問您有多大的機率會選擇產品 X？',
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
            ('A', '(A) 產品 Y 包含4 顆綠色球（$65）和 1 顆黃色球（$0）（如果其為高品質），或是包含2 顆綠色球（$65）和 3 顆黃色球（$0）（如果其為低品質）。'),
            ('B', '(B) 產品 Y 包含3 顆綠色球（$65）和 2 顆黃色球（$0）（如果其為高品質），或是包含3 顆綠色球（$65）和 2 顆黃色球（$0）（如果其為低品質）。'),
            ('C', '(C) 產品 Y 包含5 顆綠色球（$65）和 0 顆黃色球（$0）（如果其為高品質），或是包含0 顆綠色球（$65）和 5 顆黃色球（$0）（如果其為低品質）。'),
        ],
        widget=widgets.RadioSelect
    )

    question5 = models.StringField(
        label='5. 假設客戶從產品中抽到黃色球，請問他的報酬為多少？',
        choices=[
            ('A', '(A) $0'),
            ('B', '(B) $5'),
            ('C', '(C) $15'),
            ('D', '(D) $65'),
        ],
        widget=widgets.RadioSelect
    )

# PAGES
class InstructionPage(Page):
    pass

class ComprehensionCheck(Page):
    form_model = 'player'
    form_fields = ['question1', 'question2', 'question3', 'question4', 'question5']

    # 整頁驗證：使用 error_message 檢查是否答對
    def error_message(self, values):
        # values 是使用者在這個 form 裡填的所有欄位
        # 比如 values['question1'] 就是 question1 的答案
        correct_answers = {
            'question1': 'D',
            'question2': 'B',
            'question3': 'A',
            'question4': 'A',
            'question5': 'A',
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
    
    @staticmethod
    def before_next_page(player, timeout_happened):
        subsession = player.subsession
        
        if subsession.been_chosen == False:
            import random

            all_players = subsession.get_players()
            chosen_players = random.sample(all_players, 2)
            chosen_players[0].chosen_advisor = True
            chosen_players[1].chosen_client = True
            subsession.been_chosen = True
        

class MoralWaitPage(WaitPage):
    wait_for_all_groups = True
    title_text = "請稍候"
    body_text = "正在等待所有人準備完成，請耐心等候其他參與者。"

class ChoosePage(Page):
    form_model = 'player'
    form_fields = ['recommendation1', 'recommendation2', 'recommendation3', 'recommendation4', 'recommendation5', 'chosen_advisor', 'chosen_client']

    @staticmethod
    def vars_for_template(player: Player):
        if player.chosen_advisor:
            recommendations = [
                player.recommendation1,
                player.recommendation2,
                player.recommendation3,
                player.recommendation4,
                player.recommendation5,
            ]
            recommendation_numbers = [1, 2, 3, 4, 5]
            import random
            selected_recommendation_number = random.choice(recommendation_numbers)
            selected_recommendation = recommendations[selected_recommendation_number - 1]

            player.subsession.recommendation_number = selected_recommendation_number
            player.subsession.advisor_recommendation = selected_recommendation
        
        # elif player.chosen_client:
        #     received_recommendation = player.subsession.advisor_recommendation

        #     import random
        #     if received_recommendation == 'X':
        #         if random.random() <= 0.84:
        #             player.subsession.client_selection = 'X'
        #         else:
        #              player.subsession.client_selection = 'Y'
        #     elif received_recommendation == 'Y':
        #         if random.random() <= 0.78:
        #             player.subsession.client_selection= 'Y'
        #         else:
        #             player.subsession.client_selection = 'X'
        #     else:
        #         print('WTF') 


class NotChosenRevealPage(Page):
    @staticmethod
    def is_displayed(player):
        return player.chosen_advisor == False and player.chosen_client == False
    
    # @staticmethod
    # def app_after_this_page(player, upcoming_apps):
    #     if player.participant.seat < 11:
    #         return 'experiment_IF' 
    #     else:
    #         return 'experiment_QF'

class ChosenRevealAdvisorPage(Page):

    # form_model = 'player'
    # form_fields = ['recommendation1', 'recommendation2', 'recommendation3', 'recommendation4', 'recommendation5', 'chosen_advisor']

    @staticmethod
    def vars_for_template(player: Player):
        # if player.chosen_advisor:
        #     recommendations = [
        #         player.recommendation1,
        #         player.recommendation2,
        #         player.recommendation3,
        #         player.recommendation4,
        #         player.recommendation5,
        #     ]
        #     recommendation_numbers = [1, 2, 3, 4, 5]
        #     import random
        #     selected_recommendation_number = random.choice(recommendation_numbers)
        #     selected_recommendation = recommendations[selected_recommendation_number - 1]
        #     print(f'{selected_recommendation_number=}')
        #     print(f'{selected_recommendation=}')

        #     player.subsession.recommendation_number = selected_recommendation_number
        #     player.subsession.advisor_recommendation = selected_recommendation

        return dict(
            recommendation_number=player.subsession.recommendation_number,
            advisor_recommendation=player.subsession.advisor_recommendation,
        )   

    @staticmethod
    def is_displayed(player):
        return player.chosen_advisor == True 

    # @staticmethod
    # def app_after_this_page(player, upcoming_apps):
    #     if player.participant.seat < 11:
    #         return 'experiment_IF' 
    #     else:
    #         return 'experiment_QF'
        
class ChosenRevealClientPage(Page):

    form_model = 'player'
    form_fields = ['chosen_client']

    @staticmethod
    def vars_for_template(player: Player):
        if player.chosen_client:
            received_recommendation = player.subsession.advisor_recommendation

            import random
            if received_recommendation == 'X':
                if random.random() <= 0.84:
                    player.subsession.client_selection = 'X'
                else:
                     player.subsession.client_selection = 'Y'
            elif received_recommendation == 'Y':
                if random.random() <= 0.78:
                    player.subsession.client_selection= 'Y'
                else:
                    player.subsession.client_selection = 'X'
            else:
                print('WTF')     

        return dict(
            received_recommendation=player.subsession.advisor_recommendation,
            selection=player.subsession.client_selection,
        )   
    
    @staticmethod
    def is_displayed(player):
        return player.chosen_client == True

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
                ChoosePage,
                NotChosenRevealPage,
                ChosenRevealAdvisorPage,
                ChosenRevealClientPage,
                ]