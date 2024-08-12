from django.db.models import Case, When, Q, FloatField


# Purge old articles after 14 days if they come from these aggregators
PURGABLE_AGGREGATORS = ['Dispatch', 'ImportAI', 'Noah', 'Alignment', 'Yglesias', 'MLSafety',
                        'Bollard', 'NavigatingAI', 'UnderstandingAI', 'Zvi', 'AskManager',
                        'CAIP', 'CAIS', 'Observatory', 'Punchbowl', 'Transformer',
                        'SCSP']
PURGE_OLDER_THAN_X_DAYS = 7


# Purge old articles after 60 days if they come from these aggregators
LONG_PURGABLE_AGGREGATORS = ['SLW', 'SplitTicket', 'AI Impacts', 'DeNeufville', 'ScholarsStage',
                             'SamHammond', 'SamF', 'MarkB']
LONG_PURGE_OLDER_THAN_X = 60


# Purge all articles from these aggregators
OBSOLETE_AGGREGATORS = ['AIChina', 'ChinAI', 'FPChina', 'SamAltman', 'Semianalysis']

# Metaweights
PRIORITY_WEIGHT = 18   # The lower this number, the more links will be ranked according
                       # to the manual preferences set in `AGGREGATOR_WEIGHTS` below.

TIME_WEIGHT = 12       # The lower this number, the more it will be the case that recent
                       # links show up first

RANDOM_WEIGHT = 30     # The lower this number, the more it will be the case that links will
                       # show up in a random order, disregarding recenty or aggregator weights

# Equation for ranking = 1 + (aggregator weight / PRIORITY_WEIGHT) +
# (id (~100K) / TIME_WEIGHT * 100) + (seed (1-100) / RANDOM_WEIGHT)


# The relative rankings of different aggregators
AGGREGATOR_WEIGHTS = Case(When(Q(aggregator__exact='Dispatch'), then=100),
                          When(Q(aggregator__exact='Punchbowl'), then=80),
                          When(Q(aggregator__exact='Transformer'), then=80),
                          When(Q(aggregator__exact='ImportAI'), then=50),
                          When(Q(aggregator__exact='SafeAI'), then=25),
                          When(Q(aggregator__exact='Bollard'), then=25),
                          When(Q(aggregator__exact='NavigatingAI'), then=25),
                          When(Q(aggregator__exact='Zvi'), then=25),
                          When(Q(aggregator__exact='CAIP'), then=25),
                          When(Q(aggregator__exact='CAIS'), then=25),
                          When(Q(aggregator__exact='SCSP'), then=25),
                          When(Q(aggregator__exact='UnderstandingAI'), then=25),
                          When(Q(aggregator__exact='Noah'), then=15),
                          When(Q(aggregator__exact='Yglesias'), then=15),
                          When(Q(aggregator__exact='SplitTicket'), then=15),
                          When(Q(aggregator__exact='SamF'), then=8),
                          When(Q(aggregator__exact='SamHammond'), then=8),
                          When(Q(aggregator__exact='Polymarket'), then=8),
                          When(Q(aggregator__exact='Semianalysis'), then=8),
                          When(Q(aggregator__exact='MarkB'), then=8),
                          When(Q(aggregator__exact='1a3orn'), then=6),
                          When(Q(aggregator__exact='Alignment'), then=6),
                          When(Q(aggregator__exact='MLSafety'), then=6),
                          When(Q(aggregator__exact='SSC'), then=6),
                          When(Q(aggregator__exact='AirStreet'), then=4),
                          When(Q(aggregator__exact='ConPhys'), then=4),
                          When(Q(aggregator__exact='Observatory'), then=4),
                          When(Q(aggregator__exact='DeanBall'), then=4),
                          When(Q(aggregator__exact='Statecraft'), then=4),
                          When(Q(aggregator__exact='DeNeufville'), then=4),
                          When(Q(aggregator__exact='ScholarsStage'), then=4),
                          When(Q(aggregator__exact='AskManager'), then=-5),
                          default=1,
                          output_field=FloatField())
