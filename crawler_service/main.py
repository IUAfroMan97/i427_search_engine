import time
import os
import sys

import multiprocessing as mp
from multiprocessing import Pool

from collections import deque
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

import hashlib

sys.path.insert(0, '../')

from database_service.db import GoodDB
from crawler_service.crawler import Crawler

db_uri = '127.0.0.1:27017'

def main():
    start = time.time()

    ## start database service ##
    database = GoodDB('../data/')
    database.startMongo()

    num_cpus = round(os.cpu_count()/2)
    print(f"[+] Using {num_cpus} cpus")
    crawlers = [Crawler(f'C{n}',) for n in range(num_cpus)]
    with Pool(num_cpus) as p:
        p.map(crawl, crawlers)
    client = database.startClient()
    db = client.crawler
    print(f"[+] Added {len([doc for doc in db.crawler.find({})])} entries to the database")
    print("Finished in {} secs.".format(round(time.time()-start, 2)))

def crawl(crawler):
    pid = mp.current_process().pid
    crawler.setPid(pid)
    client,db = crawler.connect_db()
    print(f"{crawler.name}[{crawler.pid}] is crawling ...")
    #todo Implement the Crawler

    save_location = os.getcwd() + '/files/' ## change this as needed
    starting_link = ['https://en.wikipedia.org/wiki/Special:Random'] ## seed
    d = deque(starting_link)

    page_num = 1
    last_num_of_links = len(d)
    st = time.time()
    while(time.time()-st < 10):
        try:
            u = urllib.parse.urlparse(d.popleft())
            if u.geturl() != 'https://en.wikipedia.org/wiki/Special:Random':
                if u.geturl() not in db.crawler.find():
                    #print('Found unique link : {}'.format(db.crawler.find({'url': u.geturl()})))
                    #sys.stdout.write("\033[F")
                    pass
                else:
                    #print([doc for doc in db.crawler.find({'url':u.geturl()})])
                    pass
            else:
                print([doc for doc in db.crawler.find({'url':u.geturl()})])
            with urllib.request.urlopen(u.geturl()) as f:
                page = f.read()
                soup = BeautifulSoup(page, 'html.parser')
                #print('CURRENT LINK: {}'.format(u.geturl()))
                #print('Parsing for links ...')
                start = time.time()
                for link in soup.findAll('a'):
                    l = link.get('href')
                    if l:
                        if l[:2] == '//':
                            new_url = l[2:]
                            if new_url not in d:
                                d.append(new_url)
                        if l[0] == '/':
                            new_url = u.scheme+'://'+u.netloc+l
                            if new_url not in d:
                                d.append(new_url)
                        if l[:8] == 'https://':
                            if l not in d:
                                d.append(l)
                #print('Found {} pages in {} sec(s)'.format(len(d)-last_num_of_links, time.time()-start))
                last_num_of_links = len(d)
                
                start = time.time()
                h = hashlib.md5()
                h.update(u.geturl().encode('utf-8'))
                with open(str(os.path.join(save_location, h.hexdigest()+'.html')), 'w') as nf:
                    nf.write(str(soup.encode('utf-8')))
                    nf.close()
                #print('Cached new page: {}'.format(u.geturl()) + ' in {} sec(s)'.format(time.time()-start))

                ## TODO: Connect to db and write hash and file
                if u.geturl() == 'https://en.wikipedia.org/wiki/Special:Random':
                    pass
                else:
                    db.crawler.insert_one({'crawler_name' : crawler.name, 'crawler_pid': crawler.pid, 'url_hash': h.hexdigest(), 'url': u.geturl(), 'path': save_location+h.hexdigest()+'.html'})
            page_num += 1
        except:
            pass
        

    crawler.disconnect_db(client)
    #print(f"[+] Added {len([doc for doc in db.crawler.find({})])} entries to the database")
    print(f"{crawler.name}[{crawler.pid}] has finished crawling.")
    return True


if __name__ == "__main__":
    main()
