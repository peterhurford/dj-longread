from django.db.models import Case, When, Q, FloatField


# Purge old articles after 14 days if they come from these aggregators
PURGABLE_AGGREGATORS = ['Dispatch', 'FPSecurity', 'FPChina', 'ChinAI', 'ImportAI',
                        'Alignment', 'TIB', 'Schneier', 'Yglesias', 'MLSafety']
PURGE_OLDER_THAN_X_DAYS = 14  # For PURGABLE_AGGREGATORS, remove links older than this (in days)


# Purge old articles after 90 days if they come from these aggregators
LONG_PURGABLE_AGGREGATORS = ['AskManager', 'SLW', 'CSET', 'Caplan',
                             'Sumner', 'GEMorris', 'Lusk', 'TSNR', 'GlobalGuessing',
                             'SplitTicket', 'Intelligencer', 'Guzey', 'HLI', 'EALondon',
                             'CEA', 'AlignmnentForum', 'Zvi']
LONG_PURGE_OLDER_THAN_X = 30*2  # For LONG_PURGABLE_AGGREGATORS, remove links older than this (in days)


# Purge all articles from these aggregators
OBSOLETE_AGGREGATORS = ['Freakonometrics', 'deBoer', 'MoneyIllusion', 'Faunalytics', 'Kling', 'Matuschak',
						'JPAL', 'Putanumonit', 'GPI', 'Moynihan', 'Napkin-Math', 'AnimalEthics', 'Exponents',
                        'INFERPub', 'WIP', 'JenSkerritt', 'OutbreakO', 'Wilkinson', 'FP21', 'GFI', 'Palladium',
                        'Ted', '1a3orn', 'Divinations', 'FreakTakes', 'Fyfe', 'ImpPri', 'Nadia', 'PredPol',
                        'Pseudoerasmus', 'RatlConspiracy', 'SlimeMold', 'ThinkingComplete', 'Carlsmith', 'DanWahl',
                        'EconMed', 'FHI', 'FLI', 'FPSouthAsia', 'Intelligencer', 'Mtlynch.io', 'Superorganizers',
                        'WTB', 'BenHoffman', 'CLR', 'DataColada', 'ExperimentalHistory', 'Icosian', 'Joel',
                        'Mugwump', 'NeelNanda', 'PlannedOb', 'WarOnRocks', 'DeLong', 'Nintil', 'TDS', 'Greenspun',
                        'CSET', 'Muehlhauser', 'ProgressFo', 'NakedCapitalism', 'Progress', 'SuperOrganizers',
                        'HBR', 'Seth', 'Chait', 'RAND', 'Gelman', 'SimonWilliamson', 'Leo', 'LGM', 'SSIR', '538',
                        'SupplySide', 'Graham', 'Dwarkesh', 'Elad', 'PriceTheory', 'Hanson', 'nostalgebraist',
                        'CGDev', 'Scrimshaw', 'Aarora', 'Bruers', 'Niskanen', 'Metaculus', 'AlignmentF', 'Riholtz',
                        'NotEvenWrong', 'Almanack', 'Newport', 'Vox', 'SVN', 'FPMorning', 'KenWhite', 'NewFood',
                        'FakeNous', 'WorldInData', 'EnlightementEcon', 'GEMorris', 'Mike', 'Bulletin', 'NMA',
                        'Devon', 'Gleech', 'Krugman', 'Conservable', 'DR', 'Theorem', 'NerdFitness', 'Church',
                        'GrumpyEcon', 'RibbonFarm', 'GlobalGuessing', 'ScholarsSage', 'Apricitas', 'RiversInfect',
                        'Taleb', 'JSMP', 'BLH', 'FPChina', 'Josh', 'YLEpi', 'YaschaMounk', 'Beeminder', '3P',
                        'Caplan', 'Frum', 'Gunther', 'SamAltman', 'ScholarsStage', 'Lusk', 'MOF', 'TIB',
                        'VanNostrand', 'Schneier', 'ThingOfThings', 'Danluu', 'Sumner', 'LW',
                        'Cummings', 'QuintaJurecic', 'WBW', 'BERI', 'Crawford', 'Ziggurat', 'Guzey', '80K',
                        'EconometricSense', 'TSNR', 'CH', 'IFP', 'PragCap', 'RadReads', 'Current Affairs',
                        'ALOP', 'Acton', 'Harford', '127', 'Ariely', 'Asphalt', 'Dynomight', 'Gross',
                        'Morrill', 'D4P', 'AllegedWisdom', 'Whittlestone', 'EAForum', 'Mtlynch', 'Mankiw']

# Metaweights
PRIORITY_WEIGHT = 10   # The lower this number, the more links will be ranked according
                       # to the manual preferences set in `AGGREGATOR_WEIGHTS` below.

TIME_WEIGHT = 10       # The lower this number, the more it will be the case that recent
                       # links show up first

RANDOM_WEIGHT = 35     # The lower this number, the more it will be the case that links will
                       # show up in a random order, disregarding recenty or aggregator weights

# Equation for ranking = 1 + (aggregator weight / PRIORITY_WEIGHT) +
# (id (~100K) / TIME_WEIGHT * 100) + (seed (1-100) / RANDOM_WEIGHT)


# The relative rankings of different aggregators
AGGREGATOR_WEIGHTS = Case(When(Q(aggregator__exact='Dispatch'), then=100),
                          When(Q(aggregator__exact='SLW'), then=8),
                          When(Q(aggregator__exact='SafeAI'), then=8),
                          When(Q(aggregator__exact='Bollard'), then=8),
                          When(Q(aggregator__exact='EALondon'), then=8),
                          When(Q(aggregator__exact='ChinAI'), then=8),
                          When(Q(aggregator__exact='ImportAI'), then=8),
                          When(Q(aggregator__exact='MLSafety'), then=8),
                          When(Q(aggregator__exact='FP21'), then=8),
                          When(Q(aggregator__exact='FPChina'), then=8),
                          When(Q(aggregator__exact='GCRPolicy'), then=8),
                          default=1,
                          output_field=FloatField())

