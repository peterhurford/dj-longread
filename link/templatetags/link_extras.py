from django import template

register = template.Library()


def capitalize_each(word):
    return ' '.join([w.capitalize() for w in word.split(' ')])


@register.filter
def domain(domain):
    domain = (domain.lower()
                    .replace('www.', '')
                    .replace('.com', '')
                    .replace('.org', '')
                    .replace('the', 'the '))
    domain = capitalize_each(domain)
    domain = (domain.replace('Lesswrong', 'LessWrong')
                    .replace('Forum.effectivealtruism', 'EA Forum')
                    .replace('Zenhabits.net', 'ZenHabits')
                    .replace('Nytimes', 'NYTimes')
                    .replace('Gfile.the Dispatch', 'GFile')
                    .replace('Frenchpress.the Dispatch', 'FrenchPress')
                    .replace('Whyevolutionistrue', 'WhyEvolutionIsTrue')
                    .replace('Fivethirtyeight', '538')
                    .replace('The Atlantic', 'Atlantic')
                    .replace('Benkuhn.net', 'BenKuhn')
                    .replace('Slatestarcodex', 'SlateStarCodex')
                    .replace('Projects.fivethirtyeight', '538')
                    .replace('Podcasts.apple', 'Podcast')
                    .replace('Currentaffairs', 'Current Affairs')
                    .replace('Askamathe Matician', 'Ask A Mathematician'))
    return domain
