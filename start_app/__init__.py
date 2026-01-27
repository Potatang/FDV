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
    seat = models.IntegerField(
        blank=False,
        label='由實驗人員輸入座位電腦號碼，請參加者不要自行修改',
        min=0, max=99
    )

    # 不在頁面上顯示、由程式自動決定
    who = models.BooleanField()


# PAGES
class ComputerPage(Page):
    form_model = 'player'
    form_fields = ['seat']  # 不要顯示 who

    @staticmethod
    def before_next_page(player, timeout_happened):
        # odd seat -> advisor(True), even seat -> client(False)
        player.who = (player.seat % 2 == 1)

        player.participant.who = player.who
        player.participant.seat = player.seat

    @staticmethod
    def app_after_this_page(player, upcoming_apps):
        if player.seat == 99:
            return 'end_app'  # make sure this matches the app name in app_sequence

class RolePage(Page):
    pass

page_sequence = [ComputerPage, RolePage]
