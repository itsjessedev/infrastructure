$ErrorActionPreference = 'Stop'

# Paths
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$outputPath = '/mnt/c/Users/Jesse/OneDrive/Media Server/franchise_check.md'

# Python script content (runs on eldridge-media)
$py = @'
import urllib.request, urllib.parse, json
import xml.etree.ElementTree as ET
from pathlib import Path
import re
from datetime import datetime
from difflib import SequenceMatcher

PLEX_URL='http://localhost:32400'
CONFIG=Path('/srv/docker/kometa/config/config.yml')
LIBRARIES=['Movies','Kids Movies']
EXCLUDE_COLLECTIONS={'Sleighlist Spotlight'}
CURRENT_YEAR=datetime.utcnow().year

section=None; token=None; tmdb_key=None
for raw in CONFIG.read_text().splitlines():
    if not raw.strip():
        continue
    if not raw.startswith(' '):
        section=raw.rstrip(':')
        continue
    if section=='plex' and raw.strip().startswith('token:'):
        token=raw.split(':',1)[1].strip()
    if section=='tmdb' and raw.strip().startswith('apikey:'):
        tmdb_key=raw.split(':',1)[1].strip()
if not token or not tmdb_key:
    raise SystemExit('missing tokens')

def normalize(t: str) -> str:
    t=t.lower().replace('&',' and ')
    t=t.replace(' iii',' 3').replace(' ii',' 2').replace(' iv',' 4').replace(' vi',' 6').replace(' vii',' 7').replace(' viii',' 8').replace(' ix',' 9').replace(' x',' 10')
    t=re.sub(r"[^a-z0-9]+",' ',t)
    t=re.sub(r"\\b(the|a|an)\\b",' ',t)
    t=re.sub(r"\\s+",' ',t).strip()
    return t

def strict_match(nt, have_set):
    if nt in have_set:
        return True
    for h in have_set:
        if abs(len(h)-len(nt))<=1 and SequenceMatcher(None, nt, h).ratio()>=0.97:
            return True
    return False

def plex_fetch(url):
    authed=url+('&' if '?' in url else '?')+'X-Plex-Token='+urllib.parse.quote(token)
    with urllib.request.urlopen(urllib.request.Request(authed, headers={'Accept':'application/xml'})) as r:
        return ET.fromstring(r.read())

def tmdb_get(path, params=None):
    if params is None: params={}
    params['api_key']=tmdb_key
    qs=urllib.parse.urlencode(params)
    url=f"https://api.themoviedb.org/3{path}?{qs}"
    with urllib.request.urlopen(url) as r:
        return json.load(r)

def tmdb_id_by_title_year(title, year):
    try:
        res=tmdb_get('/search/movie', {'query': title, 'year': year or ''})
    except Exception:
        return None, None
    results=res.get('results') or []
    if not results:
        return None, None
    m=results[0]
    return m.get('id'), m.get('belongs_to_collection') and m['belongs_to_collection'].get('id')

sections=plex_fetch(f"{PLEX_URL}/library/sections")
lib_keys={}
for d in sections.findall('.//Directory'):
    if d.attrib.get('title') in LIBRARIES:
        lib_keys[d.attrib.get('title')]=d.attrib.get('key')

collection_members={}
items_info=[]
for key in lib_keys.values():
    vids=plex_fetch(f"{PLEX_URL}/library/sections/{key}/all?type=1&X-Plex-Container-Size=8000")
    for v in vids.findall('.//Video'):
        title=v.attrib.get('title') or ''
        year=v.attrib.get('year')
        nt=normalize(title)
        colls=[c.attrib.get('tag') for c in v.findall('Collection') if c.attrib.get('tag')]
        items_info.append({'title': title, 'year': year, 'collections': colls})
        for c in colls:
            collection_members.setdefault(c,set()).add(nt)

coll_to_tmdb_ids={}
for item in items_info:
    t=item['title']; y=item['year']
    _, cid = tmdb_id_by_title_year(t, y)
    if cid:
        for coll in item['collections']:
            coll_to_tmdb_ids.setdefault(coll, set()).add(cid)

canonical_map = {
    "Tom and Jerry Collection": [
        ("Tom and Jerry: The Movie", 1992),
        ("Tom and Jerry: The Magic Ring", 2002),
        ("Tom and Jerry: Blast Off to Mars", 2005),
        ("Tom and Jerry: The Fast and the Furry", 2005),
        ("Tom and Jerry: Shiver Me Whiskers", 2006),
        ("Tom and Jerry: A Nutcracker Tale", 2007),
        ("Tom and Jerry Meet Sherlock Holmes", 2010),
        ("Tom and Jerry and the Wizard of Oz", 2011),
        ("Tom and Jerry: Robin Hood and His Merry Mouse", 2012),
        ("Tom and Jerry’s Giant Adventure", 2013),
        ("Tom and Jerry: The Lost Dragon", 2014),
        ("Tom and Jerry: Spy Quest", 2015),
        ("Tom and Jerry: Back to Oz", 2016),
        ("Tom and Jerry: Willy Wonka and the Chocolate Factory", 2017),
        ("Tom and Jerry: Cowboy Up!", 2022),
    ],
    "Scooby-Doo Animated Collection": [
        ("Scooby-Doo Meets the Boo Brothers", 1987),
        ("Scooby-Doo and the Ghoul School", 1988),
        ("Scooby-Doo and the Reluctant Werewolf", 1988),
        ("Scooby-Doo on Zombie Island", 1998),
        ("Scooby-Doo and the Witch's Ghost", 1999),
        ("Scooby-Doo and the Alien Invaders", 2000),
        ("Scooby-Doo and the Cyber Chase", 2001),
        ("Scooby-Doo! and the Samurai Sword", 2009),
        ("Scooby-Doo! Abracadabra-Doo", 2010),
        ("Scooby-Doo! Camp Scare", 2010),
        ("Scooby-Doo! Legend of the Phantosaur", 2011),
        ("Scooby-Doo! Music of the Vampire", 2012),
        ("Scooby-Doo! Stage Fright", 2013),
        ("Scooby-Doo! Mask of the Blue Falcon", 2013),
        ("Scooby-Doo! Frankencreepy", 2014),
        ("Scooby-Doo! Moon Monster Madness", 2015),
        ("Scooby-Doo! and WWE: Curse of the Speed Demon", 2016),
        ("Scooby-Doo! and the Gourmet Ghost", 2018),
        ("Happy Halloween, Scooby-Doo!", 2020),
        ("Scooby-Doo! The Sword and the Scoob", 2021),
        ("Trick or Treat Scooby-Doo!", 2022),
    ],
}

pre1980_allow = {
    'aladdin collection': {'aladdin'},
    '101 dalmatians collection': {'one hundred and one dalmatians'},
    'the lion king collection': {'the lion king'},
    'beauty and the beast collection': {'beauty and the beast'},
    'cinderella collection': {'cinderella'},
    'the jungle book collection': {'the jungle book'},
}

deny_by_collection = {
    'batman collection': {'ninja'},
    'sherlock holmes collection': {'hound of the baskervilles','adventures of sherlock holmes','sherlock holmes and the voice of terror','pursuit to algiers','terror by night','dressed to kill','the woman in green','scarlet claw','pearl of death','house of fear','spider woman','secret weapon','sherlock holmes in washington','faces death'},
}

def tmdb_collection_parts_by_id(cid):
    try:
        coll=tmdb_get(f'/collection/{cid}')
    except Exception:
        return []
    out=[]
    for p in coll.get('parts', []):
        title=p.get('title') or p.get('original_title')
        date=p.get('release_date') or ''
        year=int(date[:4]) if date and re.match(r"\\d{4}", date) else None
        if title:
            out.append((title, year))
    return out

missing_by_coll={}
for coll_name, have_set in collection_members.items():
    if coll_name in EXCLUDE_COLLECTIONS:
        continue
    parts=[]
    for cid in coll_to_tmdb_ids.get(coll_name, set()):
        parts.extend(tmdb_collection_parts_by_id(cid))
    parts += canonical_map.get(coll_name, [])
    if not parts:
        continue
    miss=[]
    for title, year in parts:
        if year is None or year> CURRENT_YEAR:
            continue
        if year < 1980:
            allowed = pre1980_allow.get(coll_name.lower(), set())
            if normalize(title) not in allowed:
                continue
        norm_title=normalize(title)
        deny_terms=deny_by_collection.get(coll_name.lower(), set())
        if any(term in norm_title for term in deny_terms):
            continue
        if not strict_match(norm_title, have_set):
            label=f"{title} ({year})"
            if label not in miss:
                miss.append(label)
    if miss:
        missing_by_coll[coll_name]=sorted(miss)

franchise_map = {
    '3 ninjas': ['3 Ninjas Kick Back (1994)', '3 Ninjas Knuckle Up (1995)', '3 Ninjas: High Noon at Mega Mountain (1998)'],
    'air bud': ['Air Bud: Golden Receiver (1998)', 'Air Bud: World Pup (2000)', 'Air Bud: Seventh Inning Fetch (2002)', 'Air Bud: Spikes Back (2003)'],
    'anastasia': ['Bartok the Magnificent (1999)'],
    'bambi ii': ['Bambi (1942)'],
    'beetlejuice beetlejuice': ['Beetlejuice (1988)'],
    'cars 3': ['Cars (2006)', 'Cars 2 (2011)'],
    'clash of the titans': ['Wrath of the Titans (2012)'],
    'constantine': ['Constantine 2 (planned)'],
    'ernest scared stupid': ['Ernest Goes to Camp (1987)', 'Ernest Saves Christmas (1988)', 'Ernest Goes to Jail (1990)', 'Ernest Rides Again (1993)', 'Slam Dunk Ernest (1995)'],
    'finding dory': ['Finding Nemo (2003)'],
    'freaky friday': ['Freaky Friday (1976)', 'Freaky Friday (1995)', 'Freaky Friday (2003)', 'Freaky Friday (upcoming sequel)'],
    'frozen': ['Frozen II (2019)'],
    'ghost in the shell': ['Ghost in the Shell (1995)', 'Ghost in the Shell 2: Innocence (2004)', 'Ghost in the Shell 2.0 (2008)', 'Ghost in the Shell: SAC - Solid State Society (2006)'],
    'inside out': ['Inside Out 2 (2024)'],
    'kick ass 2': ['Kick-Ass (2010)'],
    'kung fu panda': ['Kung Fu Panda 2 (2011)', 'Kung Fu Panda 3 (2016)', 'Kung Fu Panda 4 (2024)'],
    'lilo stitch': ['Stitch! The Movie (2003)', 'Lilo & Stitch 2: Stitch Has a Glitch (2005)', 'Leroy & Stitch (2006)'],
    'mighty morphin power rangers': ['Mighty Morphin Power Rangers: The Movie (1995)', 'Turbo: A Power Rangers Movie (1997)', 'Power Rangers (2017)'],
    'mulan ii': ['Mulan (1998)', 'Mulan (2020)'],
    'peter pan wendy': ['Peter Pan (1953)', 'Return to Never Land (2002)', 'Peter Pan (2003)', 'Pan (2015)'],
    'scott pilgrim vs the world': ['Scott Pilgrim Takes Off (2023 series)'],
    'shaun of the dead': ['Hot Fuzz (2007)', "The World's End (2013)"],
    'the jetsons meet the flintstones': ['The Man Called Flintstone (1966)', 'The Flintstones (1994)', 'The Flintstones in Viva Rock Vegas (2000)'],
    'the lord of the rings the war of the rohirrim': ['The Fellowship of the Ring (2001)', 'The Two Towers (2002)', 'The Return of the King (2003)', 'The Hobbit: An Unexpected Journey (2012)', 'The Desolation of Smaug (2013)', 'The Battle of the Five Armies (2014)'],
    'the new mutants': ['X-Men series (add to X-Men Collection)'],
    'watchmen chapter i': ['Watchmen (2009)', 'Watchmen: Chapter II (upcoming)'],
    'wonka': ['Willy Wonka & the Chocolate Factory (1971)', 'Charlie and the Chocolate Factory (2005)'],
}

franchise_results={}
for title, year in sorted([(i['title'], i['year']) for i in items_info if not i['collections']], key=lambda x: normalize(x[0])):
    nt=normalize(title)
    if nt in franchise_map:
        label=f"{title} ({year})" if year else title
        franchise_results[label]=franchise_map[nt]

lines=[]
lines.append('# Franchise Gaps & Opportunities (TMDB IDs from library, canonical supplements, strict match)')
lines.append('')
lines.append('## Existing Collections – Missing Titles (not in library)')
if not missing_by_coll:
    lines.append('(none)')
    lines.append('')
else:
    for coll in sorted(missing_by_coll):
        lines.append(coll)
        lines.append('-'*len(coll))
        for t in missing_by_coll[coll]:
            lines.append(t)
        lines.append('')
lines.append('## Single Titles That Can Form Collections (only titles currently in library)')
if not franchise_results:
    lines.append('(none)')
else:
    for title in sorted(franchise_results):
        lines.append(title)
        lines.append('-'*len(title))
        for need in franchise_results[title]:
            lines.append(need)
        lines.append('')

print('\\n'.join(lines))
'@

# Base64-encode the Python payload to avoid quoting issues
$bytes = [System.Text.Encoding]::UTF8.GetBytes($py)
$b64 = [Convert]::ToBase64String($bytes)
$remoteCmd = "echo $b64 | base64 -d > /tmp/franchise_audit.py && python3 /tmp/franchise_audit.py"

# Execute remotely and capture output
$output = ssh eldridge-media $remoteCmd

# Save locally
Set-Content -Path $outputPath -Value $output -Encoding UTF8

Write-Host "franchise-audit report written to $outputPath"
