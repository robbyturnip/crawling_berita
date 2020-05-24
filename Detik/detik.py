import re
import sys
import csv
import random
import requests
import threading
from bs4 import BeautifulSoup

sys.setrecursionlimit(1000)

class Detik():

    def __init__(self):
        self.link   =   'https://www.detik.com/search/searchall?query={}'
        self.to_link()

    def file_keyword(self):
        keyword     =   open("keyword.txt", "r")

        return keyword

    def to_link(self):
        list_link       =   []
        list_worker     =   []
        list_keyword    =   [word for word in self.file_keyword()]

        for keyword in list_keyword:
            link        =   self.link.format(keyword)
            list_link.append(link)

        
        for index, link in enumerate(list_link):
            name_file   =   list_keyword[index].split()
            name_file   =   '_'.join(name_file)
            myworker    =   threading.Thread(target=ScraperLink, args=(name_file, link,)) 
            myworker.start()
            list_worker.append(myworker)

        for worker in list_worker:
            worker.join()
    
class ScraperLink():

    def __init__(self, keyword, link, first=True):
        self.link       =   link
        self.keyword    =   keyword
        self.first      =   first
        self.link_add   =   'https://www.detik.com{}'
        self.namefile   =   'detik_{}.csv'.format(self.keyword.lower())
        self.scraper()

    def get_header(self):
        user_agent_list =   [
                                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
                                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
                                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
                                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
                                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
                                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:75.0) Gecko/20100101 Firefox/75.0',
                                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                                'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0',
                                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36',
                                'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.0'
                            ]
        user_agent      =   random.choice(user_agent_list)
        header          =   {
                                'User-Agent': '{}'.format(user_agent),
                                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                                'Accept-Language': 'en-US,en;q=0.5',
                                'Accept-Encoding': 'gzip, deflate',
                                'DNT': '1',
                                'Connection': 'keep-alive',
                                'Upgrade-Insecures-Requests': '1'
                             }

        return header

    def get_content(self, link):
        response       =   requests.get(link, headers=self.get_header())
        soup           =   BeautifulSoup(response.text, 'lxml')

        content        =   soup.find('div',{'class':'detail__body-text'}).text if soup.find('div',{'class':'detail__body-text'}) else ''      
        content        =   soup.find('div', {'id':'detikdetailtext'}).text if not content and soup.find('div', {'id':'detikdetailtext'}) else content         
        content        =   re.sub('Baca juga:.*','', content) if content else content
        content        =   re.sub('Copyright @ 2020 detikcom.*','', content) if content else content
        content        =   re.sub('(DETIK)','', content) if content else content
        content        =   re.sub('\W',' ', content) if content else ''
        content        =   re.sub('\d+',' ', content) if content else ''
        content        =   re.sub('\s{2,}',' ', content) if content else ''

        return content

    def scraper(self):
        next_page   =   ''
        response    =   requests.get(self.link, headers=self.get_header())
        soup        =   BeautifulSoup(response.text, 'lxml')
        list_news   =   soup.find_all('article')

        with open(self.namefile, 'a', newline='') as csvfile:

                fieldnames = ['title','content']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                if self.first:
                    writer.writerow({'title':'title', 'content':'content'})

        for news in list_news:

            title           =   news.select('h2.title')[0].text if  news.select('h2.title') else ''
            link            =   news.select('a')[0]['href'] if  news.select('a') else ''
            link            =   self.link.format(link) if link and 'http' not in link else link
            content         =   self.get_content(link)

            with open(self.namefile, 'a', newline='') as csvfile:

                fieldnames = ['title','content']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                if title and content:
                    writer.writerow({'title':title, 'content':content})


        pagination  =   soup.find('div', {'class':'paging text_center'})
        pagination  =   pagination.find_all('a') if pagination else []

        for page in pagination:
            
            istrue =  'class="last"' in str(page)

            if istrue:
                next_page  =   page['href'] 
            else :
                pass
        
        if next_page:
            ScraperLink(self.keyword, next_page, False)
        else:
            pass


Detik()
