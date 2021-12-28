from django.db.models import Case, When, Q, FloatField

# Purge old articles if they come from these aggregators
PURGABLE_AGGREGATORS = ['Dispatch', 'LFaA', 'FPMorning', 'FPSecurity', 'FPChina', 'FPSouthAsia',
                        'FP-WYWL', 'MorningAg', '538', 'ChinAI', 'ImportAI', 'Alignment',
                        'Chait', 'TIB', 'Schneier']
PURGE_OLDER_THAN_X_DAYS = 5  # For PURGABLE_AGGREGATORS, remove links older than this (in days)


# Purge all articles from these aggregators
OBSOLETE_AGGREGATORS = ['WBW', 'Frum', 'Gunther', 'PossiblyWrong', 'Scrimshaw']

# Metaweights
PRIORITY_WEIGHT = 10   # The lower this number, the more links will be ranked according
                       # to the manual preferences set in `AGGREGATOR_WEIGHTS` below.

TIME_WEIGHT = 8        # The lower this number, the more it will be the case that recent
                       # links show up first

RANDOM_WEIGHT = 35     # The lower this number, the more it will be the case that links will
                       # show up in a random order, disregarding recenty or aggregator weights

# Equation for ranking = 1 + (aggregator weight / PRIORITY_WEIGHT) +
# (id (~100K) / TIME_WEIGHT * 100) + (seed (1-100) / RANDOM_WEIGHT)


# The relative rankings of different aggregators
AGGREGATOR_WEIGHTS = Case(When(Q(aggregator__exact='Dispatch') &
                               Q(title__startswith='The Morning'), then=100),
                          When(Q(aggregator__exact='HIPR'), then=12),
                          When(Q(aggregator__exact='EAForum'), then=12),
                          When(Q(aggregator__exact='SLW'), then=10),
                          When(Q(aggregator__exact='LW'), then=10),
                          When(Q(aggregator__exact='SuperOrganizers'), then=10),
                          When(Q(aggregator__exact='Bollard'), then=10),
                          When(Q(aggregator__exact='SSC'), then=10),
                          When(Q(aggregator__exact='ChinAI'), then=8),
                          When(Q(aggregator__exact='ImportAI'), then=8),
                          When(Q(aggregator__exact='Alignment'), then=8),
                          When(Q(aggregator__exact='GlobalGuessing'), then=6),
                          When(Q(aggregator__exact='AI Impacts'), then=6),
                          When(Q(aggregator__exact='ScholarsStage'), then=6),
                          When(Q(aggregator__exact='PoliticalKiwi'), then=6),
                          When(Q(aggregator__exact='WorldInData'), then=6),
                          When(Q(aggregator__exact='80K'), then=6),
                          When(Q(aggregator__exact='CEA'), then=6),
                          When(Q(aggregator__exact='Holden'), then=6),
                          When(Q(aggregator__exact='Lusk'), then=4),
                          When(Q(aggregator__exact='Guzey'), then=4),
                          When(Q(aggregator__exact='Noah'), then=4),
                          When(Q(aggregator__exact='FPMorning'), then=4),
                          When(Q(aggregator__exact='FPSecurity'), then=4),
                          When(Q(aggregator__exact='FPChina'), then=4),
                          When(Q(aggregator__exact='FPSouthAsia'), then=4),
                          When(Q(aggregator__exact='FP-WYWL'), then=4),
                          When(Q(aggregator__exact='Dispatch'), then=0.5),
                          When(Q(aggregator__exact='HBR'), then=0.5),
                          When(Q(aggregator__exact='Custom'), then=0.0001),
                          default=1,
                          output_field=FloatField())

