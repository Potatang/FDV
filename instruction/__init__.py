from otree.api import *


doc = """
Your app description
"""


class C(BaseConstants):
    NAME_IN_URL = 'instruction'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    seat = models.IntegerField(label='What is your seat number?', min=1, max=34)


# PAGES
class number(Page):
    form_model = 'player'
    form_fields = ['seat']


class instruction(Page):
    form_model = 'player'


page_sequence = [number, instruction]
