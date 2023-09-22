from django.db.models import Case, When, Q, FloatField


# Purge old articles after 14 days if they come from these aggregators
PURGABLE_AGGREGATORS = ['Dispatch', 'FPSecurity', 'FPChina', 'ChinAI', 'ImportAI',
                        'Alignment', 'TIB', 'Schneier', 'Yglesias', 'MLSafety']
PURGE_OLDER_THAN_X_DAYS = 14


# Purge old articles after 60 days if they come from these aggregators
LONG_PURGABLE_AGGREGATORS = ['AskManager', 'SLW', 'SplitTicket', 'Noah']
LONG_PURGE_OLDER_THAN_X = 60


# Purge all articles from these aggregators
OBSOLETE_AGGREGATORS = ['CSET']

# Metaweights
PRIORITY_WEIGHT = 10   # The lower this number, the more links will be ranked according
                       # to the manual preferences set in `AGGREGATOR_WEIGHTS` below.

TIME_WEIGHT = 12       # The lower this number, the more it will be the case that recent
                       # links show up first

RANDOM_WEIGHT = 40     # The lower this number, the more it will be the case that links will
                       # show up in a random order, disregarding recenty or aggregator weights

# Equation for ranking = 1 + (aggregator weight / PRIORITY_WEIGHT) +
# (id (~100K) / TIME_WEIGHT * 100) + (seed (1-100) / RANDOM_WEIGHT)


# The relative rankings of different aggregators
AGGREGATOR_WEIGHTS = Case(When(Q(aggregator__exact='Dispatch'), then=100),
                          When(Q(aggregator__exact='SLW'), then=8),
                          When(Q(aggregator__exact='SafeAI'), then=8),
                          When(Q(aggregator__exact='Bollard'), then=8),
                          When(Q(aggregator__exact='EALondon'), then=8),
                          When(Q(aggregator__exact='NavigatingAI'), then=8),
                          When(Q(aggregator__exact='Yglesias'), then=4),
                          When(Q(aggregator__exact='SSC'), then=4),
                          When(Q(aggregator__exact='Noah'), then=4),
                          When(Q(aggregator__exact='SplitTicket'), then=4),
                          When(Q(aggregator__exact='Holden'), then=4),
                          When(Q(aggregator__exact='DeNeufville'), then=4),
                          When(Q(aggregator__exact='AI Impacts'), then=4),
                          When(Q(aggregator__exact='Rodney'), then=4),
                          When(Q(aggregator__exact='PoliticalKiwi'), then=4),
                          When(Q(aggregator__exact='Steinhardt'), then=4),
                          default=1,
                          output_field=FloatField())
