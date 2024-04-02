from django.db.models import Case, When, Q, FloatField


# Purge old articles after 14 days if they come from these aggregators
PURGABLE_AGGREGATORS = ['Dispatch', 'FPChina', 'ChinAI', 'ImportAI',
                        'Alignment', 'TIB', 'Schneier', 'Yglesias', 'MLSafety',
                        'SafeAI', 'Bollard', 'EALondon', 'NavigatingAI',
                        'GlobalShield', 'UnderstandingAI', '3Shot', 'CSET',
                        'AIChina', 'Zvi', 'AskManager']
PURGE_OLDER_THAN_X_DAYS = 14


# Purge old articles after 60 days if they come from these aggregators
LONG_PURGABLE_AGGREGATORS = ['SLW', 'SplitTicket', 'Noah']
LONG_PURGE_OLDER_THAN_X = 60


# Purge all articles from these aggregators
OBSOLETE_AGGREGATORS = ['GlobalSheild']

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
                          When(Q(aggregator__exact='ImportAI'), then=50),
                          When(Q(aggregator__exact='SafeAI'), then=25),
                          When(Q(aggregator__exact='Bollard'), then=25),
                          When(Q(aggregator__exact='NavigatingAI'), then=25),
                          When(Q(aggregator__exact='GlobalShield'), then=25),
                          When(Q(aggregator__exact='Zvi'), then=25),
                          When(Q(aggregator__exact='CAIP'), then=25),
                          When(Q(aggregator__exact='ChinAI'), then=12),
                          When(Q(aggregator__exact='AIChina'), then=12),
                          When(Q(aggregator__exact='FPChina'), then=12),
                          When(Q(aggregator__exact='UnderstandingAI'), then=12),
                          When(Q(aggregator__exact='Noah'), then=6),
                          When(Q(aggregator__exact='Yglesias'), then=6),
                          When(Q(aggregator__exact='1a3orn'), then=6),
                          When(Q(aggregator__exact='SSC'), then=4),
                          When(Q(aggregator__exact='AskManager'), then=-5),
                          default=1,
                          output_field=FloatField())
