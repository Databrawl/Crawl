import re
from operator import itemgetter

from src.utils import timeit

WHITELIST = set()
URL_RE = re.compile(r'^(.*http(s)?://|www.)|.(com|it|net|org)($|/)')
TOKEN_RE = re.compile(r"[^\W_]+(?:'(?:d|ll|m|re|s|t|ve))?")
REFERENCE_RE = re.compile(r'/?[ur]/\w+\Z')
MARKOV_RE = re.compile(
    r"[\[(\"']?[^\W_]+(?:\'(?:d|ll|m|re|s|t|ve))?[.?\]/):,\"']?")

# Whitelist from http://www.ranks.nl/stopwords
try:
    with open('Data/whitelist.txt', 'r') as f:
        for stopword in f.readlines():
            WHITELIST.add(stopword.strip())
except FileNotFoundError:
    print('ERROR: Data/whitelist.txt file missing from folder.')


# URL_RE and TOKEN_RE patterns from https://github.com/rhiever

class CorpusMetadata:
    def __init__(self, corpus):

        # Initialization
        self.words = {}
        self.domains = {'Self Text': 0, 'Images': 0, 'Tweets': 0, 'Videos': 0,
                        'Links': 0}
        self.corpus = corpus

        # Markov chain
        self.word_chain = {}
        self.start_words = []

    @timeit
    def _count_words(self):
        for token in get_tokens(self.corpus):
            self.words[token] = self.words.get(token, 0) + 1
        for word, count in self.words.items():
            if word.endswith('s'):
                singular = word[:-1]
                if self.words.get(singular):
                    # Combine plurals and singulars into the most-used form
                    if self.words[singular] > count:
                        self.words[singular] += self.words[word]
                        self.words[word] = 0
                    else:
                        self.words[word] += self.words[singular]
                        self.words[singular] = 0

        return {word: count for word, count in self.words.items()
                if count > 10}

    @timeit
    def _count_domains(self):
        images = ['i.imgur.com', 'imgur.com', 'gfycat.com', 'media.giphy.com',
                  'i.redd.it', 'i.reddituploads.com',
                  'pbs.twimg.com', 'instagram.com']
        tweets = ['twitter.com']
        videos = ['youtube.com', 'streamable.com', 'youtu.be', 'vimeo.com',
                  'vid.me', 'v.redd.it']
        for submission in filter(
                lambda word: URL_RE.search(word) or REFERENCE_RE.search(word),
                self.corpus):
            # TODO: fix this
            domain = URL_RE.search(word) or REFERENCE_RE.search(word)
            # domain = submission.domain
            if domain.startswith('self.'):
                self.domains['Self Text'] = self.domains.get('Self Text', 0) + 1
            elif domain in images:
                self.domains['Images'] = self.domains.get('Images', 0) + 1
            elif domain in tweets:
                self.domains['Tweets'] = self.domains.get('Tweets', 0) + 1
            elif domain in videos:
                self.domains['Videos'] = self.domains.get('Videos', 0) + 1
            else:
                self.domains['Links'] = self.domains.get('Links', 0) + 1

    def analyze(self):
        # self._count_domains()
        self._count_words()

    def top_words(self):
        word_list = ((word, count) for word, count in self.words.items())
        return sorted(word_list, key=itemgetter(1), reverse=True)


def clean_comment(comment):
    if comment in ('[removed]', '[deleted]'):
        return
    cleaned = []
    for word in comment.split():
        if URL_RE.search(word) or REFERENCE_RE.search(word):
            # Word is url or reference to user/subreddit
            continue
        for token in MARKOV_RE.findall(word):
            if token == 'nbsp':
                continue
            cleaned.append(token)
    with open('../Logs/comments_log.txt', 'a+') as file:
        file.write(comment)  # Log for all comments analyzed
    return cleaned


def get_tokens(comments):
    for comment in comments:
        if comment in ('[removed]', '[deleted]'):
            continue
        for word in comment.split():
            if URL_RE.search(word) or REFERENCE_RE.search(word):
                # Word is url or reference to user/subreddit
                continue
            else:
                for token in TOKEN_RE.findall(word):
                    if token.endswith("'s"):  # Fix possessives
                        token = token[:-2]
                    if token.lower() in WHITELIST or token.isdecimal() or token == 'nbsp':  # Ignore word
                        continue
                    yield token.lower()
