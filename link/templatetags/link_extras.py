from django import template

register = template.Library()


def capitalize_each(word):
    return ' '.join([w.capitalize() for w in word.split(' ')])


def clean(text):
    return (text.replace('&nbsp;', ' ')
                .replace('&ldquo;', '"')
                .replace('&lsquo;', '"')
                .replace('&rdquo;', '"')
                .replace('&rsquo;', '"')
                 .replace('&mdash;', ' -- ')
                 .replace('""', '"')
                 .replace('""', '"')
                 .replace('""', '"'))


@register.filter
def domain(domain):
    if not domain or domain == '':
        return ''

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


@register.filter
def summary(summary):
    if not summary or summary == '':
        return ''
    else:
        return clean(summary)


@register.filter
def title(title):
    if not title or title == '':
        return ''
    else:
        return clean(title)

