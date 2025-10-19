from os import environ


SESSION_CONFIGS = [
    dict(
        name='FDI',
        num_demo_participants=2,
        app_sequence=['start_app',
                        'moralcost_IF',
                        'choice',
                        'experiment_IF',
                        'moralcost2',
                        'guessquality_IF',
                        'guessproportion_IF',
                        'end_app'
                        ],
    ),
]
# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=5.00, participation_fee=250, doc=""
)

PARTICIPANT_FIELDS = dict(
    who = int(),
    seat = int(),
    experiment_payoff = int(),
    part2_payoff = int(),
    part4_belief = int(),
    moralcost_payoff = int(),
    choice_payoff = int(),
    total_payoff = int(),
    twd_payoff = int(),
)
SESSION_FIELDS = []

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'zh-tw'

# e.g. EUR, GBP, CNY, JPY
USE_POINTS = True
POINTS_CUSTOM_NAME = '法幣'

ROOMS = [
    dict(
        name='econ101',
        display_name='Econ 101 class',
        participant_label_file='_rooms/econ101.txt',
    ),
    dict(name='live_demo', display_name='Room for live demo (no participant labels)'),
]

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """
Here are some oTree games.
"""


SECRET_KEY = '4417453228424'

INSTALLED_APPS = ['otree']
