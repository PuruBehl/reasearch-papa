# -*- coding: utf-8 -*-
"""Research papa python script.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/10XNIheBWCrTOKn257LA-IbJB5dVHBJRo
"""

from operator import itemgetter
import fitz
import json
import hashlib


def fonts(doc, granularity=False):
    """Extracts fonts and their usage in PDF documents.
    :param doc: PDF document to iterate through
    :type doc: <class 'fitz.fitz.Document'>
    :param granularity: also use 'font', 'flags' and 'color' to discriminate text
    :type granularity: bool
    :rtype: [(font_size, count), (font_size, count}], dict
    :return: most used fonts sorted by count, font style information
    """
    styles = {}
    font_counts = {}

    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            if b['type'] == 0:  # block contains text
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        if granularity:
                            identifier = "{0}_{1}_{2}_{3}".format(s['size'], s['flags'], s['font'], s['color'])
                            styles[identifier] = {'size': s['size'], 'flags': s['flags'], 'font': s['font'],
                                                  'color': s['color']}
                        else:
                            identifier = "{0}".format(s['size'])
                            styles[identifier] = {'size': s['size'], 'font': s['font']}

                        font_counts[identifier] = font_counts.get(identifier, 0) + 1  # count the fonts usage

    font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)

    if len(font_counts) < 1:
        raise ValueError("Zero discriminating fonts found!")

    return font_counts, styles


def font_tags(font_counts, styles):
    """Returns dictionary with font sizes as keys and tags as value.
    :param font_counts: (font_size, count) for all fonts occuring in document
    :type font_counts: list
    :param styles: all styles found in the document
    :type styles: dict
    :rtype: dict
    :return: all element tags based on font-sizes
    """
    p_style = styles[font_counts[0][0]]  # get style for most used font by count (paragraph)
    p_size = p_style['size']  # get the paragraph's size

    # sorting the font sizes high to low, so that we can append the right integer to each tag
    font_sizes = []
    for (font_size, count) in font_counts:
        font_sizes.append(float(font_size))
    font_sizes.sort(reverse=True)

    # aggregating the tags for each font size
    idx = 0
    size_tag = {}
    for size in font_sizes:
        idx += 1
        if size == p_size:
            idx = 0
            size_tag[size] = '<p>'
        if size > p_size:
            size_tag[size] = '<h{0}>'.format(idx)
        elif size < p_size:
            size_tag[size] = '<s{0}>'.format(idx)

    return size_tag


def headers_para(doc, size_tag):
    """Scrapes headers & paragraphs from PDF and return texts with element tags.
    :param doc: PDF document to iterate through
    :type doc: <class 'fitz.fitz.Document'>
    :param size_tag: textual element tags for each size
    :type size_tag: dict
    :rtype: list
    :return: texts with pre-prended element tags
    """
    header_para = []  # list with headers and paragraphs
    first = True  # boolean operator for first header
    previous_s = {}  # previous span

    for page in doc:
        blocks = page.getText("dict")["blocks"]
        for b in blocks:  # iterate through the text blocks
            if b['type'] == 0:  # this block contains text

                # REMEMBER: multiple fonts and sizes are possible IN one block

                block_string = ""  # text found in block
                for l in b["lines"]:  # iterate through the text lines
                    for s in l["spans"]:  # iterate through the text spans
                        if s['text'].strip():  # removing whitespaces:
                            if first:
                                previous_s = s
                                first = False
                                block_string = size_tag[s['size']] + s['text']
                            else:
                                if s['size'] == previous_s['size']:

                                    if block_string and all((c == "|") for c in block_string):
                                        # block_string only contains pipes
                                        block_string = size_tag[s['size']] + s['text']
                                    if block_string == "":
                                        # new block has started, so append size tag
                                        block_string = size_tag[s['size']] + s['text']
                                    else:  # in the same block, so concatenate strings
                                        block_string += " " + s['text']

                                else:
                                    header_para.append(block_string)
                                    block_string = size_tag[s['size']] + s['text']

                                previous_s = s

                    # new block started, indicating with a pipe
                    block_string += "|"

                header_para.append(block_string)

    return header_para

def return_headings(path) :
    doc = fitz.open(path)
    font_counts, styles = fonts(doc, granularity=False)

    size_tag = font_tags(font_counts, styles)

    elements = headers_para(doc, size_tag)
    headings = [i for i in elements if "<h" in i]
    real_headings = []
    accepted_headings = ["h1","h2","h3","h4"]
    for i in headings :
        for j in accepted_headings :
            if "<"+j in i :
                real_headings.append(i)
    for i in range(len(real_headings)):
        real_headings[i] = real_headings[i].replace("<h1>","")
        real_headings[i] = real_headings[i].replace("<h2>","")

        real_headings[i] = real_headings[i].replace("<h3>","")

        real_headings[i] = real_headings[i].replace("<h4>","")

        real_headings[i] = real_headings[i].replace("|","")

        real_headings[i] = real_headings[i].replace("  ","")
            
    real_headings2 = []
    for i in real_headings :
        count = 0
        while not i[count].isalpha() and count<len(i)-1:
            count+=1
        real_headings2.append(i[count:])
        
    return real_headings2,headings

def return_text(path) :
    doc = fitz.open(path)
    text = ""
    for page in doc :
        text+=page.get_text()
    return text

def to_hash(text):
  hashed_string = hashlib.sha256(text.encode('utf-8')).hexdigest()
  return hashed_string

def text_segmentation(path,heading):
    text = ""
    doc = fitz.open(path)
    font_counts, styles = fonts(doc, granularity=False)

    size_tag = font_tags(font_counts, styles)

    elements = headers_para(doc, size_tag)
    check = False
    for i in range(len(elements)) :
        if heading == elements[i] :
            check=True
        elif "<h" in elements[i]:
            check = False
        if check==True :
            text += elements[i]
    text = text.replace("|","\n")
    return text

def return_segmented_text(path,with_text=False) :
    doc = fitz.open(path)
    font_counts, styles = fonts(doc, granularity=False)

    size_tag = font_tags(font_counts, styles)

    elements = headers_para(doc, size_tag)
    
    # if with_text :
    #     dic = {}
    #     text = ""
    #     head=""
    #     for i in elements :
    #         k=[]
    #         if "<h1" in i or "<h2" in i or "<h3" in i or "<h4" in i :
    #             s=i
    #             s=s.replace("<h1>","")
    #             s=s.replace("<h2>","")
    #             s=s.replace("<h3>","")
    #             s=s.replace("<h4>","")
    #             s=s.replace("|","")
    #             s=s.replace("  ","")
    #             dic[head]=text
    #             text=""
    #             head=s
                
    #         else :
    #             text+=i
    #     return dic
    if with_text :
        dic = {}
        text = ""
        k=[]
        for i in elements :
            if "<h1" in i or "<h2" in i or "<h3" in i or "<h4" in i :
                s=i
                s=s.replace("<h1>","")
                s=s.replace("<h2>","")
                s=s.replace("<h3>","")
                s=s.replace("<h4>","")
                s=s.replace("|","")
                s=s.replace("  ","")
                k.append(s)
                if len(k)==1 :
                    pass
                else:
                    dic[k[-2]]=text
                    text=""
                
                
            else :
                text+=i
        dic[k[-1]]=text
        return dic
    else:
        headings = [i for i in elements if "<h" in i]
        real_headings = []
        accepted_headings = ["h1","h2","h3","h4"]
        for i in headings :
            for j in accepted_headings :
                if "<"+j in i :
                    real_headings.append(i)
        for i in range(len(real_headings)):
            real_headings[i] = real_headings[i].replace("<h1>","")
            real_headings[i] = real_headings[i].replace("<h2>","")

            real_headings[i] = real_headings[i].replace("<h3>","")

            real_headings[i] = real_headings[i].replace("<h4>","")

            real_headings[i] = real_headings[i].replace("|","")

            real_headings[i] = real_headings[i].replace("  ","")

        real_headings2 = []
        for i in real_headings :
            count = 0
            while not i[count].isalpha() and count<len(i)-1:
                count+=1
            real_headings2.append(i[count:])

        return real_headings2,headings










