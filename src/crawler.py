import logging

import praw

from src.utils import timeit

REDDIT = praw.Reddit(client_id='wUZpv15zMB-TTQ',
                     client_secret='8h8PaAufQ4xjrpuH6wcwI14pzyU',
                     user_agent='MacOS:Crawl:v1.0 (by /u/Crawl112)',
                     username='Crawl112',
                     password='15112cmu')


def create_iterable_by_sort(obj, sort):
    if sort == 'top':
        return obj.top()
    elif sort == 'new':
        return obj.new()
    elif sort == 'controversial':
        return obj.controversial()
    elif sort == 'hot':
        return obj.hot()


def get_submissions(type_, name, sort):
    if type_ == 'User':
        return create_iterable_by_sort(REDDIT.redditor(name).submissions, sort)
    else:
        return create_iterable_by_sort(REDDIT.subreddit(name), sort)


def _crawl_user(user, sort='top'):
    comments = []
    user = REDDIT.redditor(user)
    for submission in create_iterable_by_sort(user.submissions, sort):
        comments.extend([submission.title, submission.selftext])
    for comment in create_iterable_by_sort(user.comments, sort):
        comments.append(comment.body)

    logging.info(f'Number of comments and submissions analyzed: '
                 f'{len(comments)}')
    return comments


def _crawl_submission(submission, comment_sort):
    submission.comment_sort = comment_sort
    submission.comments.replace_more(limit=0)
    flat_comments = submission.comments.list()
    comments = [comm.body for comm in flat_comments]
    comments.extend([submission.title, submission.selftext])
    return comments


def _crawl_subreddit(subreddit):
    comment_sort = 'top'
    comments = []
    i = 0
    for submission in create_iterable_by_sort(REDDIT.subreddit(subreddit),
                                              comment_sort):
        i += 1
        # TODO: add crawling submission text itself
        comments.extend(_crawl_submission(submission, comment_sort))
        if i > 1:
            break
    logging.info(f'Number of submissions analyzed: {i}\n'
                 f'Number of comments analyzed: {len(comments)}\n')

    return comments


@timeit
def crawl(type_, name):
    if type_ == 'User':
        corpus = _crawl_user(name)
    else:
        corpus = _crawl_subreddit(name)

    return corpus
