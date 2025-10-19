from otree.api import *


doc = """
remove those not show up.
"""


class C(BaseConstants):
    NAME_IN_URL = 'start_app'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    seat = models.IntegerField(blank = False, label='由實驗人員輸入座位電腦號碼，請參加者不要觸碰', min=0, max=99)
    who = models.BooleanField(label = '(限實驗人員操作，請參加者不要觸碰)',
                              choices=[
                                  [True, '推薦人'], 
                                  [False, '客戶']
                                  ],
                                initial = True
                                )
    
    question1 = models.StringField(
        label='1. 產品A中有多少顆藍色的球？',
        choices=[
            ('A', '(A) 2顆'),
            ('B', '(B) 3顆'),
            ('C', '(C) 4顆'),
        ],
        widget=widgets.RadioSelect
    )

    question2 = models.StringField(
        label='2. 產品B可能是高品質的機率為何？',
        choices=[
            ('A', '(A) 25%'),
            ('B', '(B) 50%'),
            ('C', '(C) 75%'),
        ],
        widget=widgets.RadioSelect
    )

    question3 = models.StringField(
        label='3. 假設電腦從客戶選擇的產品中抽到紅色球，請問他的報酬為多少？',
        choices=[
            ('A', '(A) $0'),
            ('B', '(B) $5'),
            ('C', '(C) $15'),
            ('D', '(D) $65'),
        ],
        widget=widgets.RadioSelect
    )

    question4 = models.StringField(
        label='4. 假設客戶選擇了產品 A，客戶獲得 $65（即抽到藍色球）的機率是多少？',
        choices=[
            ('A', '(A) 20%，因為產品 A 中 5 顆球中有 1 顆是藍色球（$65）。'),
            ('B', '(B) 40%，因為產品 A 中 5 顆球中有 2 顆是藍色球（$65）。'),
            ('C', '(C) 60%，因為產品 A 中 5 顆球中有 3 顆是藍色球（$65）。'),
            ('D', '(D) 100%，因為產品 A 中 5 顆球中有 5 顆是藍色球（$65）。'),
        ],
        widget=widgets.RadioSelect
    )

    question5 = models.StringField(
        label='5. 以下敘述何者正確？',
        choices=[
            ('A', '(A) 產品B包含4 顆藍色球（$65）和 1 顆紅色球（$0）（如果其為高品質），或是包含2 顆藍色球（$65）和 3 顆紅色球（$0）（如果其為低品質）。'),
            ('B', '(B) 產品B包含3 顆藍色球（$65）和 2 顆紅色球（$0）（如果其為高品質），或是包含3 顆藍色球（$65）和 2 顆紅色球（$0）（如果其為低品質）。'),
            ('C', '(C) 產品B包含5 顆藍色球（$65）和 0 顆紅色球（$0）（如果其為高品質），或是包含0 顆藍色球（$65）和 5 顆紅色球（$0）（如果其為低品質）。'),
        ],
        widget=widgets.RadioSelect
    )


# PAGES
class ComputerPage(Page):
    form_model = 'player'
    form_fields = ['seat', 'who']

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.who = player.who
        # print(f"{player.participant.who = }")
        player.participant.seat = player.seat
        
    
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        if player.seat == 99:
            return 'end_app'  # make sure this matches the app name in app_sequence

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
    
page_sequence = [ComputerPage,
                #  ComprehensionCheck
                 ]
