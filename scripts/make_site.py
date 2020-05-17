import pandas as pd

def clean_domain(domain):
    if isinstance(domain, str):
        domain = domain.replace('www.', '')
        domain = domain.replace('.com', '')
        domain = domain.replace('.org', '')
        domain = domain.replace('.net', '')
        domain = domain.replace('.edu', '')
        if domain == 'web.archive' or 'feedproxy' in domain or domain == 'docs.google':
            return None
        domain = domain.replace('blog.', '')
        domain = domain.replace('.wordpress', '')
        domain = domain.replace('blogspot', '')
        domain = domain.replace('substack', '')
        domain = domain.replace('github.io', '')
        domain = domain.replace('feeds', '')
        domain = domain.replace('tumblr', '')
        domain = domain.capitalize()
        domain = domain.replace('.', '')
        domain = domain.replace('-', '')
        domain = domain.replace('Forumeffectivealtruism', 'EAForum')
        domain = domain.replace('Nytimes', 'NYTimes')
        domain = domain.replace('Paulgraham', 'PaulGraham')
        domain = domain.replace('Marginalrevolution', 'MarginalRevolution')
        domain = domain.replace('Econlib', 'EconLib')
        domain = domain.replace('Hbr', 'HBR')
        domain = domain.replace('Slatestarcodex', 'SlateStarCodex')
        domain = domain.replace('Lesswrong', 'LessWrong')
        domain = domain.replace('Fivethirtyeight', '538')
        return domain
    else:
        return None

def format_link(data):
    domain = clean_domain(data['domain'])
    if domain:
        domain = ' [{}]'.format(domain)
    else:
        domain = ''
    return '<b><a href="{}">{}</a>{}</b>: {}'.format(data['url'],
                                                     data['title'],
                                                     domain,
                                                     data['summary'])

links = pd.read_csv('data/links.csv')
links = links[links['liked'] == 1]
links = links[links['summary'].apply(lambda x: isinstance(x, str))]  # Filter out empty summary
links = links.iloc[::-1]  # Reverse
categories = links.groupby('cluster')
links = links.apply(format_link, axis=1).values.tolist()

with open('site/index.html', 'w') as site:
    print('Writing index.html...')
    site.write('<head>\n')
    site.write('<title>Links</title>\n')
    site.write('<link href="style.css" rel="stylesheet" type="text/css">\n')
    site.write('</head>\n\n')
    site.write('<body>\n')
    site.write('<div id="main">\n')
    site.write('<p><em>“Everything that needs to be said has already been said. But since no one was listening, everything must be said again.”</em> ― André Gide</p>')
    site.write('<p>&nbsp;</p>')
    site.write('<p>This is my links site. It is open to the public and you can share it with anyone you want and use it however you want, but please keep in mind that it was designed with the intention to be used first and foremost as a personal reference, so I can\'t vouch for its usefulness. Note that I do not necessarially agree or fully endorse all links contained here - I just think they\'re worth thinking about.</p>')
    site.write('<p>&nbsp;</p>')
    site.write('<p><a href="categorized.html">(See these links by category)</a></p>')
    site.write('<p>&nbsp;</p>')
    site.write('<ul>\n')
    for link in links:
        site.write('  <li>{}</li>\n'.format(link))
    site.write('</ul>\n')
    site.write('</body>\n')


with open('site/categorized.html', 'w') as site:
    site.write('<head>\n')
    site.write('<title>Categorized Links</title>\n')
    site.write('<link href="style.css" rel="stylesheet" type="text/css">\n')
    site.write('</head>\n\n')
    site.write('<body>\n')
    site.write('<div id="main">\n')
    site.write('<p><em>“Everything that needs to be said has already been said. But since no one was listening, everything must be said again.”</em> ― André Gide</p>')
    site.write('<p>&nbsp;</p>')
    site.write('<p>This is my links site. It is open to the public and you can share it with anyone you want and use it however you want, but please keep in mind that it was designed with the intention to be used first and foremost as a personal reference, so I can\'t vouch for its usefulness.</p>')
    site.write('<p>&nbsp;</p>')
    site.write('<p><a href="index.html">(See these links by most recently added)</a>')
    site.write('<p>&nbsp;</p>')
    site.write('<h2>Table of Contents</h2>\n')
    site.write('<ul>\n')
    for name, group in categories:
        site.write('<li><a href="#{}">{}</a></li>\n'.format(name, name.capitalize()))
    site.write('</ul>\n')
    for name, group in categories:
        print('Writing categorized.html, {}...'.format(name))
        site.write('\n<a id="{}"><h2>{}</h2></a>\n'.format(name, name.capitalize()))
        site.write('<ul>\n')
        for link in group.iterrows():
            site.write('  <li>{}</li>\n'.format(format_link(link[1])))
        site.write('</ul>\n')
    site.write('</body>\n')

print('Done!')
