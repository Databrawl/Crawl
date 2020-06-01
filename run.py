import logging

from src import crawler, text_analysis
from src.utils import init_logging

init_logging()

if __name__ == '__main__':
    corpus = crawler.crawl(type_='Subreddit', name='financialindependence')
    corpus_meta = text_analysis.CorpusMetadata(corpus)
    corpus_meta.analyze()

    logging.info('### Report ###')
    logging.info('Most popular words:')
    logging.info(corpus_meta.top_words())
