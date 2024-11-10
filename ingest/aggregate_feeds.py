import os
import boto3 # Fail fast if Python env is not properly loaded
import json
import random
import psycopg2

import numpy as np
import pandas as pd

from datetime import datetime, timedelta

from utils.download import read
from utils.sql import add_row, delete_row, update_row, export_db

from link.config import (PURGE_OLDER_THAN_X_DAYS, LONG_PURGE_OLDER_THAN_X, PURGABLE_AGGREGATORS,
                         LONG_PURGABLE_AGGREGATORS, OBSOLETE_AGGREGATORS)


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
            [idx] + [c.replace('\'', '"') for c in content + [str(datetime.now())] * 2] + [seed])
    return None


def delete_link_row(cur, id_):
    delete_row(cur, 'link_link', 'id', id_)
    return None


def star_row(cur, id_):
    update_row(cur, 'link_link', 'starred', 1, 'id', id_)
    return None


def hide_row(cur, id_):
    update_row(cur, 'link_link', 'liked', -1, 'id', id_)
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


def load_contents(name, feed, reader_fn='item', return_type='soup', reader_type='xml'):
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


def aorn_reader_fn(name, content):
    content = [str(c).split('"') for c in content.find_all('a')]
    content = [[c[2].replace('</a>', '').replace('>', ''), 'https://1a3orn.com' + c[1], '1a3orn'] for c in content]
    content = content[2:-1]
    content = [c for c in content if 'About' not in c[0] and 'See more' not in c[0]]
    return content


def caip_reader_fn(name, content):
    content = [str(c).split('div>')[0] for c in content.find_all('a') if '/work/' in str(c)]
    content = [c.split('href="')[1].split('" class="')[0] for c in content]
    content = [c.split('"><img alt="') for c in content if 'img alt' in c]
    content = [[c[1], 'https://www.aipolicy.us' + c[0], 'CAIP'] for c in content]
    return content


def graham_reader_fn(name, content):
    content = [str(c).split('"') for c in content.find_all('a')]
    content = [[c[2].replace('</a>', '').replace('>', ''), 'http://paulgraham.com/' + c[1], 'Graham'] for c in content]
    content = content[6:-1]
    return content


def slw_reader_fn(name, content):
    content = [str(c) for c in content.find_all('a') if 'Issue' in str(c)]
    content = [['Software Lead Weekly ' + c[-1].replace('></path></svg>', '').replace('</a>', ''), 'https://softwareleadweekly.com' + c[3], 'SLW'] for c in [c.split('"') for c in content]]
    return content


def ted_reader_fn(name, content):
    content = [str(c).split('"') for c in content.find_all('a')][2:]
    content = [[c[4].replace('>', '').replace('</a', ''), 'https://www.tedsanders.com' + c[3], 'Ted'] for c in content]
    return content


# Fail fast if psql is not properly loaded
DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=stanza_dev user=dbuser')
psycopg2.connect(DATABASE_URL, sslmode='require')


# Load the contents
contents = []
contents += load_contents('1a3orn', 'https://1a3orn.com', aorn_reader_fn, reader_type='lxml')
contents += load_contents('80K', 'https://80000hours.org/podcast/episodes/feed/')
contents += load_contents('AI Impacts', 'https://blog.aiimpacts.org/feed')
contents += load_contents('AirStreet', 'https://press.airstreet.com/feed')
contents += load_contents('Alignment', 'https://us18.campaign-archive.com/feed?u=1d1821210cc4f04d1e05c4fa6&id=dbac5de515')
contents += load_contents('AskManager', 'https://www.askamanager.org/feed')
contents += load_contents('Ben Kuhn', 'https://www.benkuhn.net/rss/', 'entry')
contents += load_contents('Bollard', 'https://us14.campaign-archive.com/feed?u=66df320da8400b581cbc1b539&id=de632a3c62', 'item')
contents += load_contents('CAIP', 'https://aipolicyus.substack.com/feed')
contents += load_contents('CAIP', 'https://www.aipolicy.us/work', caip_reader_fn, reader_type='lxml')
contents += load_contents('Carlsmith', 'https://joecarlsmith.com/rss.xml')
contents += load_contents('CAIS', 'https://newsletter.safe.ai/feed')
contents += load_contents('ConPhys', 'https://www.construction-physics.com/feed')
contents += load_contents('Danluu', 'https://danluu.com/atom.xml')
contents += load_contents('DeanBall', 'https://www.hyperdimensional.co/feed')
contents += load_contents('DeNeufville', 'https://tellingthefuture.substack.com/feed')
contents += load_contents('Dispatch', 'https://thedispatch.com/feed/?newsletter-brands=morning')
contents += load_contents('Dispatch', 'https://thedispatch.com/newsletter/dispatch-politics/feed')
contents += load_contents('Dispatch', 'https://thedispatch.com/newsletter/techne/feed/')
contents += load_contents('Dwarkesh', 'https://www.dwarkeshpatel.com/feed')
contents += load_contents('Dynomight', 'https://dynomight.net/feed', 'entry')
contents += load_contents('ExperienceMachines', 'https://experiencemachines.substack.com/feed')
contents += load_contents('Forecasting', 'https://forecasting.substack.com/feed')
contents += load_contents('GEMorris', 'https://gelliottmorris.substack.com/feed')
contents += load_contents('Graham', 'http://paulgraham.com/articles.html', graham_reader_fn, reader_type='lxml')
contents += load_contents('Grunewald', 'https://www.erichgrunewald.com/feed.xml', 'entry')
contents += load_contents('Holden', 'https://www.cold-takes.com/rss/')
contents += load_contents('ImportAI', 'https://jack-clark.net/feed/')
contents += load_contents('JeffKauffman', 'https://www.jefftk.com/news.rss')
contents += load_contents('Josh', 'https://www.joshbarro.com/feed')
contents += load_contents('JuliaWise', 'https://juliawise.net/feed/')
contents += load_contents('Kitstack', 'https://kitsonjonathon.substack.com/feed')
contents += load_contents('MarkB', 'https://notanotherbigtech.substack.com/feed')
contents += load_contents('Masley', 'https://andymasley.substack.com/feed')
contents += load_contents('Miles', 'https://milesbrundage.substack.com/feed')
contents += load_contents('MLSafety', 'https://newsletter.mlsafety.org/feed')
contents += load_contents('NateSilver', 'https://www.natesilver.net/feed')
contents += load_contents('NavigatingAI', 'https://navigatingairisks.substack.com/feed')
contents += load_contents('Noah', 'https://noahpinion.substack.com/feed')
contents += load_contents('Observatory', 'https://effectiveinstitutionsproject.substack.com/feed')
contents += load_contents('Polymarket', 'https://news.polymarket.com/feed')
contents += load_contents('Rodney', 'https://rodneybrooks.com/blog/feed/')
contents += load_contents('SamF', 'https://samf.substack.com/feed')
contents += load_contents('SamHammond', 'https://www.secondbest.ca/feed')
contents += load_contents('ScholarsStage', 'https://scholars-stage.org/feed/')
contents += load_contents('Semianalysis', 'https://www.semianalysis.com/feed')
contents += load_contents('SimonM', 'https://simonm.substack.com/feed')
contents += load_contents('SLW', 'https://softwareleadweekly.com/issues/', slw_reader_fn, reader_type='lxml')
contents += load_contents('SplitTicket', 'https://split-ticket.org/feed/')
contents += load_contents('SSC', 'https://astralcodexten.substack.com/feed')
contents += load_contents('SCSP', 'https://scsp222.substack.com/feed')
contents += load_contents('Sentinel', 'https://blog.sentinel-team.org/feed')
contents += load_contents('Statecraft', 'https://www.statecraft.pub/feed')
contents += load_contents('Steinhardt', 'https://bounded-regret.ghost.io/rss/')
contents += load_contents('Stevenson', 'https://doingwestminsterbetter.substack.com/feed')
contents += load_contents('Transformer', 'https://www.transformernews.ai/feed')
contents += load_contents('QuantGalore', 'https://quantgalore.substack.com/feed')
contents += load_contents('Ted', 'https://www.tedsanders.com/', ted_reader_fn, reader_type='lxml')
contents += load_contents('UnderstandingAI', 'https://www.understandingai.org/feed')
contents += load_contents('Yglesias', 'https://www.slowboring.com/feed')
contents += load_contents('Zvi', 'https://thezvi.substack.com/feed')

print('-')
print('Gathering content')
random.shuffle(contents)


# Dump into DB
print('-')
print('Psycopg2 connect')
DATABASE_URL = os.environ.get('DATABASE_URL', 'dbname=stanza_dev user=dbuser')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

print('-')
print('Data export')
export_db(cur)


# Clean
links = pd.read_csv('data/export.csv')
print('-')
print('Purging broken links')
nans_if_any = links[links['id'].astype('str') == 'nan']

broken = links[~links['url'].apply(lambda u: isinstance(u, str) and 'http' in u)]['id']
lines = len(broken)
if lines:
    broken = list(filter(lambda x: ~np.isnan(x), broken.values))
    lines = len(broken)

if len(nans_if_any) > 0:
    links = links.dropna()
    lines += 1

if lines == 0:
    print('...No broken links detected')
else:
    for i, id_ in enumerate(broken):
        id_ = int(id_)
        delete_link_row(cur, id_)
    print('...{} broken links purged!'.format(lines))

print('-')
print('Calculating links to add')
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

print('-')
print('Purging duplicated')
duplicated = links[links['url'].duplicated(keep=False)]['id']
lines = len(duplicated)
if lines == 0:
    print('...No duplicated links detected')
else:
    for i, id_ in enumerate(duplicated):
        if i % 2 == 0:
            star_row(cur, id_)
        else:
            delete_link_row(cur, id_)
    print('...{} duplicated links purged!'.format(lines / 2))

print('-')
print('Purging old')
links['liked'] = links['liked'].apply(lambda x: np.nan if str(x) == '\\N' else str(x).split('.')[0]).astype(float)
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

print('-')
print('Purging long old')
links['liked'] = links['liked'].apply(lambda x: np.nan if str(x) == '\\N' else str(x).split('.')[0]).astype(float)
links['added'] = pd.to_datetime(links['added'], utc=True).dt.tz_localize(None)
relative_now = links['added'].max()
before_purge_window = relative_now - timedelta(days=LONG_PURGE_OLDER_THAN_X)
purgable = links[(links['aggregator'].apply(lambda a: a in LONG_PURGABLE_AGGREGATORS)) &
                 (links['added'] < before_purge_window) &
                 (links['liked'] != 0) &
                 (links['liked'] != 1) &
                 (links['liked'] != -1)]
purgable = purgable['id']
lines = len(purgable)
if lines == 0:
    print('...No long old-purgable links detected')
else:
    for i, id_ in enumerate(purgable):
        hide_row(cur, id_)
    print('...{} long old links purged!'.format(lines))

print('-')
print('Purging obsolete')
obsolete = links[(links['aggregator'].apply(lambda a: a in OBSOLETE_AGGREGATORS)) &
                 (links['liked'] != 0) & (links['liked'] != 1) & (links['liked'] != -1)]
obsolete_ids = list(obsolete['id'].values)

# Kill Yglesias's "X Thread"
# TODO: This doesn't work!
obsolete = links[(links['aggregator'] == 'Yglesias') & links['title'].apply(lambda t: 'Thread' in str(t)) &
                 (links['liked'] != 0) & (links['liked'] != 1) & (links['liked'] != -1)]
obsolete_ids += list(obsolete['id'].values)

lines = len(obsolete_ids)
if lines == 0:
    print('...No obsolete links detected')
else:
    for i, id_ in enumerate(obsolete_ids):
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

