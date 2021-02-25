from django.db.models import Case, When, Q, FloatField

# Purge old articles if they come from these aggregators
PURGABLE_AGGREGATORS = ['Dispatch', 'LFaA', 'FPMorning', 'FPSecurity', 'FPChina', 'FPSouthAsia',
                        'FP-WYWL', 'MorningAg', '538', 'ChinAI']
PURGE_OLDER_THAN_X_DAYS = 5  # For PURGABLE_AGGREGATORS, remove links older than this (in days)


PRIORITY_WEIGHT = 11  # The lower this number, the more links will be ranked according
                      # to the manual preferences set in `AGGREGATOR_WEIGHTS` below.

TIME_WEIGHT = 7       # The lower this number, the more it will be the case that recent
                      # links show up first

RANDOM_WEIGHT = 70    # The lower this number, the more it will be the case that links will
                      # show up in a random order, disregarding recenty or aggregator weights


# The relative rankings of different aggregators
AGGREGATOR_WEIGHTS = Case(When(Q(aggregator__exact='Dispatch') &
                               Q(title__startswith='The Morning'), then=80),
                          When(Q(aggregator__exact='Custom'), then=20),
                          When(Q(aggregator__exact='LFaA'), then=17),
                          When(Q(aggregator__exact='FPMorning'), then=17),
                          When(Q(aggregator__exact='FPSecurity'), then=17),
                          When(Q(aggregator__exact='FPChina'), then=17),
                          When(Q(aggregator__exact='FPSouthAsia'), then=17),
                          When(Q(aggregator__exact='FP-WYWL'), then=17),
                          When(Q(aggregator__exact='MorningAg'), then=17),
                          When(Q(aggregator__exact='Bollard'), then=17),
                          When(Q(aggregator__exact='EAForum'), then=17),
                          When(Q(aggregator__exact='538'), then=17),
                          When(Q(aggregator__exact='SSC'), then=17),
                          When(Q(aggregator__exact='80K'), then=17),
                          When(Q(aggregator__exact='CEA'), then=17),
                          When(Q(aggregator__exact='Noah'), then=10),
                          When(Q(aggregator__exact='Leo'), then=10),
                          When(Q(aggregator__exact='ALOP'), then=10),
                          When(Q(aggregator__exact='Yglesias'), then=10),
                          When(Q(aggregator__exact='AI Impacts'), then=8),
                          When(Q(aggregator__exact='DanWahl'), then=8),
                          When(Q(aggregator__exact='JenSkerritt'), then=8),
                          When(Q(aggregator__exact='Lusk'), then=8),
                          When(Q(aggregator__exact='NMA'), then=8),
                          When(Q(aggregator__exact='NerdFitness'), then=8),
                          When(Q(aggregator__exact='Vox'), then=6),
                          When(Q(aggregator__exact='Dispatch'), then=6),
                          When(Q(aggregator__exact='CurrentAffairs'), then=6),
                          When(Q(aggregator__exact='LW'), then=6),
                          When(Q(aggregator__exact='Caplan'), then=6),
                          When(Q(aggregator__exact='MOF'), then=6),
                          When(Q(aggregator__exact='MR'), then=6),
                          When(Q(aggregator__exact='Rosewater'), then=6),
                          When(Q(aggregator__exact='Sumner'), then=4),
                          When(Q(aggregator__exact='D4P'), then=4),
                          When(Q(aggregator__exact='3P'), then=3),
                          default=1,
                          output_field=FloatField())

