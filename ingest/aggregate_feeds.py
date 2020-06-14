import time
import random
import psycopg2

import pandas as pd

from datetime import datetime, timedelta
from mlgear.utils import chunk

from utils.download import read
from utils.ingest import clean_url, get_root_url
from utils.sql import table_exists, drop_table, escape, enquote, add_row, delete_row, find_row


# DRY with scripts/import_onetab.py
ALL_COLS = ['id', 'url', 'title', 'summary', 'domain', 'added', 'modified',
            'liked', 'benched', 'category', 'aggregator']


def add_link_row(cur, content):
    add_row(cur,
            'link_link',
            ['title', 'url', 'aggregator', 'added', 'modified', 'benched'],
            [enquote(c) for c in content + [str(datetime.now())] * 2] + [enquote('0')])
    return None


def delete_link_row(cur, url):
    delete_row(cur, 'link_link', 'url', enquote(url))
    return None


def find_link_row(cur, url):
    result = find_row(cur, 'link_link', 'url', url, n='many')
    if result:
        return [dict(zip(ALL_COLS, r)) for r in result]
    else:
        return []


contents = []


print('Load HN...')
content, error, msg = read('https://news.ycombinator.com/rss', return_type='list', reader_type='xml')
if error:
    print(msg)
else:
    content = chunk(content[3:], 5)
    content = [c[:2] for c in content]
    content = [[c[0], c[1], 'HN'] for c in content]
    contents += content

print('Load Vox...')
content2, error, msg = read('https://www.vox.com/rss/index.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content2 = content2.find_all('entry')
    content2 = [[c.title.get_text(), c.id.get_text(), 'Vox'] for c in content2]
    contents += content2

print('Load SSC...')
content6, error, msg = read('https://slatestarcodex.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content6 = content6.find_all('item')
    content6 = [[c.title.get_text(), c.link.get_text(), 'SSC'] for c in content6]
    contents += content6

print('Load EA Blogs...')
content3, error, msg = read('http://eablogs.net', return_type='soup')
if error:
    print(msg)
else:
    content3 = content3.find_all('ul')[0]
    content3 = [str(c.a).split('href="')[1].split('rel=') for c in content3.find_all('li')]
    content3 = [[c[1].split('>')[1].split('<')[0],
                 c[0].replace('"', '').strip(),
                 'EABlogs'] for c in content3]
    contents += content3

print('Load LW Curated...')
content4, error, msg = read('https://www.lesswrong.com/feed.xml?view=curated-rss', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content4 = content4.find_all('item')
    content4 = [[c.title.get_text(), c.link.get_text(), 'LW'] for c in content4]
    contents += content4

print('Load 538 Politics...')
content5, error, msg = read('https://fivethirtyeight.com/politics/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content5 = content5.find_all('item')
    content5 = [[c.title.get_text(), c.link.get_text(), '538'] for c in content5]
    contents += content5

print('Load Jason Lusk...')
content7, error, msg = read('http://jaysonlusk.com/blog?format=rss', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content7 = content7.find_all('item')
    content7 = [[c.title.get_text(), c.link.get_text(), 'Lusk'] for c in content7]
    contents += content7

print('Load Bryan Caplan...')
content8, error, msg = read('https://www.econlib.org/feed/indexCaplan_xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content8 = content8.find_all('item')
    content8 = [[c.title.get_text().replace(', by Bryan Caplan', ''), c.link.get_text(), 'Caplan'] for c in content8]
    contents += content8

print('Load Mankiw...')
content9, error, msg = read('http://feeds.feedburner.com/blogspot/SOpj?format=xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content9 = content9.find_all('item')
    content9 = [[c.title.get_text(), c.link.get_text(), 'Mankiw'] for c in content9]
    contents += content9

print('Load AI Impacts...')
content10, error, msg = read('https://aiimpacts.org/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content10 = content10.find_all('item')
    content10 = [[c.title.get_text(), c.link.get_text(), 'AI Impacts'] for c in content10]
    contents += content10

print('Load Ben Kuhn...')
content11, error, msg = read('https://www.benkuhn.net/rss/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content11 = content11.find_all('entry')
    content11 = [[c.title.get_text(), str(c.link).split('"')[1], 'Ben Kuhn'] for c in content11]
    contents += content11

print('Load Scott Young...')
content12, error, msg = read('http://feeds.feedburner.com/scotthyoung/HAHx', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content12 = content12.find_all('item')
    content12 = [[c.title.get_text(), c.link.get_text(), 'Scott Young'] for c in content12]
    contents += content12

print('Load Current Affairs...')
content13, error, msg = read('https://www.currentaffairs.org', return_type='soup')
if error:
    print(msg)
else:
    content13 = content13.find_all('a')
    content13 = [str(a).split('"') for a in content13]
    content13 = [[a[1], a[2]] for a in content13 if len(a) == 3 and 'author' not in a[1]]
    content13 = content13[2:]
    content13 = [[a[1].replace('</a>', '').replace('>', ''),
                 'https://www.currentaffairs.org' + a[0],
                 'Current Affairs'] for a in content13]
    contents += content13

print('Load Mtlynch.io...')
content14, error, msg = read('https://mtlynch.io/feed.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content14 = content14.find_all('entry')
    content14 = [[c.title.get_text(),
                  str(c.link).split('"')[1],
                  'Mtlynch'] for c in content14]
    contents += content14

print('Load Beeminder...')
content15, error, msg = read('http://feeds.feedburner.com/bmndr', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content15 = content15.find_all('item')
    content15 = [[c.title.get_text(), c.link.get_text(), 'Beeminder'] for c in content15]
    contents += content15

print('Load Katherine Savoie...')
content16, error, msg = read('https://www.deliberatehappiness.com/1/feed', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content16 = content16.find_all('item')
    content16 = [[c.title.get_text(), c.link.get_text(), 'KatherineSavoie'] for c in content16]
    contents += content16

print('Load Mr. Money Mustache...')
content17, error, msg = read('https://feeds.feedburner.com/mrmoneymustache', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content17 = content17.find_all('item')
    content17 = [[c.title.get_text(), c.link.get_text(), 'MMM'] for c in content17]
    contents += content17

print('Load Sarah Constantin...')
content18, error, msg = read('https://srconstantin.wordpress.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content18 = content18.find_all('item')
    content18 = [[c.title.get_text(), c.link.get_text(), 'Constantin'] for c in content18]
    contents += content18

print('Load Marginal Revolution...')
content19, error, msg = read('http://feeds.feedburner.com/marginalrevolution/feed', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content19 = content19.find_all('item')
    content19 = [[c.title.get_text(), c.link.get_text(), 'MR'] for c in content19]
    contents += content19

print('Load Tyler Bloomberg...')
content107, error, msg = read('https://www.bloomberg.com/opinion/authors/AS6n2t3d_iA/tyler-cowen.rss', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content107 = content107.find_all('item')
    content107 = [[c.title.get_text(), c.link.get_text(), 'MR'] for c in content107]
    contents += content107

print('Load Roots of Progress...')
content20, error, msg = read('https://rootsofprogress.org/posts', return_type='soup')
if error:
    print(msg)
else:
    content20 = content20.find_all('li')
    content20 = [c.find_all('a') for c in content20]
    content20 = [str(c).split('"')[3:5] for c in content20]
    content20 = [[c[1].replace('</a>', '').replace('>', ''),
                  'http://www.rootsofprogress.org' + c[0], 'Progress'] for c in content20]
    contents += content20

print('Load PhilosophyEtc...')
content21, error, msg = read('http://feeds.philosophyetc.net/PhilosophyEtCetera', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content21 = content21.find_all('entry')
    content21 = [[c.title.get_text(), str(c.find_all('link')[-1]).split('"')[1], 'PhilosophyEtc'] for c in content21]
    contents += content21

print('Load Melting Asphalt...')
content22, error, msg = read('https://meltingasphalt.com/archive/', return_type='soup')
if error:
    print(msg)
else:
    content22 = [str(c) for c in content22.find_all('a') if 'bookmark' in str(c)]
    content22 = [c.split('"') for c in content22]
    content22 = [[c[6].replace('</a>', '').replace('>', ''), c[3], 'Asphalt'] for c in content22]
    contents += content22

print('Load Paul Graham...')
content23, error, msg = read('http://paulgraham.com/articles.html', return_type='soup')
if error:
    print(msg)
else:
    content23 = [str(c).split('"') for c in content23.find_all('a')]
    content23 = [[c[2].replace('</a>', '').replace('>', ''), 'http://paulgraham.com/' + c[1], 'Graham'] for c in content23]
    content23 = content23[6:-1]
    contents += content23

print('Load Joel on Software...')
content23, error, msg = read('https://www.joelonsoftware.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content23 = [str(c).split('"') for c in content23.find_all('a')]
    content23 = [[c[2].replace('</a>', '').replace('>', ''), 'http://paulgraham.com/' + c[1], 'Graham'] for c in content23]
    content23 = content23[6:-1]
    contents += content23

print('Load ALOP...')
content24, error, msg = read('https://alifeofproductivity.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content24 = content24.find_all('item')
    content24 = [[c.title.get_text(), c.link.get_text(), 'ALOP'] for c in content24]
    contents += content24

print('Load Dinsmore...')
content25, error, msg = read('https://thomaswdinsmore.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content25 = content25.find_all('item')
    content25 = [[c.title.get_text(), c.link.get_text(), 'Dinsmore'] for c in content25]
    contents += content25

print('Load Hanson...')
content26, error, msg = read('http://www.overcomingbias.com/feed', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content26 = content26.find_all('item')
    content26 = [[c.title.get_text(), c.link.get_text(), 'Hanson'] for c in content26]
    contents += content26

print('Load Muehlhauser...')
content28, error, msg = read('http://feeds.feedburner.com/LukeMuehlhauser', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content28 = content28.find_all('entry')
    content28 = [[c.title.get_text(), str(c.link).split('"')[1], 'Muehlhauser'] for c in content28]
    contents += content28

print('Load Leo...')
content29, error, msg = read('https://zenhabits.net/archives/', return_type='soup')
if error:
    print(msg)
else:
    content29 = [str(c).split('"') for c in content29.find_all('a')]
    content29 = [[c[2].replace('</a>', '').replace('>', '').replace('\n', ''), c[1], 'Leo'] for c in content29]
    content29 = content29[2:]
    contents += content29

print('Load WBW...')
content30, error, msg = read('https://waitbutwhy.com/archive', return_type='soup')
if error:
    print(msg)
else:
    content30 = content30.find_all('h5')
    content30 = [c.find_all('a')[0] for c in content30]
    content30 = [str(c).split('"')[1:3] for c in content30]
    content30 = [[c[1].replace('>\r\n', '').replace('\t', '').replace('\n', '').replace('</a>', '').replace('>', ''), c[0], 'WBW'] for c in content30]
    contents += content30

print('Load Cummings...')
content31, error, msg = read('https://dominiccummings.com/', return_type='soup')
if error:
    print(msg)
else:
    content31 = content31.find_all('h1')
    content31 = [c.find_all('a') for c in content31]
    content31 = [c for c in content31 if 'bookmark' in str(c) and c != []]
    content31 = [str(c).split('"') for c in content31]
    content31 = [[c[4].replace('</a>', '').replace('>', '').replace(']', ''), c[1], 'Cummings'] for c in content31]
    contents += content31

print('Load D4P Memos...')
content32, error, msg = read('https://www.dataforprogress.org/memos', return_type='soup')
if error:
    print(msg)
else:
    content32 = content32.find_all('a')
    content32 = [str(c).split('"') for c in content32 if 'BlogList-item' in str(c)]
    content32 = [c for c in content32 if len(c) == 7]
    content32 = [[c[6].replace('</a>', '').replace('>', ''), 'https://www.dataforprogress.org' + c[5], 'D4P'] for c in content32]
    contents += content32

print('Load D4P Blog...')
content33, error, msg = read('https://www.dataforprogress.org/blog', return_type='soup')
if error:
    print(msg)
else:
    content33 = content33.find_all('a')
    content33 = [str(c).split('"') for c in content33 if 'BlogList-item' in str(c)]
    content33 = [c for c in content33 if len(c) == 7]
    content33 = [[c[6].replace('</a>', '').replace('>', ''), 'https://www.dataforprogress.org' + c[5], 'D4P'] for c in content33]
    contents += content33

print('Load Rosewater...')
content34, error, msg = read('https://magic.wizards.com/en/articles/columns/making-magic', return_type='soup')
if error:
    print(msg)
else:
    content34 = content34.find_all('a')
    content34 = [c for c in content34 if 'articles' in str(c)][1:-2]
    content34 = [[c.find_all('h3')[0].get_text(),
                  'https://magic.wizards.com' + str(c).split('"')[1], 'Rosewater']
                 for c in content34]
    contents += content34

print('Load Levels...')
content35, error, msg = read('https://levels.io/rss/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content35 = content35.find_all('item')
    content35 = [[c.title.get_text(), c.link.get_text(), 'Levels'] for c in content35]
    contents += content35

print('Load TSNR...')
content36, error, msg = read('https://tnsr.org/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content36 = content36.find_all('item')
    content36 = [[c.title.get_text(), c.link.get_text(), 'TSNR'] for c in content36]
    contents += content36

print('Load Acton...')
content37, error, msg = read('https://carnegieendowment.org/experts/tabs/opinion/434', return_type='soup')
if error:
    print(msg)
else:
    content37 = content37.find_all('a')
    content37 = [str(c).split('"') for c in content37[:-4]]
    content37 = [[c[2].replace('</a>', '').replace('>', ''),
                  'https://carnegieendowment.org' + c[1], 'Acton'] for c in content37]
    contents += content37

print('Load Noah Blog...')
content39, error, msg = read('http://noahpinionblog.blogspot.com/feeds/posts/default', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content39 = content39.find_all('entry')
    content39 = [[c.title.get_text(), str(c.find_all('link')[-1]).split('"')[1], 'Noah'] for c in content39]
    contents += content39

print('Load Noah Bloomberg...')
content106, error, msg = read('https://www.bloomberg.com/opinion/authors/AR3OYuAmvcU/noah-smith.rss', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content106 = content106.find_all('item')
    content106 = [[c.title.get_text(), c.link.get_text(), 'Noah'] for c in content106]
    contents += content106

print('Load Ariely...')
content40, error, msg = read('http://danariely.com/resources/the-blog/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content40 = content40.find_all('item')
    content40 = [[c.title.get_text(), c.link.get_text(), 'Ariely'] for c in content40]
    contents += content40

print('Load NotEvenWrong...')
content41, error, msg = read('http://www.math.columbia.edu/~woit/wordpress/?feed=rss2', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content41 = content41.find_all('item')
    content41 = [[c.title.get_text(), c.link.get_text(), 'NotEvenWrong'] for c in content41]
    contents += content41

print('Load Chait...')
content42, error, msg = read('http://nymag.com/author/jonathan-chait/', return_type='soup')
if error:
    print(msg)
else:
    content42 = [d for d in content42.find_all('div') if 'the national interest' in str(d)][0]
    content42 = content42.find_all('a')[:-1]
    content42 = [str(c).split('"') for c in content42]
    content42 = [[c[6].replace('</span></a>', '').replace('>', ''), c[3], 'Chait'] for c in content42]
    contents += content42

print('Load 3P...')
content43, error, msg = read('https://www.peoplespolicyproject.org/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content43 = content43.find_all('item')
    content43 = [[c.title.get_text(), c.link.get_text(), '3P'] for c in content43]
    contents += content43

print('Load DeLong...')
content44, error, msg = read('https://www.bradford-delong.com/atom.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content44 = content44.find_all('entry')
    content44 = [[c.title.get_text(), str(c.link).split('"')[1], 'DeLong'] for c in content44]
    contents += content44

print('Load Gunther...')
content45, error, msg = read('https://medium.com/feed/@marcgunther', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content45 = content45.find_all('item')
    content45 = [[c.title.get_text(), c.link.get_text().replace('?source=rss-8e6c9c00a22b------2', ''), 'Gunther'] for c in content45]
    contents += content45

print('Load ImportAI...')
content46, error, msg = read('https://jack-clark.net/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content46 = content46.find_all('item')
    content46 = [[c.title.get_text(), c.link.get_text(), 'ImportAI'] for c in content46]
    contents += content46

print('Load MoneyIllusion...')
content47, error, msg = read('http://feeds.feedburner.com/Themoneyillusion', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content47 = content47.find_all('item')
    content47 = [[c.title.get_text(), c.link.get_text(), 'MoneyIllusion'] for c in content47]
    contents += content47

print('Load AllegedWisdom...')
content48, error, msg = read('http://allegedwisdom.blogspot.com/feeds/posts/default', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content48 = content48.find_all('entry')
    content48 = [[c.title.get_text(), str(c.find_all('link')[-1]).split('"')[1], 'AllegedWisdom'] for c in content48]
    contents += content48

print('Load Mike...')
content49, error, msg = read('https://mikethemadbiologist.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content49 = content49.find_all('item')
    content49 = [[c.title.get_text(), c.link.get_text(), 'Mike'] for c in content49]
    contents += content49

print('Load Gelman...')
content50, error, msg = read('https://statmodeling.stat.columbia.edu/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content50 = content50.find_all('item')
    content50 = [[c.title.get_text(), c.link.get_text(), 'Gelman'] for c in content50]
    contents += content50

print('Load EconometricSense...')
content51, error, msg = read('http://econometricsense.blogspot.com/feeds/posts/default', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content51 = content51.find_all('entry')
    content51 = [[c.title.get_text(), str(c.find_all('link')[-1]).split('"')[1], 'EconometricSense'] for c in content51]
    contents += content51

print('Load Freakonometrics...')
content52, error, msg = read('https://freakonometrics.hypotheses.org/feed', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content52 = content52.find_all('item')
    content52 = [[c.title.get_text(), c.link.get_text(), 'Freakonometrics'] for c in content52]
    contents += content52

print('Load Riholtz...')
content53, error, msg = read('https://ritholtz.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content53 = content53.find_all('item')
    content53 = [[c.title.get_text(), c.link.get_text(), 'Riholtz'] for c in content53]
    contents += content53

print('Load PragCap...')
content54, error, msg = read('https://www.pragcap.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content54 = content54.find_all('item')
    content54 = [[c.title.get_text(), c.link.get_text(), 'PragCap'] for c in content54]
    contents += content54

print('Load NakedCapitalism...')
content55, error, msg = read('https://www.nakedcapitalism.com/feed', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content55 = content55.find_all('item')
    content55 = [[c.title.get_text(), c.link.get_text(), 'NakedCapitalism'] for c in content55]
    contents += content55

print('Load Conservable...')
content56, error, msg = read('http://conversableeconomist.blogspot.com/feeds/posts/default', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content56 = content56.find_all('entry')
    content56 = [[c.title.get_text(), str(c.find_all('link')[-1]).split('"')[1], 'Conservable'] for c in content56]
    contents += content56

print('Load Harford...')
content57, error, msg = read('http://timharford.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content57 = content57.find_all('item')
    content57 = [[c.title.get_text(), c.link.get_text(), 'Harford'] for c in content57]
    contents += content57

print('Load Krugman...')
content58, error, msg = read('http://www.nytimes.com/svc/collections/v1/publish/www.nytimes.com/column/paul-krugman/rss.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content58 = content58.find_all('item')
    content58 = [[c.title.get_text(), c.link.get_text(), 'Krugman'] for c in content58]
    contents += content58

print('Load Fyfe...')
content59, error, msg = read('http://feeds.feedburner.com/blogspot/inod', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content59 = content59.find_all('item')
    content59 = [[c.title.get_text(), c.link.get_text(), 'Fyfe'] for c in content59]
    contents += content59

print('Load VoxEU...')
content60, error, msg = read('https://voxeu.org/feed/recent/rss.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content60 = content60.find_all('item')
    content60 = [[c.title.get_text(), c.link.get_text(), 'VoxEU'] for c in content60]
    contents += content60

print('Load EnlightenmentEcon...')
content61, error, msg = read('http://www.enlightenmenteconomics.com/blog/index.php/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content61 = content61.find_all('item')
    content61 = [[c.title.get_text(), c.link.get_text(), 'EnlightementEcon'] for c in content61]
    contents += content61

print('Load Schneier...')
content62, error, msg = read('https://www.schneier.com/blog/atom.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content62 = content62.find_all('entry')
    content62 = [[c.title.get_text(), str(c.link).split('"')[1], 'Schneier'] for c in content62]
    contents += content62

print('Load Christian Rationalist...')
content63, error, msg = read('https://thechristianrationalist.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content63 = content63.find_all('item')
    content63 = [[c.title.get_text(), c.link.get_text(), 'ChristianRationalist'] for c in content63]
    contents += content63

print('Load GrumpyEcon...')
content64, error, msg = read('https://johnhcochrane.blogspot.com/feeds/posts/default', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content64 = content64.find_all('entry')
    content64 = [[c.title.get_text(), str(c.find_all('link')[-1]).split('"')[1], 'GrumpyEcon'] for c in content64]
    contents += content64

print('Load SupplySide...')
content65, error, msg = read('https://blog.supplysideliberal.com/post?format=rss', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content65 = content65.find_all('item')
    content65 = [[c.title.get_text() if c.title is not None else '',
                  c.link.get_text() if c.link is not None else '', 'SupplySide'] for c in content65]
    contents += content65

print('Load Bulletin...')
content66, error, msg = read('https://thebulletin.org/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content66 = content66.find_all('item')
    content66 = [[c.title.get_text(), c.link.get_text(), 'Bulletin'] for c in content66]
    contents += content66

print('Load Rodney...')
content67, error, msg = read('http://rodneybrooks.com/blog/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content67 = content67.find_all('item')
    content67 = [[c.title.get_text(), c.link.get_text(), 'Rodney'] for c in content67]
    contents += content67

print('Load Theorem...')
content68, error, msg = read('https://afinetheorem.wordpress.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content68 = content68.find_all('item')
    content68 = [[c.title.get_text(), c.link.get_text(), 'Theorem'] for c in content68]
    contents += content68

print('Load RAND Research...')
content69, error, msg = read('https://www.rand.org/pubs/new.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content69 = content69.find_all('entry')
    content69 = [[c.title.get_text(), str(c.find_all('link')[-1]).split('"')[1]] for c in content69]
    content69 = [[c[0], 'https://www.rand.org' + c[1] if 'http' not in c[1] else c[1], 'RAND'] for c in content69]
    contents += content69

print('Load RAND Blog...')
content70, error, msg = read('https://www.rand.org/blog.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content70 = content70.find_all('entry')
    content70 = [[c.title.get_text(), str(c.find_all('link')[-1]).split('"')[1]] for c in content70]
    content70 = [[c[0], 'https://www.rand.org' + c[1] if 'http' not in c[1] else c[1], 'RAND'] for c in content70]
    contents += content70

print('Load Vegan Strategist...')
content71, error, msg = read('http://veganstrategist.org/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content71 = content71.find_all('item')
    content71 = [[c.title.get_text(), c.link.get_text(), 'VeganStrat'] for c in content71]
    contents += content71

print('Load Ribbonfarm...')
content72, error, msg = read('http://www.ribbonfarm.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content72 = content72.find_all('item')
    content72 = [[c.title.get_text(), c.link.get_text(), 'RibbonFarm'] for c in content72]
    contents += content72

print('Load Scott Sumner...')
content73, error, msg = read('https://www.econlib.org/feed/indexSumner_xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content73 = content73.find_all('item')
    content73 = [[c.title.get_text().replace(', by Scott Sumner', ''), c.link.get_text(), 'Sumner'] for c in content73]
    contents += content73

print('Load NewFoodEconomy...')
content74, error, msg = read('https://newfoodeconomy.org/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content74 = content74.find_all('item')
    content74 = [[c.title.get_text(), c.link.get_text(), 'NewFood'] for c in content74]
    contents += content74

print('Load Danielle Morrill...')
content75, error, msg = read('http://feeds.feedburner.com/daniellemorrill', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content75 = content75.find_all('item')
    content75 = [[c.title.get_text(), c.link.get_text(), 'Morrill'] for c in content75]
    contents += content75

print('Load BLH...')
content76, error, msg = read('https://bleedingheartlibertarians.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content76 = content76.find_all('item')
    content76 = [[c.title.get_text(), c.link.get_text(), 'BLH'] for c in content76]
    contents += content76

print('Load WorldInData...')
content77, error, msg = read('https://ourworldindata.org/atom.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content77 = content77.find_all('entry')
    content77 = [[c.title.get_text(), str(c.find_all('link')[-1]).split('"')[1], 'WorldInData'] for c in content77]
    contents += content77

print('Load Fake Nous...')
content79, error, msg = read('http://fakenous.net/?feed=rss2', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content79 = content79.find_all('item')
    content79 = [[c.title.get_text(), c.link.get_text(), 'FakeNous'] for c in content79]
    contents += content79

print('Load Sam Altman...')
content80, error, msg = read('http://blog.samaltman.com/posts.atom', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content80 = content80.find_all('entry')
    content80 = [[c.title.get_text(), str(c.find_all('link')[-1]).split('"')[1], 'SamAltman'] for c in content80]
    contents += content80

print('Load Jason Crawford...')
content81, error, msg = read('https://jasoncrawford.org/feed.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content81 = content81.find_all('entry')
    content81 = [[c.title.get_text(), str(c.find_all('link')[-1]).split('"')[1], 'Crawford'] for c in content81]
    contents += content81

print('Load HBR...')
content82, error, msg = read('http://feeds.hbr.org/harvardbusiness/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content82 = content82.find_all('entry')
    content82 = [[c.title.get_text(), str(c.find_all('link')[-1]).split('"')[1], 'HBR'] for c in content82]
    contents += content82

print('Load Devon...')
content83, error, msg = read('https://devonzuegel.com/feed.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content83 = content83.find_all('entry')
    content83 = [[c.title.get_text(), str(c.find_all('link')[-1]).split('"')[1], 'Devon'] for c in content83]
    contents += content83

print('Load Pseudoerasmus...')
content84, error, msg = read('https://pseudoerasmus.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content84 = content84.find_all('item')
    content84 = [[c.title.get_text(), c.link.get_text(), 'Pseudoerasmus'] for c in content84]
    contents += content84

print('Load Nintil...')
content85, error, msg = read('https://nintil.com/rss.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content85 = content85.find_all('item')
    content85 = [[c.title.get_text(), c.link.get_text(), 'Nintil'] for c in content85]
    contents += content85

print('Load Aarora...')
content86, error, msg = read('https://harshitaarora.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content86 = content86.find_all('item')
    content86 = [[c.title.get_text(), c.link.get_text(), 'Aarora'] for c in content86]
    contents += content86

print('Load WTB...')
content87, error, msg = read('https://medium.com/feed/what-to-build', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content87 = content87.find_all('item')
    content87 = [[c.title.get_text(), c.link.get_text(), 'WTB'] for c in content87]
    contents += content87

print('Load Elad...')
content88, error, msg = read('http://blog.eladgil.com/feeds/posts/default', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content88 = content88.find_all('entry')
    content88 = [[c.title.get_text(), str(c.find_all('link')[-1]).split('"')[1], 'Elad'] for c in content88]
    contents += content88

print('Load Eghbal...')
content89, error, msg = read('https://nadiaeghbal.com/feed', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content89 = content89.find_all('entry')
    content89 = [[c.title.get_text(), str(c.find_all('link')[-1]).split('"')[1], 'Eghbal'] for c in content89]
    contents += content89

print('Load Greenspun...')
content90, error, msg = read('https://philip.greenspun.com/blog/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content90 = content90.find_all('item')
    content90 = [[c.title.get_text(), c.link.get_text(), 'Greenspun'] for c in content90]
    contents += content90

print('Load ScholarsSage...')
content91, error, msg = read('https://scholars-stage.blogspot.com/feeds/posts/default', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content91 = content91.find_all('entry')
    content91 = [[c.title.get_text(), str(c.find_all('link')[-1]).split('"')[1], 'ScholarsSage'] for c in content91]
    contents += content91

print('Load Gross...')
content92, error, msg = read('https://dcgross.com/feed.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content92 = content92.find_all('entry')
    content92 = [[c.title.get_text(), str(c.find_all('link')[-1]).split('"')[1], 'Gross'] for c in content92]
    contents += content92

print('Load Kling...')
content93, error, msg = read('http://www.arnoldkling.com/blog/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content93 = content93.find_all('item')
    content93 = [[c.title.get_text(), c.link.get_text(), 'Kling'] for c in content93]
    contents += content93

print('Load Seliger...')
content94, error, msg = read('https://jakeseliger.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content94 = content94.find_all('item')
    content94 = [[c.title.get_text(), c.link.get_text(), 'Seliger'] for c in content94]
    contents += content94

print('Load Matuschak...')
content95, error, message = read('https://andymatuschak.org/', return_type='soup')
if error:
    print(msg)
else:
    content95 = content95.find_all('a')
    content95 = [c for c in content95 if 'h3' in str(c) and 'href' in str(c)]
    content95 = [[cx for cx in str(c).split('"') if 'class' not in cx and 'jsx' not in cx and 'href' not in cx and 'alternateGlyph' not in cx] for c in content95]
    content95 = [['Matuschak', c[1].replace('</p>', '').replace('</a>', '').replace('><h3>', '').replace('</h3><p>', ': ').replace('>', ''), c[0]] for c in content95]
    content95 = [[c[1], 'https://andymatuschak.org' + c[2] if 'http' not in c[2] else c[2], c[0]] for c in content95]
    contents += content95

print('Load Guzey Blog...')
content96, error, message = read('https://guzey.com/', return_type='soup')
if error:
    print(msg)
else:
    content96 = content96.find_all('div')[-3].find_all('a')
    content96 = [[c[2].replace('</a>', '').replace('>', '').replace('>', ''),
                  'https://guzey.com/' + c[1], 'Guzey'] for c in [str(c).split('"') for c in content96]] 
    contents += content96

print('Load Guzey Twitter...')
content97, error, message = read('https://www.getrevue.co/profile/guzey/', return_type='soup')
if error:
    print(msg)
else:
    content97 = [c for c in content97.find_all('a') if 'Best of' in str(c)]
    content97 = [str(c).split('"') for c in content97]
    content97 = [[c[0], c[1]] for c in [[c for c in cs if 'best' in c.lower()] for cs in content97]]
    content97 = [[c[1].replace('Best of Twitter - Best of Twitter - ', 'Best of Twitter - ').replace('title=\'', ''),
                  'https://www.getrevue.co' + c[0], 'Guzey'] for c in content97]
    contents += content97

print('Load Guzey Links...')
content98, error, message = read('https://guzey.com/links/', return_type='soup')
if error:
    print(msg)
else:
    content98 = [c for c in content98.find_all('a') if 'http' in str(c) and 'perma.cc' not in str(c) and 'social-icon' not in str(c) and 'div' not in str(c)]
    content98 = [str(c).split('"') for c in content98]
    content98 = [c for c in content98 if c[1].count('/') > 3]
    content98 = [[c[2].replace('</a>', '').replace('>', '').replace('“', '').replace('”', ''), c[1], 'Guzey'] for c in content98]
    contents += content98

print('Load NationalReview...')
content99, error, msg = read('https://www.nationalreview.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content99 = content99.find_all('item')
    content99 = [[c.title.get_text(), c.link.get_text(), 'NR'] for c in content99]
    contents += content99

print('Load CodingHorror...')
content100, error, msg = read('http://feeds.feedburner.com/codinghorror?format=xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content100 = content100.find_all('item')
    content100 = [[c.title.get_text(), c.link.get_text(), 'CH'] for c in content100]
    contents += content100

print('Load Towards Data Science...')
content101, error, msg = read('https://towardsdatascience.com/feed', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content101 = content101.find_all('item')
    content101 = [[c.title.get_text(), c.link.get_text().replace('?source=rss----7f60cf5620c9---4', ''), 'TDS'] for c in content101]
    contents += content101

print('Load Niskanen Center...')
content102, error, msg = read('https://www.niskanencenter.org/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content102 = content102.find_all('item')
    content102 = [[c.title.get_text(), c.link.get_text(), 'Niskanen'] for c in content102]
    contents += content102

print('Load SSIR...')
content103, error, msg = read('https://ssir.org/site/rss_2.0', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content103 = content103.find_all('item')
    content103 = [[c.title.get_text(), c.link.get_text(), 'SSIR'] for c in content103]
    contents += content103

print('Load Mischiefs of Faction...')
content104, error, msg = read('https://www.mischiefsoffaction.com/blog-feed.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content104 = content104.find_all('item')
    content104 = [[c.title.get_text(), c.link.get_text(), 'MOF'] for c in content104]
    contents += content104

print('Load Rosie...')
content105, error, msg = read('https://rosiecam.home.blog/blog-feed/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content105 = content105.find_all('item')
    content105 = [[c.title.get_text(), c.link.get_text(), 'Rosie'] for c in content105]
    contents += content105

print('Load Ryan Avent...')
content108, error, msg = read('https://ryanavent.substack.com/feed', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content108 = content108.find_all('item')
    content108 = [[c.title.get_text(), c.link.get_text(), 'RyanAvent'] for c in content108]
    contents += content108

print('Load Quillette...')
content109, error, msg = read('https://quillette.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content109 = content109.find_all('item')
    content109 = [[c.title.get_text(), c.link.get_text(), 'Quillette'] for c in content109]
    contents += content109

print('Load No Meat Athlete...')
content110, error, msg = read('https://www.nomeatathlete.com/blog/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content110 = content110.find_all('item')
    content110 = [[c.title.get_text(), c.link.get_text(), 'NMA'] for c in content110]
    contents += content110

print('Load The Economist\'s Medium...')
content111, error, msg = read('https://medium.economist.com/feed', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content111 = content111.find_all('item')
    content111 = [[c.title.get_text(), c.link.get_text().replace('?source=rss----ae7c30c8cbcc---4', ''), 'EconMed'] for c in content111]
    contents += content111

print('Load NerdFitness...')
content112, error, msg = read('https://www.nerdfitness.com/blog/feed', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content112 = content112.find_all('item')
    content112 = [[c.title.get_text(), c.link.get_text(), 'NerdFitness'] for c in content112]
    contents += content112

print('Load DataRobot...')
content113, error, msg = read('https://blog.datarobot.com/rss.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content113 = content113.find_all('item')
    content113 = [[c.title.get_text(), c.link.get_text(), 'DR'] for c in content113]
    contents += content113

print('Load JSMP...')
content114, error, msg = read('https://jsmp.dk/index.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content114 = content114.find_all('item')
    content114 = [[c.title.get_text(), c.link.get_text(), 'JSMP'] for c in content114]
    contents += content114

print('Load JSMP Medium...')
content115, error, msg = read('https://medium.com/feed/@jsmp', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content115 = content115.find_all('item')
    content115 = [[c.title.get_text(), c.link.get_text(), 'JSMP'] for c in content115]
    contents += content115

print('Load Palladium...')
content116, error, msg = read('https://palladiummag.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content116 = content116.find_all('item')
    content116 = [[c.title.get_text(), c.link.get_text(), 'Palladium'] for c in content116]
    contents += content116

print('Load Possibly Wrong...')
content117, error, msg = read('https://possiblywrong.wordpress.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content117 = content117.find_all('item')
    content117 = [[c.title.get_text(), c.link.get_text(), 'PossiblyWrong'] for c in content117]
    contents += content117

print('Load XKCD What If...')
content118, error, msg = read('https://what-if.xkcd.com/feed.atom', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content118 = content118.find_all('entry')
    content118 = [[c.title.get_text(), c.id.get_text(), 'XKCDWI'] for c in content118]
    contents += content118

print('Load Ask a Mathematician / Physicist...')
content119, error, msg = read('https://www.askamathematician.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content119 = content119.find_all('item')
    content119 = [[c.title.get_text(), c.link.get_text(), 'AskAM/P'] for c in content119]
    contents += content119

print('Load Signal v Noise...')
content120, error, msg = read('https://m.signalvnoise.com/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content120 = content120.find_all('item')
    content120 = [[c.title.get_text(), c.link.get_text(), 'SVN'] for c in content120]
    contents += content120

print('Load Exponents Mag...')
content121, error, msg = read('https://exponentsmag.org/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content121 = content121.find_all('item')
    content121 = [[c.title.get_text(), c.link.get_text(), 'Exponents'] for c in content121]
    contents += content121

print('Load 127...')
content122, error, msg = read('https://onetwentyseven.blog/feed/', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content122 = content122.find_all('item')
    content122 = [[c.title.get_text(), c.link.get_text(), '127'] for c in content122]
    contents += content122

print('Load SuperOrganizers...')
content123, error, msg = read('https://superorganizers.substack.com/feed', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content123 = content123.find_all('item')
    content123 = [[c.title.get_text(), c.link.get_text(), 'SuperOrganizers'] for c in content123]
    contents += content123

print('Load The Dispatch...')
content124, error, msg = read('https://thedispatch.com/feed', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content124 = content124.find_all('item')
    content124 = [[c.title.get_text(), c.link.get_text(), 'Dispatch'] for c in content124]
    contents += content124

print('Load NatElison Blog...')
content125, error, msg = read('https://www.nateliason.com/blog', return_type='soup')
if error:
    print(msg)
else:
    content125 = [str(c) for c in content125.find_all('a') if 'blog-page-heading' in str(c)]
    content125 = [[c[6].replace('</h2><p class=', '').replace('>', ''), 'https://www.nateliason.com' + c[3], 'NatEliason'] for c in [c.split('"') for c in content125]]
    contents += content125

print('Load NatElison Book Notes...')
content126, error, msg = read('https://www.nateliason.com/notes', return_type='soup')
if error:
    print(msg)
else:
    content126 = [str(c) for c in content126.find_all('p') if '/notes' in str(c)]
    content126 = [['Book Notes: ' + c[2].split('</a>')[0].replace('>', ''), 'https://www.nateliason.com' + c[1], 'NatEliason'] for c in [c.split('"') for c in content126]]
    contents += content126

print('Load SLW...')
content127, error, msg = read('https://softwareleadweekly.com/issues/', return_type='soup')
if error:
    print(msg)
else:
    content127 = [str(c) for c in content127.find_all('a') if 'Issue' in str(c)]
    content127 = [['Software Lead Weekly ' + c[-1].replace('></path></svg>', '').replace('</a>', ''), 'https://softwareleadweekly.com' + c[3], 'SLW'] for c in [c.split('"') for c in content127]]
    contents += content127

print('Load Gladfelter...')
content128, error, msg = read('https://www.ogladfelter.com/rss.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content128 = content128.find_all('item')
    content128 = [[c.title.get_text(), c.link.get_text(), 'Gladfelter'] for c in content128]
    contents += content128

print('Load French Press...')
content129, error, msg = read('https://frenchpress.thedispatch.com/feed', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content129 = content129.find_all('item')
    content129 = [[c.title.get_text(), c.link.get_text(), 'French'] for c in content129]
    contents += content129

print('Load G-File...')
content130, error, msg = read('https://gfile.thedispatch.com/feed', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content130 = content130.find_all('item')
    content130 = [[c.title.get_text(), c.link.get_text(), 'GFile'] for c in content130]
    contents += content130

print('Load Dan Luu...')
content131, error, msg = read('https://danluu.com/atom.xml', return_type='soup', reader_type='xml')
if error:
    print(msg)
else:
    content131 = content131.find_all('item')
    content131 = [[c.title.get_text(), c.link.get_text(), 'Danluu'] for c in content131]
    contents += content131


random.shuffle(contents)


# TODO: DRY with scripts/import_onetab.py
print('Psycopg2 connect')
conn = psycopg2.connect('dbname=stanza_dev user=dbuser')
cur = conn.cursor()
lines = len(contents)
for i, content in enumerate(contents):
    if i % 100 == 0:
        print('{}/{}'.format(i, lines))

    result = find_link_row(cur, content[1])

    if len(result) == 0:
        add_link_row(cur, content)
    elif len(result) > 1:
        delete_link_row(cur, content[1])
        add_link_row(cur, content)
    elif str(result[0]['added'].date()) == '1900-01-01':
        delete_link_row(cur, content[1])
        add_link_row(cur, content)

    result = find_link_row(cur, content[1])
    if len(result) == 0:
        print('FATAL ERROR 1')
        import pdb
        pdb.set_trace()

    if len(result) > 1:
        print('FATAL ERROR 2')
        import pdb
        pdb.set_trace()

cur.close()
conn.commit()
conn.close()
print('Done')
