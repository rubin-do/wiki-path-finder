import requests
from bs4 import BeautifulSoup, SoupStrainer
from typing import List
from queue import Queue
from urllib.parse import unquote

def parse_urls(page: str) -> List[str]:
    urls = []

    body = BeautifulSoup(page, features='lxml').select('div#bodyContent')[0]

    for url in BeautifulSoup(str(body), features='lxml', parse_only=SoupStrainer('a')):
        if hasattr(url, 'href'):
            link = url.get('href')
            
            if not link or link[0] != '/' or '#' in link or (link[:6] != '/wiki/'):
                continue
            
            if ':' in link:
                link = link[:link.find(':')]

            if '#' in link:
                link = link[:link.find('#')]

            final = 'https://ru.wikipedia.org' + unquote(link)

            if final not in urls:
                urls.append(final)
        
    return urls
    


def get_page(url: str) -> str:
    ans = requests.get(url)

    return ans.content


def process_url(url_start: str, url_dest: str) -> List[str]:
    url_start = unquote(url_start)
    url_dest = unquote(url_dest)


    print(url_start, url_dest)

    visited_from = dict()

    queue = Queue()
    queue.put(url_start)
    
    visited_from[url_start] = ''

    while not queue.empty():
        cur_url = queue.get()

        #print(cur_url)

        urls_cur = parse_urls(
            get_page(cur_url)
        )
        
        if url_dest in urls_cur:
            visited_from[url_dest] = cur_url
            break

        for url in urls_cur:
            if url not in visited_from.keys():
                visited_from[url] = cur_url
                queue.put(url)

    
    path = []
    cur_url = url_dest

    while cur_url != '':
        path.append(cur_url)
        cur_url = visited_from[cur_url]
    
    path.reverse()

    #print(path)

    for i in range(len(path)):
        path[i] = path[i][path[i].find('/wiki/') + 6:]
    
    return path
