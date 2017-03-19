# -*- coding: utf-8 -*-
#
# This file is part of the gocomics project
#
# Copyright (c) 2017 Tiago Coutinho
# Distributed under the MIT license. See LICENSE for more info.

"""gocomics downloader"""

import os
import sys
import logging
import datetime
import functools

import gevent
import gevent.pool
import grequests
from requests.exceptions import ConnectionError

from bs4 import BeautifulSoup

__version__ = '0.0.1'

site = 'http://www.gocomics.com/{0}'

def from_user_date(date):
    if isinstance(date, datetime.date):
        return date
    return datetime.date(*map(int, date.split('-')))

def idates(start, end=datetime.date.today(), step=datetime.timedelta(days=1)):
    start = from_user_date(start)
    end = from_user_date(end)
    date = start
    while date < end:
        yield date
        date += step

def get_pool(pool=None, size=5):
    return gevent.pool.Pool(size=size) if pool is None else pool

def get_url(url, retries=5):
    logging.info("Asking for %s...", url)
    req = None
    while retries:
        req = grequests.get(url).send()
        logging.info("Got %s...", url)
        if req.response is None:
            if hasattr(req, "exception"):
                if type(req.exception) == ConnectionError:
                    logging.warning('Failed to get %s (retries left=%d). Retrying...',
                                    url, retries)
                    retries -= 1
                    continue
            else:
                break
        else:
            break

    if req.response is None:
        logging.error('Failed to get %s (retries left=%d). Skipping...',
                      url, retries)
    return req

def get_url_content(url, retries=5):
    resp = get_url(url, retries=retries).response
    if resp is None:
        return resp
    return resp.content

def get_url_page(url, retries=5):
    resp = get_url_content(url, retries=retries)
    if resp is None:
        return resp
    return BeautifulSoup(resp, 'html.parser')

def get_page_image_url(page, retries=5):
    page = get_url_page(page, retries=retries)
    return page.find(attrs={'class':'item-comic-image'}).img['src']

def process_page(url, page, out_dir="."):
    url = '{0}/{1}'.format(url, page.strftime('%Y/%m/%d'))
    try:
        image_url = get_page_image_url(url)
    except:
        logging.error('Failed to get page %s', page, exc_info=1)
        return
    file_name = str(page)
    logging.info('Processing %s', file_name)
    path = os.path.abspath(out_dir)
    full_name = os.path.join(path, file_name)
    if os.path.exists(full_name):
        logging.warning("%s already exists. Skipping...", full_name)
        return
    image = get_url_content(image_url)
    if image is None:
        return
    if not os.path.isdir(path):
        os.makedirs(path)
    with open(full_name, mode="wb") as f:
        f.write(image)
    logging.info("Saved %s in %s", file_name, path)

def find_first(url):
    page = get_url_page(url)
    ref = page.find(attrs={'class':'fa-backward'})['href']
    args = map(int, ref.rsplit('/', 3)[-3:])
    return datetime.date(*args)

def process(url, out_dir=".", pages=None, pool=None):
    pool = get_pool(pool)
    Task = functools.partial(pool.spawn, process_page,
                             out_dir=out_dir)
    pages = tuple(pages or idates())
    urls = len(pages)*[url]
    logging.info('Fetching pages [%s, %s] from %s (parallel=%d)',
                 pages[0], pages[-1], url, pool.size)
    tasks = map(Task, urls, pages)
    gevent.joinall(tuple(tasks))

def _ils():
    pages = 'a-b', 'c-e', 'f-i', 'j-n', 'o-r', 's-t', r'u-%23'
    for page_id in pages:
        comics = {}
        url = site.format('comics/a-to-z?page=' + page_id)
        page = get_url_page(url)
        for item in page.find_all(attrs={'class':'amu-media-item-link'}):
            url = site + item['href']
            data = tuple(item.find(attrs={'class':'media-body'}).stripped_strings)
            title = data[0]
            author = data[1] if len(data) > 1 else '?'
            cid = item['href'].strip('/')
            comics[cid] = dict(url=url, title=title, author=author)
        yield comics

def _ls():
    comics = {}
    for c in _ils():
        comics.update(c)
    return comics

def ls():
    for comics in _ils():
        for key in sorted(comics):
            comic = comics[key]
            print(u'{0:>24}: {1:>24} - {2}'.format(key, comic['title'], comic['author']))

def __main():
    import sys
    import time
    import argparse
    start = time.time()
    parser = argparse.ArgumentParser(description='gocomics downloader',
                                     version=__version__)
    parser.add_argument('--logging-level', default='INFO')
    subparsers = parser.add_subparsers(title='operation', dest='operation',
                                       description='type of operation',
                                       help='which operation to perform')

    ls_parser = subparsers.add_parser('ls', help='list available comics')

    fetch_parser = subparsers.add_parser('fetch', help='fetch a comic')
    add = fetch_parser.add_argument
    add('comic')
    add('-o', '--output-dir', default='')
    add('-s', '--start-date', default='')
    add('-e', '--end-date', default=datetime.date.today())
    add('--max-parallel', default=5, type=int)

    args = parser.parse_args()

    level = getattr(logging, args.logging_level.upper())
    logging.basicConfig(level=level, format="%(levelname)-8s %(message)s")

    if args.operation == 'ls':
        ls()
    elif args.operation == 'fetch':
        comic = args.comic
        url = site.format(comic)
        out_dir = args.output_dir if args.output_dir else '~/Downloads/{0}'.format(comic)
        start_date = args.start_date if args.start_date else find_first(url)
        pages = idates(start_date, args.end_date)
        pool = get_pool(size=args.max_parallel)
        process(url, out_dir=os.path.expanduser(out_dir), pages=pages, pool=pool)
        logging.info('Took %ss', time.time()-start)

def main():
    try:
        __main()
    except KeyboardInterrupt:
        print('Ctrl-C pressed. Bailing out...')

if __name__ == "__main__":
    main()
