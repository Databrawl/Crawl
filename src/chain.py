import random
import re

from src.text_analysis import clean_comment


def get_markov_chain(corpus=None):
    if corpus:
        markov_chain_sentence = generate_markov_chain(corpus.start_words,
                                                      corpus.word_chain)
        canvas.create_text(self.width / 2, 200, text=markov_chain_sentence,
                           width=500,
                           font='TkDefaultFont 20')
    else:
        words = []
        with open('Data/preloaded_comments.txt', 'r') as file:
            for line in file.readlines():
                words.append(line)
        word_chain = generate_word_chain(words)
        start_words = [key for key in word_chain.keys() if key[0][0].isupper()]
        markov_chain_sentence = generate_markov_chain(start_words, word_chain)
        canvas.create_text(self.width / 2, 200, text=markov_chain_sentence,
                           width=500,
                           font='TkDefaultFont 20')
    return markov_chain_sentence


def generate_word_chain(corpus):
    word_chain = {}
    for comment in corpus:
        comment = clean_comment(comment)
        if not comment:
            continue
        for i, word in enumerate(comment):
            try:
                first, second, third = comment[i], comment[i + 1], comment[
                    i + 2]
            except IndexError:
                break
            key = (first, second)
            if key not in word_chain:
                word_chain[key] = []
            word_chain[key].append(third)
    return word_chain


def generate_markov_chain(start_words, word_chain):
    """ Algorithm from www.onthelambda.com. """
    if not start_words:
        return None
    first, second = random.choice(start_words)

    sentence = [first, second]
    max_len = 0
    while max_len < 50:
        try:
            third = random.choice(word_chain[(first, second)])
        except KeyError:
            break
        sentence.append(third)
        if third[-1] in {'!', '.', '?'}:
            break
        first, second = second, third
        max_len += 1

    return ' '.join(sentence)


MARKOV_RE = re.compile(
    r"[\[(\"']?[^\W_]+(?:\'(?:d|ll|m|re|s|t|ve))?[.?\]/):,\"']?")


def build_markov_chain(self):
    self.word_chain = generate_word_chain(self.corpus)
    self.start_words = [key for key in self.word_chain.keys() if
                        key[0][0].isupper()]
