from os.path import join
from twarc import Twarc2
import pandas as pd
import os
from datetime import datetime, timedelta

# from https://emojipedia.org/people/
emojis = {
    'wavinghand':"👋",
    'raisedhand':"✋",
    'raisedbackhand':"🤚",
    'vulcansalute':"🖖",
    'okhand':"👌",
    'pinchedfingers':"🤌",
    'pinchinghand':"🤏",
    'victoryhand':"✌️",
    'crossedfingers':"🤞",
    'loveyougesture':"🤟",
    'signofthehorns':"🤘",
    'callmehand':"🤙",
    'backhandindexpointingleft':"👈",
    'backhandindexpointingright':"👉",
    'backhandindexpointingup':"👆",
    'middlefinger':"🖕",
    'backhandindexpointingdown':"👇",
    'indexpointingup':"☝️",
    'thumbsup':"👍",
    'thumbsdown':"👎",
    'raisedfist':"✊",
    'oncomingfist':"👊",
    'leftfacingfist':"🤛",
    'rightfacingfist':"🤜",
    'clappinghands':"👏",
    'raisinghands':"🙌",
    'openhands':"👐",
    'palmsuptogether':"🤲",
    'handshake':"🤝",
    'foldedhands':"🙏"
}

# from https://developer.twitter.com/en/docs/twitter-for-websites/supported-languages
# and https://backlinko.com/twitter-users
languages = ['en', 'it', 'de', 'fr', 'es',
             'ru', 'id', 'pt', 'tr', 'ar',
             'hi', 'ja', 'ko', 'th']

def get_stopwords(language):
    sw = []
    with open(join("stopwords", f"{language}_stopwords.txt"), "r") as f:
        for l in f.readlines():
            sw.append(l.strip("\n").replace("\t", ""))
    return sw

#from https://www.ranks.nl/stopwords/
stopwords = {
    'en':get_stopwords('en'),
    'it':get_stopwords('it'),
    'de':get_stopwords('de'),
    'fr':get_stopwords('fr'),
    'es':get_stopwords('es'),
    'ru':get_stopwords('ru'),
    'id':get_stopwords('id'),
    'pt':get_stopwords('pt'),
    'tr':get_stopwords('tr'),
    'ar':get_stopwords('ar'),
    'hi':get_stopwords('hi'), 
    'ja':get_stopwords('ja'), 
    'ko':get_stopwords('ko'), 
    'th':get_stopwords('th'), 
}

def get_credentials():
    credentials = {}
    for name in ['jana', 'david', 'max', 'hannah', 'alina', 'anna']:
        tmp = {}
        with open(join("API_keys", f"twitter_API_{name}.txt"), 'r') as f:
            for l in f:
                tmp[l.split('=')[0]] = l.split('=')[1].strip('\n')
        credentials[name] = tmp['bearer_token']
    return credentials


def get_stopword_query(language):
    words = stopwords[language]
    query = '('
    i = 0
    # needs to accommodate the "lang: xy" string in the 1024 characters
    while len(query) < 1009 and i < len(words): 
        word = words[i]
        if "'" in word: #or len(word) == 1: 
            i += 1
            continue
        query += word
        query += ' OR '
        i += 1
    query = query[0:-4]
    query += ')'
    return query


def get_counts(info):
    '''
    Gets the daily tweet counts between a start time and an end
    time given a language and search string, using Twarc to access
    the Twitter v2 API.
    '''
    t = Twarc2(bearer_token=info['bearer_token'])
    string = info["string"]
    language = info["language"]
    search_string = f"{string} lang:{language}"
    color = info["color"]
    start = info["start"]
    end = info["end"]
    dst = info["dst"]
    
    counts = pd.DataFrame()
    for c in t.counts_all(
        search_string,
        start_time=start,
        end_time=end,
        granularity='day'):
        
        counts = counts.append(c['data'], ignore_index=False)
        
    if len(counts) == 0:
        print(f"no counts received for {language} {string} {start} to {end}")
        return
    
    counts['start'] = pd.to_datetime(counts['start'])
    counts['end'] = pd.to_datetime(counts['end'])
    counts = counts.sort_values(by='start')
    counts = counts.drop(columns=["end"]).rename(columns={"start":"date"})
    counts["date"] = counts["date"].apply(lambda x: x.date)
    dump_counts(counts, language, string, color, start, end, dst)
    return counts


    

def dump_counts(df, language, emoji, color, start, end, dst):
    '''
    Save the daily tweet counts for a given language and search string as
    .csv file.
    '''
   
    #s = str(start.date())
    #e = str(end.date())
    
    if color == None:
        df.to_csv(join(dst, lang,
        f"counts_language-{language}_baseline_{start}-to-{end}.csv"),
                   index=False)
    else:
        df.to_csv(join(dst, lang,
        f"counts_language-{language}_emoji-{emoji}_color-{color}_{start}-to-{end}.csv"),
                   index=False)
        
        
def create_stopword_combinations(language, start, end, timewindow, credentials,
                                 dst):
    '''
    Creates a list of dictionaries with the information necessary to query the
    counts for the stopwords of a given language. Count queries need to be split
    up into smaller time windows to until each query returns < 55 mio counts, 
    otherwise the API request fails.
    
    Parameters:
    -----------
    language: str
        Two-letter string indicating the language for the twitter APi query.
    start: datetime
        Datetime object indicating the start of the queried period.
    end: datetime
        Datetime object indicating the end of the queried period.
    timewindow: int
        Time period of a single query in hours.
    credentials: dict
        Dictionary with the bearer tokens for the twitter v2 API
        
    '''
    sw_query = get_stopword_query(language)
    langdst = join(dst, language)
    
    if type(start) == datetime:
        duration = (end - start).days

        combinations = [{"language":language,
                         "string":sw_query,
                         "bearer_token":"", 
                         "color":None,
                         "start":start + timedelta(hours=i * timewindow),
                         "end":start + timedelta(hours=(i + 1) * timewindow),
                         "dst":langdst}\
                    for i in range(duration * int(24 / timewindow))] 
        
    elif type(start) == list:
        combinations = []
        for s in start:
            combinations.append({"language":language,
                                 "string":sw_query,
                                 "bearer_token":"",
                                 "color":None,
                                 "start":s,
                                 "end": s + timedelta(hours=timewindow),
                                 "dst":langdst})
    else:
        print(f"unknown start type {type(start)}")
        return None
    
    credlist = list(credentials.values()) * (int(len(combinations) \
                                          / len(credentials)) + 1)
    for i in range(len(combinations)):
        combinations[i]['bearer_token'] = credlist[i]
        
    return combinations


def get_missing_combinations(language, start, end, timewindow, credentials, dst):
    existing_starts = []
    files = os.listdir(join(dst, language))
    for f in files:
        counts, lang, mode, startend = f.split("_")
        s, e = startend.strip(".csv").split("-to-")
        existing_starts.append(pd.to_datetime(s))

    existing_starts = set(existing_starts)
    wanted_starts = create_stopword_combinations(\
        language, start, end, timewindow, credentials, dst)
    wanted_starts = set([ws["start"] for ws in wanted_starts])
    missing_starts = list(wanted_starts.difference(existing_starts))
    missing_starts.sort()
    
    combinations = create_stopword_combinations(language, missing_starts,
                                                   None, 12, credentials, dst)
    
    return combinations


def split_count_timewindow(missing_counts):
    timewindow = (missing_counts[0]["end"] - missing_counts[0]["start"]).seconds / (60 * 60) / 2
    language = missing_counts[0]["language"]
    string = missing_counts[0]["string"]
    color = missing_counts[0]["color"]
    dst = missing_counts[0]["dst"]
    
    new_missing_counts = []
    for mc in missing_counts:
        new_missing_counts.append({
            "language":language,
            "string":string,
            "bearer_token":mc["bearer_token"],
            "color":color,
            "start":mc["start"],
            "end":mc["start"] + timedelta(hours = timewindow),
            "dst":dst
        })
        
        new_missing_counts.append({
            "language":language,
            "string":string,
            "bearer_token":mc["bearer_token"],
            "color":color,
            "start":mc["start"] + timedelta(hours = timewindow),
            "end":mc["end"],
            "dst":dst
        })
        
    return new_missing_counts