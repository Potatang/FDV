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
    who = models.BooleanField(label = '(限實驗人員操作，請參加者不要觸碰)', initial = True)


# PAGES
class ComputerPage(Page):
    form_model = 'player'
    form_fields = ['seat', 'who']

    # @staticmethod
    # def vars_for_template(player):
    #     print(f"{player.who = }")
    #     player.participant.who = player.who
    #     print(f"{player.participant.who = }")

    #     return dict(who=player.participant.who,
    #                 letsgo=player.letsgo,
    #                 )

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.who = player.who
        print(f"{player.participant.who = }")
    
    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        if player.seat == 99:
            return 'end_app'  # make sure this matches the app name in app_sequence

page_sequence = [ComputerPage]
