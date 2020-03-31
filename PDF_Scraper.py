from io import StringIO
import pickle
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import pprint
import json

filename = "b1.pdf"
output_filename = "output.json"
textoutput = "output.txt"

def extract_text(pdf_file, password='', page_numbers=None, maxpages=0,
                 caching=True, codec='utf-8', laparams=None):
    """Parse and return the text contained in a PDF file.
​
    :param pdf_file: Path to the PDF file to be worked on
    :param password: For encrypted PDFs, the password to decrypt.
    :param page_numbers: List of zero-indexed page numbers to extract.
    :param maxpages: The maximum number of pages to parse
    :param caching: If resources should be cached
    :param codec: Text decoding codec
    :param laparams: An LAParams object from pdfminer.layout. If None, uses
        some default settings that often work well.
    :return: a string containing all of the text extracted.
    """
    if laparams is None:
        laparams = LAParams()
    prev = ""
    pages = []
    with open(pdf_file, "rb") as fp:
        output_string = StringIO()
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string,
                               laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pro = 0
        for page in PDFPage.get_pages(
                fp,
                page_numbers,
                maxpages=maxpages,
                password=password,
                caching=caching,
                check_extractable=True,
        ):
            interpreter.process_page(page)
            current = output_string.getvalue()
            pages.append(current[len(prev):])
            prev = current
            print(pro)
            pro += 1
            
        return pages
        
pages = extract_text(filename)

with open("data.pkl", "wb") as f:
    pickle.dump(pages, f)
print()

def start_with_field(t, f):
    for f1 in f:
        if t.startswith(f1):
            return f1
            
def read_page(s):
    s = s.split("\n")
    program = s[0]
    f = ['Department:', 'Program Contact:',
         'Program Offer Type:', 'Program Offer Stage:',
         'Related Programs:',
         'Program Characteristics:',
         'Executive Summary',
         'Program Summary', 'Performance Measures']

    d = {k: '' for k in f}
    d['id'] = program
    d.pop('Performance Measures')
    
    d['Department:'] = s[6]
    for i in range(11, 16):
        if not s[i].startswith("Program") and len(s[i]) > 0:
            d['Program Contact:'] = s[i]
            break
    d['Program Offer Type:'] = s[7]
    for i in range(9, 16):
        if s[i].startswith("Program Offer Stage: "):
            d['Program Offer Stage:'] = s[i].split(':')[-1]
            break
    d['Related Programs:'] = s[8]
    d['Program Characteristics:'] = s[4].split(':')[-1]

    i = 15
    started = False
    while not started:
        if len(s[i]) < 40:
            i += 1
        else:
            started = True
    
    while len(s[i]) != 0:
        d['Executive Summary'] = d['Executive Summary'] + s[i]
        i += 1
    
    started = False
    while not started:
        if len(s[i]) < 40:
            i += 1
        else:
            started = True

    while len(s[i]) != 0:
        d['Program Summary'] = d['Program Summary'] + s[i]
        i += 1

    return d

with open("data.pkl", "rb") as f:
    pages = pickle.load(f)
pages = [p for p in pages if p.startswith("Program #")]
data = []
for p in pages:
    d = read_page(p)
    data.append(d)

with open(output_filename, "w") as f:
    json.dump(data, f, indent="\t")
