import requests
import re
from bs4 import BeautifulSoup
import time
# ## ?compare urllib.request to requests?

online_text_url = "https://so.gushiwen.cn/guwen/book_46653FD803893E4F3F8B9229F3CD9433.aspx"
text_contents_html = requests.get(online_text_url).text  # now got a str of the html codes

# write the html codes in a txt file for future reference
# enable the coder to realize what and how to grab necessary information
with open("original_text_html.txt",'w',encoding='utf-8') as wf:
    wf.write(text_contents_html)

soup=BeautifulSoup(text_contents_html,"html.parser")
chapter_regex=re.compile('bookv_')    # we found the target links have this specific pattern
links=soup.find_all('a', href=chapter_regex)

records=[]  
contents={} # a dictionary for urls, in the form of { number(int) : url(string)}
chapter_number=0    # use the numbers rather than chinese characters to name files for the convenience of future call
for link in links[:80]:    # we only want the first 80 chapters, written by Cao, Xueqin. 
    chapter_number+=1
    url=link.get('href')    # return a str
    records.append(f"{chapter_number}: {url}")
    contents[f"{chapter_number}"]=url

with open("original_text_urls.txt",'w',encoding='utf8') as wf:  # we save the urls in a separte file
    wf.write('\n'.join(records))

for title, url in contents.items(): # contents is a dict; title=(int) Ch number, url=(str) url address
    time.sleep(1)   # crawl-delay, for politeness
    with open(f"{title}.txt",'w',encoding='utf-8') as wf:
        contents_html = requests.get(url).text  # now got a str of the html codes
        soup=BeautifulSoup(contents_html,"html.parser")
        contents=soup.find_all('p') # now contents stores all the paragraphs of a chapter
        # we only take [:-2] of contents, as we found there are always two paragraphs of ads that are irrelavant to the text
        # added content.string!=None to avoid some unexpected mistakes
        text=[content.string for content in contents[:-2] if content.string!=None]
        wf.write('\n'.join(text))

