from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'moralcost'
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


class Subsession(BaseSubsession):
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

    moralcost_payoff = models.CurrencyField(initial=0)
    total_payoff = models.CurrencyField(initial=0)

    age = models.IntegerField(
        min = 0,
        max = 99,
        label = '請問您的年齡是',
    )

    gender = models.IntegerField(
        choices = [
              [0,'女'], [1,'男'],
        ],
        label = '請問您的生理性別為？',
    )

    grade = models.IntegerField(
        choices = [
            [1,'大一'],
            [2,'大二'],
            [3,'大三'],
            [4,'大四'],
            [5,'碩一'],
            [6,'碩二'],
            [7,'其他'],
            [8,'不便透露']
        ],
        widget = widgets.RadioSelectHorizontal,
        label = '請問您的年級?'
    )
    grade_other = models.StringField(
        blank=True,
        label='請輸入您的年級（若選擇了「其他」請填寫）'
    )

    major = models.IntegerField(
        choices = [
            [1,'文學院'],
            [2,'理學院'],
            [3,'社會科學院'],
            [4,'醫學院'],
            [5,'工學院'],
            [6,'生物資源暨農學院'],
            [7,'管理學院'],
            [8,'公共衛生學院'],
            [9,'電機資訊學院'],
            [10,'法律學院'],
            [11,'生命科學院'],
            [12,'其他'],
            [13,'不便透露']
        ],
        widget = widgets.RadioSelectHorizontal,
        label = '請問您主修的科系所屬的學院為? '
    )
    major_other = models.StringField(
        blank=True,
        label='請輸入您的所屬院系（若選擇了「其他」請填寫）'
    )

    income = models.IntegerField(
        choices = [
            [1,'3,000 元及以下'],
            [2,'3,001-6,000 元'],
            [3,'6,001-9,000 元'],
            [4,'9,001-12,000 元'],
            [5,'12,001-15,000 元'],
            [6,'15,001-18000 元'],
            [7,'18,001-21,000 元'],
            [8,'21,000 元以上'],
            [9,'不便透露']
        ],
        widget = widgets.RadioSelectHorizontal,
        label = '請問您個人平均每月可支配的金錢?? '
    )

    hometown = models.IntegerField(
        choices = [
            [1,'北部地區 【苗栗以北】'],
            [2,'中部地區 【台中至雲林】'],
            [3,'南部地區 【嘉義至恆春】'],
            [4,'東部、外島地區'],
            [5,'其他'],
            [6,'不便透露'],
        ],
        widget = widgets.RadioSelectHorizontal,
        label = '請問您的居住縣市為?'
    )
    hometown_other = models.StringField(
        blank=True,
        label='請輸入您的居住縣市（若選擇了「其他」請填寫）'
    )

    religion = models.IntegerField(
        choices = [
            [1,'佛教，有皈依'],
            [2,'佛教，未皈依'],
            [3,'道教'],
            [4,'民間信仰'],
            [5,'一貫道'],
            [6,'回教（伊斯蘭教）'],
            [7,'天主教'],
            [8,'基督教'],
            [9,'其他信仰'],
            [10,'無信仰'],
            [11,'不便透露']
        ],
        widget = widgets.RadioSelectHorizontal,
        label = '請問您目前的宗教信仰?'
    )
    religion_other = models.StringField(
        blank=True,
        label='請輸入您的宗教信仰（若選擇了「其他」請填寫）'
    )

    reason1= models.LongStringField(
        blank = False,
        label = '當您必須在產品 A 和產品 B 之間做出選擇時，你是如何決定要推薦哪一個的？',
    )

    choice = models.IntegerField(
        choices = [
            [0,'會'],
            [1,'不會']
        ],
        widget = widgets.RadioSelectHorizontal,
        label = '整體而言您是否會按照收到的推薦進行選擇？',
    )
    reason2 = models.StringField(
        blank=True,
        label='若您不會，請問原因為何？'
    )

    email = models.StringField(
        label="請輸入你常用的 Email(若領款資訊有任何問題，報帳人員將以此方式聯絡您。)",
        blank=False,
        # 自訂驗證函數
        validate=lambda email: (
            "請輸入有效的 Email 地址"
            if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)
            else None
        )
    )

    name = models.StringField(
        label="姓名",
        blank=False,
    )

    id_number = models.StringField(
        label="身分證字號",
        blank=False,
        validate=lambda s: (
            "請輸入有效的身分證字號"
            if not re.match(r'^[A-Z][12]\d{8}$', s.upper())
            else None
        )
    )

    student_id = models.StringField(
        label="學號",
        blank=False,
    )

    zipcode = models.StringField(
        label="郵遞區號",
        blank=False,
        validate=lambda z: (
            "請輸入 3 或 5 碼的郵遞區號"
            if not re.match(r'^\d{3}(\d{2})?$', z)
            else None
        )
    )

    address = models.LongStringField(
        label="戶籍地址(須與身分證背面之住址一致)",
        blank=False,
    )

def set_payoffs(group: Group):   
    for p in group.get_players():
        p.moralcost_payoff = cu(0)
        
        if p.role == C.ADVISOR_ROLE:
            recommendations = [
                p.recommendation1,
                p.recommendation2,
                p.recommendation3,
                p.recommendation4,
                p.recommendation5,
            ]

            import random
            # 從中隨機抽取一個
            chosen_recommendation = random.choice(recommendations)
            print(f"{chosen_recommendation = }")

            # 根據推薦內容給報酬
            if chosen_recommendation == 'X':
                p.moralcost_payoff = cu(0)
            elif chosen_recommendation == 'Y':
                p.moralcost_payoff = cu(5)
            else:
                p.moralcost_payoff = cu(0)  # fallback，萬一沒有選到有效選項
        elif p.role == C.CLIENT_ROLE:
            pass
        
        p.participant.moralcost_payoff = p.moralcost_payoff 

# PAGES
class InstructionPage(Page):
    
    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE

class RecommendationPage(Page):

    form_model = 'player'
    form_fields = ['recommendation1', 'recommendation2', 'recommendation3', 'recommendation4', 'recommendation5']

    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE
    
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


class QuestionnairePage(Page):

    form_model = 'player'

    @staticmethod
    def get_form_fields(player):
        fields = [
            'age', 'gender', 'grade', 'grade_other',
            'major', 'major_other', 'income',
            'hometown', 'hometown_other',
            'religion', 'religion_other'
        ]
        if player.role == C.ADVISOR_ROLE:
            fields.append('reason1')
        elif player.role == C.CLIENT_ROLE:
            fields.append('choice')
            fields.append('reason2')
        return fields
    
    @staticmethod
    def error_message(player, values):
        errors = []

        if values['grade'] == 7 and not values['grade_other']:
            errors.append('請在選擇「其他」後填寫您的年级')

        if values['major'] == 12 and not values['major_other']:
            errors.append('請在選擇「其他」後填寫您的所屬院系')

        if values['hometown'] == 5 and not values['hometown_other']:
            errors.append('請在選擇「其他」後填寫您的居住縣市')

        if values['religion'] == 9 and not values['religion_other']:
            errors.append('請在選擇「其他」後填寫您的宗教信仰')

        if player.role == C.CLIENT_ROLE and values['choice'] == 1 and not values['reason2']:
            errors.append('請在選擇「不會」後填寫您的原因')

        return errors if errors else None

class ResultsWaitPage(WaitPage):    
    @staticmethod
    def is_displayed(player):
        return player.role == C.ADVISOR_ROLE
    
    after_all_players_arrive = set_payoffs

class ReceiptPage(Page):

    form_model = 'player'
    form_fields = ['email', 'name', 'id_number', 'student_id', 'zipcode', ]

    @staticmethod
    def vars_for_template(player):
        player.total_payoff = player.participant.experiment_payoff + player.participant.moralcost_payoff
        player.participant.total_payoff = player.total_payoff
        
        return dict(experiment_payoff=player.participant.experiment_payoff,
                    moralcost_payoff=player.participant.moralcost_payoff,
                    total_payoff=player.participant.total_payoff)

page_sequence = [InstructionPage, RecommendationPage, ResultsWaitPage, QuestionnairePage, ReceiptPage]
