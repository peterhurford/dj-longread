import os
import re
import random
import psycopg2

import pandas as pd

from datetime import datetime, timedelta

from utils.download import read
from utils.sql import enquote, add_row, delete_row, update_row, export_db

from link.config import PURGE_OLDER_THAN_X_DAYS, PURGABLE_AGGREGATORS, OBSOLETE_AGGREGATORS


def chunk(l, n):
    out = []
    for i in range(0, len(l), n):
        out.append(l[i:i + n])
    return out


def resync_ids(cur):
    cur.execute('SELECT setval(\'link_link_id_seq\', (SELECT MAX(id) FROM link_link)+1);')
    return None


def get_max_id(cur):
    cur.execute('SELECT MAX(id) FROM link_link')
    max_id = cur.fetchone()[0]
    if not max_id:
        return 1
    else:
        return max_id


def add_link_row(cur, content):
    seed = random.randint(1, 100)
    idx = get_max_id(cur) + 1
    add_row(cur,
            'link_link',
            ['id', 'title', 'url', 'aggregator', 'added', 'modified', 'seed'],
            [enquote(str(idx))] + [enquote(c.replace('\'', '"')) for c in content + [str(datetime.now())] * 2] + [enquote(str(seed))])
    return None


def delete_link_row(cur, id_):
    delete_row(cur, 'link_link', 'id', enquote(id_))
    return None


def hide_row(cur, id_):
    update_row(cur, 'link_link', 'liked', -1, 'id', enquote(id_))
    return None


def entry_process_fn(name, content):
    content = content.find_all('entry')
    content = [[c.title.get_text() if c.title is not None else 'Blank',
                c.id.get_text() if c.id is not None else '', name] for c in content]
    return content

def item_process_fn(name, content):
    content = content.find_all('item')
    content = [[c.title.get_text() if c.title is not None else 'Blank',
                c.link.get_text() if c.link is not None else '', name] for c in content]
    return content

def entry_link_process_fn(name, content):
    content = content.find_all('entry')
    content = [[c.title.get_text() if c.title is not None else 'Blank',
                str(c.find_all('link')[-1]).split('"')[1] if c.link is not None else '',
                name] for c in content]
    return content


def load_contents(name, feed, reader_fn, return_type='soup', reader_type='xml'):
    print('Load {}...'.format(name))

    content, error, msg = read(feed, return_type=return_type, reader_type=reader_type)
    if error:
        print('--- ERROR: {}'.format(msg))
        return []

    if reader_fn == 'item':
        reader_fn = item_process_fn
    elif reader_fn == 'entry':
        reader_fn = entry_process_fn
    elif reader_fn == 'entry-link':
        reader_fn = entry_link_process_fn

    try:
        content = reader_fn(name, content)
    except Exception as e:
        print('-- ERROR in reader fn: {}'.format(e))
        return []

    if len(content) == 0:
        print('--- ERROR: No content!')
        return []

    if 'http' not in content[0][1]:
        print('--- ERROR: Malformed URLs!')
        return []

    print('...Got {}'.format(len(content)))
    return content


contents = []

def ea_blogs_reader_fn(name, content):
    content = content.find_all('ul')[0]
    content = [str(c.a).split('href="')[1].split('rel=') for c in content.find_all('li')]
    content = [[c[1].split('>')[1].split('<')[0],
                 c[0].replace('"', '').strip(),
                 'EABlogs'] for c in content]
    processed_content = []

    # Add custom aggregators for EA Blogs members
    url_map = {'forum.effectivealtruism.org': 'EAForum',
               'cset.georgetown.edu': 'CSET',
               'overcomingbias.com': 'Hanson',
               'impartial-priorities.org': 'ImpPri',
               'philosophyetc.net': 'PhilosophyEtc',
               'thingofthings.wordpress.com': 'Ozy',
               'palladiummag.com': 'Palladium',
               'benjaminrosshoffman.com': 'BenHoffman',
               'vox.com': 'Vox',
               'charityentrepreneurship.com': 'CE',
               'stijnbruers.wordpress.com': 'Bruers',
               'fhi.ox.ac.uk': 'FHI',
               'centreforeffectivealtruism.org': 'CEA',
               '80000hours.org': '80K',
               'rationalconspiracy.com': 'RatlConspiracy',
               'astralcodexten.substack.com': 'SSC',
               'lukemuehlhauser.com': 'Muehlhauser',
               'longtermrisk.org': 'CLR',
               'thewholesky.wordpress.com': 'JuliaWise',
               'globalprioritiesinstitute.org': 'GPI',
               'theunitofcaring.tumblr.com': 'Kelsey',
               'givedirectly.org': 'GiveDirectly',
               'acesounderglass.com': 'VanNostrand'}

    for c in content:
        include = True
        for url, label in url_map.items():
            if url in c[1]:
                c[2] = label
            else:
                include = False

        if include:
            processed_content.append(c)

    return processed_content


contents += load_contents('EABlogs', 'http://eablogs.net', ea_blogs_reader_fn)
contents += load_contents('EAForum', 'https://forum.effectivealtruism.org/feed.xml?view=rss&karmaThreshold=40', 'item')
contents += load_contents('LW', 'https://www.lesswrong.com/feed.xml?view=curated-rss', 'item')
contents += load_contents('538', 'https://fivethirtyeight.com/politics/feed/', 'item')
contents += load_contents('Lusk', 'http://jaysonlusk.com/blog?format=rss', 'item')

def caplan_reader_fn(name, content):
    content = content.find_all('item')
    content = [[c.title.get_text().replace(', by Bryan Caplan', ''),
                c.link.get_text(), 'Caplan'] for c in content]
    return content
contents += load_contents('Caplan', 'https://www.econlib.org/feed/indexCaplan_xml',
                          caplan_reader_fn)

contents += load_contents('Mankiw', 'http://feeds.feedburner.com/blogspot/SOpj?format=xml', 'item')
contents += load_contents('AI Impacts', 'https://aiimpacts.org/feed/', 'item')
contents += load_contents('Ben Kuhn', 'https://www.benkuhn.net/rss/', 'entry')
contents += load_contents('Scott Young', 'http://feeds.feedburner.com/scotthyoung/HAHx', 'item')

def current_affairs_reader_fn(name, content):
    content = content.find_all('a')
    content = [str(a).split('"') for a in content]
    content = [[a[1], a[2]] for a in content if len(a) == 3 and 'author' not in a[1]]
    content = content[2:]
    content = [[a[1].replace('</a>', '').replace('>', ''),
                 'https://www.currentaffairs.org' + a[0],
                 'Current Affairs'] for a in content]
    return content
contents += load_contents('Current Affairs', 'https://www.currentaffairs.org',
                          current_affairs_reader_fn)

def mtlynch_reader_fn(name, content):
    content = content.find_all('item')
    content = [[c.title.get_text(), c.guid.get_text(), name] for c in content]
    return content
contents += load_contents('Mtlynch.io', 'https://mtlynch.io/feed.xml',
                          mtlynch_reader_fn, reader_type='lxml')

contents += load_contents('Beeminder', 'http://feeds.feedburner.com/bmndr', 'item')
contents += load_contents('Constantin', 'https://srconstantin.wordpress.com/feed/', 'item')

def roots_reader_fn(name, content):
    content = content.find_all('li')
    content = [c.find_all('a') for c in content]
    content = [str(c).split('"')[3:5] for c in content]
    content = [[c[1].replace('</a>', '').replace('>', ''),
                  'http://www.rootsofprogress.org' + c[0], 'Progress'] for c in content]
    return content
contents += load_contents('Progress', 'https://rootsofprogress.org/posts',
                          roots_reader_fn, reader_type='lxml')

contents += load_contents('PhilosophyEtc',
                          'http://feeds.philosophyetc.net/PhilosophyEtCetera',
                          'entry-link')

def graham_reader_fn(name, content):
    content = [str(c).split('"') for c in content.find_all('a')]
    content = [[c[2].replace('</a>', '').replace('>', ''), 'http://paulgraham.com/' + c[1], 'Graham'] for c in content]
    content = content[6:-1]
    return content
contents += load_contents('Graham', 'http://paulgraham.com/articles.html', graham_reader_fn,
                          reader_type='lxml')

contents += load_contents('ALOP', 'https://alifeofproductivity.com/feed/', 'item')
contents += load_contents('Muehlhauser', 'http://feeds.feedburner.com/LukeMuehlhauser', 'entry')

def leo_reader_fn(name, content):
    content = [str(c).split('"') for c in content.find_all('a')]
    content = [[c[2].replace('</a>', '').replace('>', '').replace('\n', ''),
                'https://zenhabits.net' + c[1], 'Leo'] for c in content]
    content = content[2:]
    return content
contents += load_contents('Leo', 'https://zenhabits.net/archives/', leo_reader_fn,
                          reader_type='lxml')

def rosewater_reader_fn(name, content):
    content = content.find_all('a')
    content = [c for c in content if 'articles' in str(c)][1:-2]
    content = [[c.find_all('h3')[0].get_text(),
                 'https://magic.wizards.com' + str(c).split('"')[1], 'Rosewater']
                 for c in content]
    return content
contents += load_contents('Rosewater',
                          'https://magic.wizards.com/en/articles/columns/making-magic',
                          rosewater_reader_fn, reader_type='lxml')

contents += load_contents('Levels', 'https://levels.io/rss/', 'item')
contents += load_contents('Noah', 'http://noahpinionblog.blogspot.com/feeds/posts/default',
                          'entry-link')
contents += load_contents('Noah',
                          'https://www.bloomberg.com/opinion/authors/AR3OYuAmvcU/noah-smith.rss',
                          'item')
contents += load_contents('Noah', 'https://noahpinion.substack.com/feed', 'item')
contents += load_contents('deBoer', 'https://freddiedeboer.substack.com/feed', 'item')
contents += load_contents('CSET', 'https://cset.georgetown.edu/feed/', 'item')
contents += load_contents('GEMorris', 'https://gelliottmorris.substack.com/feed', 'item')
contents += load_contents('ChinAI', 'https://chinai.substack.com/feed', 'item')
contents += load_contents('ImportAI', 'https://jack-clark.net/feed/', 'item')
contents += load_contents('Gelman', 'https://statmodeling.stat.columbia.edu/feed/', 'item')

def sumner_reading_fn(name, content):
    content = content.find_all('item')
    content = [[c.title.get_text().replace(', by Scott Sumner', ''), c.link.get_text(), 'Sumner'] for c in content]
    return content
contents += load_contents('WorldInData', 'https://ourworldindata.org/atom.xml', 'entry')
contents += load_contents('SamAltman', 'http://blog.samaltman.com/posts.atom', 'entry-link')
contents += load_contents('Crawford', 'https://jasoncrawford.org/feed.xml', 'entry')
contents += load_contents('HBR', 'http://feeds.hbr.org/harvardbusiness/', 'entry-link')
contents += load_contents('Nintil', 'https://nintil.com/rss.xml', 'item')
contents += load_contents('Aarora', 'https://harshitaarora.com/feed/', 'item')
contents += load_contents('WTB', 'https://medium.com/feed/what-to-build', 'item')
contents += load_contents('Elad', 'http://blog.eladgil.com/feeds/posts/default', 'entry-link')
contents += load_contents('ScholarsSage',
                          'https://scholars-stage.blogspot.com/feeds/posts/default',
                          'entry-link')
contents += load_contents('Seliger', 'https://jakeseliger.com/feed/', 'item')
contents += load_contents('PredPol', 'https://predictingpolitics.com/feed/', 'item')
contents += load_contents('BreadFixer', 'https://medium.com/feed/@breadpricefixer', 'item')
contents += load_contents('Avraham', 'https://misinfounderload.substack.com/feed', 'item')
contents += load_contents('FakeNous', 'https://fakenous.net/?feed=rss2', 'item')
contents += load_contents('AppliedDiv', 'https://applieddivinitystudies.com/atom.xml', 'entry')
contents += load_contents('WIP', 'https://worksinprogress.co/feed/', 'item')
contents += load_contents('Scrimshaw', 'https://scrimshawunscripted.substack.com/feed', 'item')

def andy_reader_fn(name, content):
    content = content.find_all('a')
    content = [c for c in content if 'h3' in str(c) and 'href' in str(c)]
    content = [[cx for cx in str(c).split('"') if 'class' not in cx and 'jsx' not in cx and 'href' not in cx and 'alternateGlyph' not in cx] for c in content]
    content = [['Matuschak', c[1].replace('</p>', '').replace('</a>', '').replace('><h3>', '').replace('</h3><p>', ': ').replace('>', ''), c[0]] for c in content]
    content = [[c[1], 'https://andymatuschak.org' + c[2] if 'http' not in c[2] else c[2], c[0]] for c in content]
    return content
contents += load_contents('Matuschak', 'https://andymatuschak.org/', andy_reader_fn,
                          reader_type='lxml')

def guzey_reader_fn(name, content):
    content = [c for c in content.find_all('a')][16:-8]
    content = [str(c).split('"') for c in content]
    content = [[c[2].replace('</a>', '').replace('>', '').replace('“', '').replace('”', ''),
               'https://guzey.com/' + c[1], 'Guzey'] for c in content]
    return content
contents += load_contents('Guzey', 'https://guzey.com/', guzey_reader_fn)
contents += load_contents('Guzey', 'https://bestoftwitter.substack.com/feed', 'item')

def guzey_link_reader_fn(name, content):
    content = [c for c in content.find_all('a') if 'http' in str(c) and 'perma.cc' not in str(c) and 'social-icon' not in str(c) and 'div' not in str(c)]
    content = [str(c).split('"') for c in content]
    content = [c for c in content if c[1].count('/') > 3]
    content = [[c[2].replace('</a>', '').replace('>', '').replace('“', '').replace('”', ''), c[1], 'Guzey'] for c in content]
    return content
contents += load_contents('Guzey', 'https://guzey.com/links/', guzey_link_reader_fn,
                          reader_type='lxml')
contents += load_contents('MOF', 'https://www.mischiefsoffaction.com/blog-feed.xml', 'item')
contents += load_contents('NMA', 'https://www.nomeatathlete.com/blog/feed/', 'item')
contents += load_contents('JSMP', 'https://jsmp.dk/index.xml', 'item')
contents += load_contents('JSMP', 'https://medium.com/feed/@jsmp', 'item')
contents += load_contents('AskAM/P', 'https://www.askamathematician.com/feed/', 'item')
contents += load_contents('SVN', 'https://m.signalvnoise.com/feed/', 'item')
contents += load_contents('Dispatch', 'https://thedispatch.com/feed', 'item')
contents += load_contents('SSC', 'https://astralcodexten.substack.com/feed', 'item')
contents += load_contents('Yglesias', 'https://www.slowboring.com/feed', 'item')
contents += load_contents('Wilkinson', 'https://modelcitizen.substack.com/feed', 'item')
contents += load_contents('80K', 'https://80000hours.org/latest/feed/', 'item')

def eliason_reader_fn(name, content):
    content = [str(c) for c in content.find_all('a') if 'blog-page-heading' in str(c)]
    content = [[c[6].replace('</h2><p class=', '').replace('>', ''), 'https://www.nateliason.com' + c[3], 'NatEliason'] for c in [c.split('"') for c in content]]
    return content
contents += load_contents('NatEliason', 'https://www.nateliason.com/blog', eliason_reader_fn,
                          reader_type='lxml')

def eliason_book_reader_fn(name, content):
    content = [str(c) for c in content.find_all('p') if '/notes' in str(c)]
    content = [['Book Notes: ' + c[2].split('</a>')[0].replace('>', ''), 'https://www.nateliason.com' + c[1], 'NatEliason'] for c in [c.split('"') for c in content]]
    return content
contents += load_contents('NatEliason', 'https://www.nateliason.com/notes',
                          eliason_book_reader_fn, reader_type='lxml')

def slw_reader_fn(name, content):
    content = [str(c) for c in content.find_all('a') if 'Issue' in str(c)]
    content = [['Software Lead Weekly ' + c[-1].replace('></path></svg>', '').replace('</a>', ''), 'https://softwareleadweekly.com' + c[3], 'SLW'] for c in [c.split('"') for c in content]]
    return content
contents += load_contents('SLW', 'https://softwareleadweekly.com/issues/', slw_reader_fn,
                          reader_type='lxml')
contents += load_contents('Danluu', 'https://danluu.com/atom.xml', 'item')
contents += load_contents('Bollard',
                          'https://us14.campaign-archive.com/feed?u=66df320da8400b581cbc1b539&id=de632a3c62',
                          'item')
contents += load_contents('CSET',
                          'https://us20.campaign-archive.com/feed?u=248119f7a6386759c3a4f7155&id=fcbacf8c3e',
                          'item')
contents += load_contents('HLI',
                          'https://us19.campaign-archive.com/feed?u=e759f3a724b8709250fb153c2&id=163285db12',
                          'item')
contents += load_contents('Alignment', 'https://us18.campaign-archive.com/feed?u=1d1821210cc4f04d1e05c4fa6&id=dbac5de515', 'item')
contents += load_contents('FPChina', 'https://foreignpolicy.com/category/china-brief/feed/',
                          'item')
contents += load_contents('FPSouthAsia', 'https://foreignpolicy.com/category/south-asia-brief/feed/',
                          'item')
contents += load_contents('FPMorning', 'https://foreignpolicy.com/category/morning-brief/feed/',
                          'item')
contents += load_contents('FPSecurity', 'https://foreignpolicy.com/category/security-brief/feed/',
                          'item')
contents += load_contents('FP-WYWL',
                          'https://foreignpolicy.com/category/while-you-werent-looking/feed/',
                          'item')
contents += load_contents('FWI',
                          'https://us3.campaign-archive.com/feed?u=2afeee16b30494a373a377a31&id=92de5d8090',
                          'item')
contents += load_contents('DanWahl', 'https://danwahl.net/atom.xml', 'entry')
contents += load_contents('Katja', 'https://worldspiritsockpuppet.com/feed.xml', 'entry')
contents += load_contents('Metaculus', 'https://www.metaculus.com/news/rss/', 'item')
contents += load_contents('GlobalGuessing', 'https://globalguessing.com/rss/', 'item')
def evans_reader_fn(name, content):
    content = [str(c) for c in content.find_all('a') if 'benedictevans' in str(c)]
    content = [c.split('href="')[-1].split('>')[:-1] for c in content]
    content = [[c[1].replace('</a', ''),
                'https://www.ben-evans.com' + c[0].replace('"', ''),
                'BenEvans'] for c in content]
    content = [c for c in content if '\n' not in c[0]]
    return content
contents += load_contents('BenEvans', 'https://www.ben-evans.com/essays', evans_reader_fn,
                          reader_type='lxml')
contents += load_contents('Putanumonit', 'https://putanumonit.com/feed/', 'item')
contents += load_contents('HIPR', 'http://www.highimpactpolicy.review/feed', 'item')

def every_reader_fn(name, content):
    content = [str(c) for c in content.find_all('a') if '/{}/'.format(name.lower()) in str(c) and 'h2' in str(c)]
    content = [[re.sub(r'<span class="hand hand-[A-Z]">', '', c).replace('</span>', '').split('">')[2].
split('</h2>')[0],
                'https://every.to' + c.split('href="')[1].split('"')[0],
                name] for c in content]
    return content
contents += load_contents('Superorganizers', 'https://every.to/superorganizers?sort=newest',
                          every_reader_fn,
                          reader_type='xml')
contents += load_contents('Divinations', 'https://every.to/divinations?sort=newest',
                          every_reader_fn,
                          reader_type='xml')
contents += load_contents('Napkin-Math', 'https://every.to/napkin-math?sort=newest',
                          every_reader_fn,
                          reader_type='xml')
contents += load_contents('Almanack', 'https://every.to/almanack?sort=newest',
                          every_reader_fn,
                          reader_type='xml')
contents += load_contents('PoliticalKiwi', 'https://politicalkiwi.wordpress.com/feed/', 'item')
contents += load_contents('Taleb', 'https://fooledbyrandomnessdotcom.wordpress.com/feed/', 'item')
contents += load_contents('Taleb', 'https://medium.com/feed/incerto', 'item')
contents += load_contents('Holden', 'https://www.cold-takes.com/rss/', 'item')
contents += load_contents('Cummings', 'https://dominiccummings.substack.com/feed', 'item')
contents += load_contents('Schubert', 'https://stefanfschubert.com/blog?format=rss', 'item')
contents += load_contents('DataColada', 'https://datacolada.org/feed', 'item')
contents += load_contents('Seth', 'https://seths.blog/feed/', 'item')
contents += load_contents('Trammell', 'https://philiptrammell.com/blog/feed', 'item')
contents += load_contents('TIB', 'https://s3.amazonaws.com/revue/accounts/rss_feeds/000/033/453/original/rss_feed_33453.xml?1632204004', 'item')

print('-')
print('Gathering content')
random.shuffle(contents)

print('-')
print('Psycopg2 connect')
DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=stanza_dev user=dbuser')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

print('-')
print('Data export')
links = export_db(cur)

if links is not None:
    print('-')
    print('Purging broken links')
    broken = links[~links['url'].apply(lambda u: isinstance(u, str) and 'http' in u)]['id']
    lines = len(broken)
    if lines == 0:
        print('...No broken links detected')
    else:
        for i, id_ in enumerate(broken):
            delete_link_row(cur, id_)
        print('...{} broken links purged!'.format(lines))

print('-')
print('Calculating links to add')
if links is not None:
    existing_urls = set(links['url'].values)
    contents = [c for c in contents if c[1] not in existing_urls]

lines = len(contents)
added = []
if lines == 0:
    print('...No links to add')
else:
    print('...Adding links to DB')
    for i, content in enumerate(contents):
        if content[1] not in added:
            add_link_row(cur, content)
            added.append(content[1])
    print('...{} new links added!'.format(lines))

if links is not None:
    print('-')
    print('Purging duplicated')
    duplicated = links[links['url'].duplicated()]['id']
    lines = len(duplicated)
    if lines == 0:
        print('...No duplicated links detected')
    else:
        for i, id_ in enumerate(duplicated):
            delete_link_row(cur, id_)
        print('...{} duplicated links purged!'.format(lines))

if links is not None:
    print('-')
    print('Purging old')
    links['added'] = pd.to_datetime(links['added'], utc=True).dt.tz_localize(None)
    relative_now = links['added'].max()
    before_purge_window = relative_now - timedelta(days=PURGE_OLDER_THAN_X_DAYS)
    purgable = links[(links['aggregator'].apply(lambda a: a in PURGABLE_AGGREGATORS)) &
                     (links['added'] < before_purge_window) &
                     (links['liked'] != 0) &
                     (links['liked'] != 1) &
                     (links['liked'] != -1)]
    purgable = purgable['id']
    lines = len(purgable)
    if lines == 0:
        print('...No old-purgable links detected')
    else:
        for i, id_ in enumerate(purgable):
            hide_row(cur, id_)
        print('...{} old links purged!'.format(lines))

if links is not None:
    print('-')
    print('Purging obsolete')
    obsolete = links[(links['aggregator'].apply(lambda a: a in OBSOLETE_AGGREGATORS)) &
                     (links['liked'] != 0) & (links['liked'] != 1) & (links['liked'] != -1)]
    obsolete = obsolete['id']
    lines = len(obsolete)
    if lines == 0:
        print('...No obsolete links detected')
    else:
        for i, id_ in enumerate(obsolete):
            hide_row(cur, id_)
        print('...{} obsolete links purged!'.format(lines))

print('-')
print('Resync IDs')
resync_ids(cur)

print('-')
print('Closing connection')
cur.close()
conn.commit()
conn.close()
print('DONE!')

