from django.db.models import Case, When, Q, FloatField


# Purge old articles after 14 days if they come from these aggregators
PURGABLE_AGGREGATORS = ['Dispatch', 'FPSecurity', 'FPChina', '538', 'ChinAI', 'ImportAI',
                        'Alignment', 'TIB', 'Schneier', 'Yglesias', 'MLSafety']
PURGE_OLDER_THAN_X_DAYS = 14  # For PURGABLE_AGGREGATORS, remove links older than this (in days)


# Purge old articles after 90 days if they come from these aggregators
LONG_PURGABLE_AGGREGATORS = ['AskManager', 'SLW', 'CSET', 'Caplan',
                             'Sumner', 'GEMorris', 'Lusk', 'TSNR', 'GlobalGuessing',
                             'SplitTicket', 'Intelligencer', 'Guzey', 'HLI', 'EALondon',
                             'CEA', 'AlignmnentForum', 'Zvi']
LONG_PURGE_OLDER_THAN_X = 30*2  # For LONG_PURGABLE_AGGREGATORS, remove links older than this (in days)


# Purge all articles from these aggregators
OBSOLETE_AGGREGATORS = ['Hanson', 'Guzey', 'Progress', 'ProgressFo']


# Metaweights
PRIORITY_WEIGHT = 12   # The lower this number, the more links will be ranked according
                       # to the manual preferences set in `AGGREGATOR_WEIGHTS` below.

TIME_WEIGHT = 10       # The lower this number, the more it will be the case that recent
                       # links show up first

RANDOM_WEIGHT = 33     # The lower this number, the more it will be the case that links will
                       # show up in a random order, disregarding recenty or aggregator weights

# Equation for ranking = 1 + (aggregator weight / PRIORITY_WEIGHT) +
# (id (~100K) / TIME_WEIGHT * 100) + (seed (1-100) / RANDOM_WEIGHT)


# The relative rankings of different aggregators
AGGREGATOR_WEIGHTS = Case(When(Q(aggregator__exact='Dispatch'), then=100),
                          When(Q(aggregator__exact='SLW'), then=8),
                          When(Q(aggregator__exact='Bollard'), then=8),
                          When(Q(aggregator__exact='EALondon'), then=8),
                          When(Q(aggregator__exact='SSC'), then=8),
                          When(Q(aggregator__exact='ChinAI'), then=8),
                          When(Q(aggregator__exact='ImportAI'), then=8),
                          When(Q(aggregator__exact='MLSafety'), then=8),
                          When(Q(aggregator__exact='Forecasting'), then=8),
                          When(Q(aggregator__exact='FP21'), then=8),
                          When(Q(aggregator__exact='FPChina'), then=8),
                          When(Q(aggregator__exact='FWI'), then=8),
                          When(Q(aggregator__exact='Zvi'), then=8),
                          When(Q(aggregator__exact='GlobalGuessing'), then=8),
                          When(Q(aggregator__exact='AI Impacts'), then=8),
                          When(Q(aggregator__exact='Holden'), then=8),
                          When(Q(aggregator__exact='ScholarsStage'), then=6),
                          When(Q(aggregator__exact='Noah'), then=6),
                          When(Q(aggregator__exact='FPMorning'), then=4),
                          When(Q(aggregator__exact='FPSecurity'), then=4),
                          When(Q(aggregator__exact='FPChina'), then=4),
                          When(Q(aggregator__exact='FPSouthAsia'), then=4),
                          When(Q(aggregator__exact='FP-WYWL'), then=4),
                          default=1,
                          output_field=FloatField())

