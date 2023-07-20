import requests
import html2text
from flair.data import Sentence
from flair.models import SequenceTagger
from googlesearch import search
from urlib.request import urlopen
from bs4 import BeautifulSoup

#dictionaries containing the rank
rankPER = {}
rankLOC = {}
rankORG = {}

#search and retrieve top 10 sites given query and apply entity extraction
query = input("Enter search query:")

for sites in search(query, tld="co.in", num=2, stop=2, pause=2):

    print(sites)

    #takes care of image urls
    image_formats = ("image/png", "image/jpeg", "image/jpg")
    r = requests.head(sites)
    if r.headers["content-type"] in image_formats:
        print("website is just an image")
        continue

    #takes care of website that cannot be read
    try:
        url = sites
        html = urlopen(url).read()
    except:
        print("website not readable go next")
        continue

    #get text from html
    soup = BeautifulSoup(html, features="html.parser")
    for script in soup(["script", "style"]):
        script.extract()
    text = soup.get_text()

    #break into lines and remove leading and trailing space
    lines = (line.strip() for line in text.splitlines())
    #break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split(" "))
    #remove blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    #remove non ascii characters
    text = text.encode("ascii", "ignore").decode()
    #replace all next line with a space
    text = text.replace('\n', '')


    #convert text from website into a sentence used by FLAIR
    sentence = Sentence(text)

    #load the NER tagger
    tagger = SequenceTagger.load('ner')

    #run NER over the text
    print("gathering entities from this site, will take a moment")
    tagger.predict(sentence)

    #split entity to just the name and insert into corresponding dictionaries
    for entity in sentence.get_spans('ner'):
        if (entity.tag == 'MISC'):
            continue
        result = entity.__str__().split(": ")[1].split(" →")[0]
        if (entity.tag == "PER"):
            if result in rankPER:
                rankPER[result] = rankPER[result] + 1
            else:
                rankPER.update({result:1})
        if (entity.tag == "LOC"):
            if result in rankLOC:
                rankLOC[result] = rankLOC[result] + 1
            else:
                rankLOC.update({result:1})
        if (entity.tag == "ORG"):
            if result in rankORG:
                rankORG[result] = rankORG[result] + 1
            else:
                rankORG.update({result:1})

#find the top 5 persons in dictionary
for x in range(5):
    max = 0
    if (rankPER.__len__() == 0):
        break
    for keys in rankPER:
        if rankPER[keys] > max:
            max = rankPER[keys]
            top = keys
    print("Number", 1 + x, " person is", top)
    rankPER.pop(top)


#find the top 5 locations in dictionary
for x in range(5):
    max = 0
    if (rankLOC.__len__() == 0):
        break
    for keys in rankLOC:
        if rankLOC[keys] > max:
            max = rankLOC[keys]
            top = keys
    print("Number", 1 + x, " location is", top)
    rankLOC.pop(top)

    #find the top 5 locations in dictionary
for x in range(5):
    max = 0
    if (rankORG.__len__() == 0):
        break
    for keys in rankORG:
        if rankORG[keys] > max:
            max = rankORG[keys]
            top = keys
    print("Number", 1 + x, " organization is", top)
    rankORG.pop(top)
            
