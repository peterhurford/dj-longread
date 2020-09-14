from django.db.models import Case, When, Q, FloatField


PRIORITY_WEIGHT = 15  # The lower this number, the more links will be ranked according
                      # to the manual preferences set in `AGGREGATOR_WEIGHTS` below.

TIME_WEIGHT = 15      # The lower this number, the more it will be the case that recent
                      # links show up first

RANDOM_WEIGHT = 50    # The lower this number, the more it will be the case that links will
                      # show up in a random order, disregarding recenty or aggregator weights

# The relative rankings of different aggregators
AGGREGATOR_WEIGHTS = Case(When(Q(aggregator__exact='LFaA'), then=40),
                          When(Q(aggregator__exact='FPMorning'), then=40),
                          When(Q(aggregator__exact='FPSecurity'), then=40),
                          When(Q(aggregator__exact='FPChina'), then=40),
                          When(Q(aggregator__exact='FPSouthAsia'), then=40),
                          When(Q(aggregator__exact='FP-WYWL'), then=40),
                          When(Q(aggregator__exact='MorningAg'), then=40),
                          When(Q(aggregator__exact='Dispatch') &
                               Q(title__startswith='The Morning'), then=40),
                          When(Q(aggregator__exact='Custom'), then=25),
                          When(Q(aggregator__exact='EAForum'), then=15),
                          When(Q(aggregator__exact='538'), then=15),
                          When(Q(aggregator__exact='SSC'), then=14),
                          When(Q(aggregator__exact='80K'), then=14),
                          When(Q(aggregator__exact='CEA'), then=14),
                          When(Q(aggregator__exact='Noah'), then=10),
                          When(Q(aggregator__exact='AI Impacts'), then=8),
                          When(Q(aggregator__exact='DanWahl'), then=8),
                          When(Q(aggregator__exact='JenSkerritt'), then=8),
                          When(Q(aggregator__exact='Lusk'), then=8),
                          When(Q(aggregator__exact='Leo'), then=8),
                          When(Q(aggregator__exact='NMA'), then=8),
                          When(Q(aggregator__exact='NerdFitness'), then=8),
                          When(Q(aggregator__exact='ALOP'), then=8),
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
