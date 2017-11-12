'''
Created on Oct 31, 2017

@author: chiragm
'''
from io import StringIO
from os import path
import sys
from  urllib.parse import urljoin
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import RegexpTokenizer
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser
from requests import get
import urllib3


def countTravelWords(pdf):
    tokenizer = RegexpTokenizer(r'\w+')
    count = 0
    password = ""
    fp = open(pdf, "rb")
    sio = StringIO()
    parser = PDFParser(fp)
    document = PDFDocument(parser, password)
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    
    for page in PDFPage.create_pages(document):
        
        interpreter.process_page(page)
        layout = device.get_result()
        for lt_obj in layout:
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                tokens = tokenizer.tokenize(lt_obj.get_text())
                words = [word.lower() for word in tokens]
                fdist = nltk.FreqDist(words)
                count+= fdist['travel']
    fp.close()
    return count
    
 
#connect to a URL
url = 'http://ir.expediainc.com/annuals.cfm'
base_dir = sys.argv[1]
http = urllib3.PoolManager()
response = http.request('GET', url)
pdf_list = set()
# 
soup = BeautifulSoup(response.data, "html.parser")
for a in soup.findAll('a'):
    if a['href'].endswith('.pdf'):
        pdf_list.add(a['href'])

pdf_file_names = []
for pdfkey in pdf_list:
    words = pdfkey.split('&')
    pdfname = words[len(words)-1].split('=')[1]
    content = get(urljoin(url, pdfkey))
    pdf_file_names.append(pdfname)
    with open(path.join(base_dir, pdfname), 'wb') as pdf:
        pdf.write(content.content)

for pdfn in sorted(pdf_file_names):
    print('travel word count in %s is :'%(pdfn))
    cnt = countTravelWords(path.join(base_dir, pdfn))
    print(cnt)


