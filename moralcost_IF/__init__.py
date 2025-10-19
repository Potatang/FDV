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
                RecommendationPage,
                MoralWaitPage,
                ChoosePage,
                NotChosenRevealPage,
                ChosenRevealAdvisorPage,
                ChosenRevealClientPage,
                ]