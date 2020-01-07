#!/usr/bin/env python
# coding: utf-8

# # Aligning Parameters
# 
# In this notebook we are taking one language (for example Spanish), reading the output from ExtractNamedTempates and:
# 
# * Counting templates frequency
# * Counting parameters frequency
# * Getting the pages where templates occurs
# * Getting a second language (Ex: Catalan), trying to find the equivalent template (using Wikidata)
# * Comparing the paramers and values in those pairs of language

# ## Define basic functions

# In[50]:


get_ipython().magic('matplotlib inline')
from matplotlib import pyplot
import requests
import json
import mwparserfromhell
from scipy.spatial import distance
from collections import Counter

def getWikidataPair(titles,lang,target):
    """
    titles: list of pages titles
    lang:source lang (same of the titles)
    target: target lang
    returns a list: page_title_source,page_title_target
    """
    response= requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&sites=%swiki&titles=%s&props=sitelinks&format=json" % (lang,'|'.join(titles)))
    output = []
    for entity,data in  response.json()['entities'].items():
        if data['sitelinks'].get(target+'wiki'):
            s=data['sitelinks'][lang+'wiki']['title']
            t=data['sitelinks'][target+'wiki']['title']
            output.append([s,t])
    return output

def getWikidataID(titles,lang):
    """
    titles: list of pages titles
    lang:source lang (same of the titles)
    target: target lang
    returns a list: page_title_source,page_title_target
    """
    response= requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&sites=%swiki&titles=%s&props=sitelinks&format=json" % (lang,'|'.join(titles)))
    output = []
    for entity,data in  response.json()['entities'].items():
        if data['sitelinks'].get(target+'wiki'):
            s=data['sitelinks'][lang+'wiki']['title']
            t=data['sitelinks'][target+'wiki']['title']
            output.append([s,t])
    return output


#Get articles
def getContent(title,lang):
    """
    title: page title
    lang: lang
    returns wikitext
    """
    url = "https://%s.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=content&format=json&formatversion=2&titles=%s" % (lang,title)
    response = requests.get(url)
    content = response.json()['query']['pages'][0]['revisions'][0]['content']
    return content

#get all the templates with named parameters
def extract_templates(text):
    wikicode = mwparserfromhell.parse(text)
    tmpdict = {}
    for template in wikicode.filter_templates():
        if template.params:
            values = dict([[t.name.strip(),t.value.strip()] for t in template.params if t.showkey])
            if values:
                tmpdict[template.name.strip()] = values
    return tmpdict

def getTemplateData(template,lang):
    url =  "https://%s.wikipedia.org/w/api.php?action=templatedata&titles=%s&formatversion=2&redirects=1" % (lang,template)
    #print(url)
    resp = requests.get(url)
    data = list(resp.json()['pages'].values())[0]
    return data


def apply_transform(vec, transform):
        """
        Apply the given transformation to the vector space

        Right-multiplies given transform with embeddings E:
            E = E * transform

        Transform can either be a string with a filename to a
        text file containing a ndarray (compat. with np.loadtxt)
        or a numpy ndarray.
        """
        transmat = np.loadtxt(transform) if isinstance(transform, str) else transform
        return np.matmul(vec, transmat)


# ## Aggregating templates coming from ExtractNamedTempates.ipynb
# 
# Note that all templantes name are capitalized and parameters are in low case

# In[2]:


lang = 'es'
f = open('templates-articles_%s.json' % lang)
templates = {}
params = {}
for l in f:
    tmp = json.loads(l)
    page = tmp[1]
    for template,param in tmp[2].items():
        template = template.capitalize()
        templates[template] = templates.get(template,{'Tcount':0,'Tpages':[],'Params':{}})
        templates[template]['Tcount'] += 1
        templates[template]['Tpages'].append(page)
        for name,val in param.items():
            name = name.lower()
            templates[template]['Params'][name] =templates[template]['Params'].get(name,0)
            templates[template]['Params'][name] +=1
            params[name] = params.get(name,0)
            params[name] += 1


# In[3]:


targetLang = 'en'
f = open('templates-articles_%s.json' % targetLang)
templatesTarget = {}
paramsTarget = {}
for l in f:
    tmp = json.loads(l)
    page = tmp[1]
    for template,param in tmp[2].items():
        template = template.capitalize()
        templatesTarget[template] = templatesTarget.get(template,{'Tcount':0,'Tpages':[],'Params':{}})
        templatesTarget[template]['Tcount'] += 1
        templatesTarget[template]['Tpages'].append(page)
        for name,val in param.items():
            name = name.lower()
            templatesTarget[template]['Params'][name] =templatesTarget[template]['Params'].get(name,0)
            templatesTarget[template]['Params'][name] +=1
            paramsTarget[name] = paramsTarget.get(name,0)
            paramsTarget[name] += 1


# ## Getting most frequent templates and parameters

# In[12]:


templateFreq = [(a[0],a[1]['Tcount'],len(a[1]['Params'])) for a in sorted(templates.items(), key =  lambda x:x[1]['Tcount'],reverse=True)]
templateFreq = [(a[0],a[1]['Tcount'],len(a[1]['Params'])) for a in sorted(templates.items(), key =  lambda x:x[1]['Tcount'],reverse=True)]


# In[34]:


templateFreq[0:50]


# In[121]:


### looking for errors or unsual parameters
get_ipython().system('grep --color=always "05.22.2012 acessodata" templates-articles_es.json')


# In[22]:


params['05.22.2012 acessodata']


# In[35]:


sorted(params.items(), key =  lambda x:x[1],reverse=True)[0:20]


# In[24]:


sorted(paramsTarget.items(), key =  lambda x:x[1],reverse=True)[0:20]


# ## Experiments with some (arbitrary) selected templates

# In[36]:


exampleTemplate = 'Ficha de persona'
sourceLang ='es'
targetLang = 'en'
templatesTwoLang = getWikidataPair(['Plantilla:'+exampleTemplate],sourceLang,targetLang)[0]


# In[37]:


import random
random.seed(1)
pagesSource = random.sample(templates[exampleTemplate]["Tpages"],50)
pagesPairs = getWikidataPair(pagesSource,sourceLang,targetLang)
templatesPairsPerPage = {}
for pages in pagesPairs:
    templateSource = [(name,data) for name,data in  extract_templates(getContent(pages[0],sourceLang)).items() if name.lower() in templatesTwoLang[0].lower()] 
    templateTarget = [(name,data) for name,data in  extract_templates(getContent(pages[1],targetLang)).items() if name.lower() in templatesTwoLang[1].lower()] 
    if templateSource:
        if templateTarget:
            templatesPairsPerPage[pages[0]] = templatesPairsPerPage.get(pages[0],[])

            templatesPairsPerPage[pages[0]].append((templateSource,templateTarget))
    
    


# ## TemplateData (metadata) based aligments
# 

# ### Using Josifoski et al alignments [https://arxiv.org/abs/1904.03922]

# In[192]:


import numpy as np
from cr5 import Cr5_Model
from scipy.spatial import distance
from collections import Counter

model = Cr5_Model('./','joint_28') # path_to_pretrained_model, model_prefix
model.load_langs(['en', 'ca','es']) # list_of_languages


# In[57]:


templatesTwoLang


# In[58]:



templateDataLang1 = getTemplateData(templatesTwoLang[0],sourceLang)
templateDataLang2 = getTemplateData(templatesTwoLang[1],targetLang)


# In[59]:


distances = {}
for param1,data1 in templateDataLang1['params'].items():
    try:
        vec1 = model.get_document_embedding(param1.split(),sourceLang)
        distances[param1] = []
        for param2,data2 in templateDataLang2['params'].items():
            if data1['type'] == data2['type']:

                try:
                    vec2 = model.get_document_embedding(param2.split(),targetLang)
                    dist = distance.cosine(vec1,vec2)
                    distances[param1].append([dist,param2])
                except:
                    pass
    except:
        pass
for param,words in distances.items():
    try:
        print(param,sorted(words)[0:3])
    except:
        pass


# In[60]:


distances2= {}
for param1,data1 in templateDataLang1['params'].items():
    try:
        try:
            vec1 = model.get_document_embedding(data1['label'][sourceLang].split(),sourceLang)
        except:
            vec1 = model.get_document_embedding(param1.split(),sourceLang)

        distances2[param1] = []
        for param2,data2 in templateDataLang2['params'].items():
            if data1['type'] == data2['type']:
                try:
                    vec2 = model.get_document_embedding(data2['label'][targetLang].split(),targetLang)
                except:
                    vec2 = model.get_document_embedding(param2.split(),targetLang)
                try:
                    dist = distance.cosine(vec1,vec2)
                    distances2[param1].append([dist,param2])
                except:
                    pass
    except:
        pass
for param,words in distances2.items():
    try:
        print(param,sorted(words)[0:2])
    except:
        pass


# ### Using Wikidata based alignemnts https://github.com/digitalTranshumant/wmf-interlanguage

# In[27]:


## Trying my alignments

import fastText
myModel = fastText.load_model('fastText/wiki.es.bin')
myModel2 = fastText.load_model('fastText/wiki.en.bin')


# In[61]:


distances3 = {}
transmat = np.loadtxt('fastText_multilingual/my_alingments/apply_in_en_to_es.txt')
for param1,data1 in templateDataLang1['params'].items():
        vec1 = myModel.get_sentence_vector(param1)
        distances3[param1] = []
        for param2,data2 in templateDataLang2['params'].items():
          #  if data1['type'] == data2['type']:
                vec2= myModel2.get_sentence_vector(param2)
                vec2T = apply_transform(vec2,transmat)
                dist = distance.cosine(vec1,vec2T)
                distances3[param1].append([dist,param2])

for param,words in distances3.items():
    try:
        if sorted(words)[0][0] < .4:
            print(param,sorted(words)[0:3])
    except:
        pass


# ### Template data limitations
# * Big amount of 'es' templates, have no templatedata info

# In[39]:


withTemplateData = 0
withoutTemplateData = 0
for t in templateFreq[0:50]:
    try:
        tmp = getTemplateData('Plantilla:'+t[0],lang='es')
        print(t[0],'ok')
        withTemplateData +=1
    except:
        print(t[0],'no')
        withoutTemplateData +=1
print(withTemplateData,'ok',withoutTemplateData,'No')


# ### Without Template Data
# This is working pretty good. 
# We need to:
# * Play with the similiarty threshold
# * Map 1 to 1 (keep just the most similar)

# In[62]:


distancesNoTemplateData = {}
print(templatesTwoLang)
template1 = templates[templatesTwoLang[0].split(':')[1]]
template1['params'] = sorted(template1['Params'].items(), key= lambda x: x[1],reverse=True)[:100]
template2 = templatesTarget[templatesTwoLang[1].split(':')[1]]
template2['params'] = sorted(template2['Params'].items(), key= lambda x: x[1],reverse=True)[:200]


transmat = np.loadtxt('fastText_multilingual/my_alingments/apply_in_en_to_es.txt')
for param1,data1 in template1['params']:
    try:
        vec1 = myModel.get_sentence_vector(param1.strip())
        distancesNoTemplateData[param1] = []
    except: pass
    for param2,data2 in template2['params']:
            try:
                vec2= myModel2.get_sentence_vector(param2.strip())
                vec2T = apply_transform(vec2,transmat)
                dist = distance.cosine(vec1,vec2T)
                distancesNoTemplateData[param1].append([dist,param2])
            except:
                pass

cNotFound = 0
for param,words in distancesNoTemplateData.items():
    try:
        if sorted(words)[0][0] < .4:
            print(param,sorted(words)[0:3])
        else:
            cNotFound +=1
    except:
        pass
print(cNotFound,'Without Mapping')


# In[41]:


template1['params']


# In[43]:


#Same before, just trying with other Template
exampleTemplate2 = 'Ficha de deportista'
sourceLang2 ='es'
targetLang2 = 'en'
templatesTwoLang2 = getWikidataPair(['Plantilla:'+exampleTemplate2],sourceLang2,targetLang2)[0]


distancesNoTemplateData = {}
print(templatesTwoLang2)
template1 = templates[templatesTwoLang2[0].split(':')[1]]
template1['params'] = sorted(template1['Params'].items(), key= lambda x: x[1],reverse=True)[:100]
template2 = templatesTarget[templatesTwoLang2[1].split(':')[1]]
template2['params'] = sorted(template2['Params'].items(), key= lambda x: x[1],reverse=True)[:200]

transmat = np.loadtxt('fastText_multilingual/my_alingments/apply_in_en_to_es.txt')
for param1,data1 in template1['params']:
    try:
        vec1 = myModel.get_sentence_vector(param1.strip())
        distancesNoTemplateData[param1] = []
    except: pass
    for param2,data2 in template2['params']:
            try:
                vec2= myModel2.get_sentence_vector(param2.strip())
                vec2T = apply_transform(vec2,transmat)
                dist = distance.cosine(vec1,vec2T)
                distancesNoTemplateData[param1].append([dist,param2])
            except:
                pass

cNotFound = 0
for param,words in distancesNoTemplateData.items():
    try:
        if sorted(words)[0][0] < .4:
            print(param,sorted(words)[0:3])
        else:
            cNotFound +=1
    except:
        pass
print(cNotFound,'Without Mapping')


# ## With Graph approach
# Notes:
# * Play with amount of candidates per language. By now, what works the best is to have few elements in the source lang and a lot in the target

# In[51]:


import networkx as nx
G= nx.Graph()
exampleTemplate2 = 'Ficha de película'
sourceLang2 ='es'
targetLang2 = 'en'
templatesTwoLang2 = getWikidataPair(['Plantilla:'+exampleTemplate2],sourceLang2,targetLang2)[0]


distancesNoTemplateData = {}
print(templatesTwoLang2)
template1 = templates[templatesTwoLang2[0].split(':')[1]]
#template1['params'] = sorted(template1['Params'].items(), key= lambda x: x[1],reverse=True)[:400]
template1['params'] = [x for x in template1['Params'].items() if x[1]/len(template1['Params']) > .05] #appears at least X% of times
template2 = templatesTarget[templatesTwoLang2[1].split(':')[1]]
#template2['params'] = sorted(template2['Params'].items(), key= lambda x: x[1],reverse=True)[:400]
template2['params'] = [x for x in template2['Params'].items() if x[1]/len(template2['Params']) > .05] #appears at least 1X of times


transmat = np.loadtxt('fastText_multilingual/my_alingments/apply_in_en_to_es.txt')
for param1,data1 in template1['params']:
    try:
        vec1 = myModel.get_sentence_vector(param1.strip().replace('_',' '))
        distancesNoTemplateData[param1] = []
    except: pass
    for param2,data2 in template2['params']:
            try:
                vec2= myModel2.get_sentence_vector(param2.strip().replace('_',' '))
                vec2T = apply_transform(vec2,transmat)
                dist = distance.cosine(vec1,vec2T)
                distancesNoTemplateData[param1].append([dist,param2])
                if dist < .45:
                    node1= '%s_%s' % (sourceLang2,param1)
                    node2= '%s_%s' % (targetLang2,param2)

                    G.add_edge(node1,node2)
                    G[node1][node2]['w'] = dist
            except:
                pass



# In[52]:


get_ipython().magic('matplotlib inline')

nx.draw(G,with_labels=True)


# In[53]:


c = 0
while G.edges():
    p = sorted(G.edges(data=True), key=lambda x: x[2]['w'])[0]
    psorted = sorted(list(p[:2]))
    print(psorted[0][3:],'->',psorted[1][3:])
    G.remove_node(p[0])
    G.remove_node(p[1])
    c+=1
print(c/len(template1['params']))


# #### Download top 100 templates in 'es' to 'en

# In[63]:


import networkx as nx
G= nx.Graph()
output = {}
transmat = np.loadtxt('fastText_multilingual/my_alingments/apply_in_en_to_es.txt')

for exampleTemplate2 in  templateFreq[0:50]:
    try:
        exampleTemplate2 = exampleTemplate2[0]
        sourceLang2 ='es'
        targetLang2 = 'en'
        templatesTwoLang2 = getWikidataPair(['Plantilla:'+exampleTemplate2],sourceLang2,targetLang2)[0]


        distancesNoTemplateData = {}
        print(templatesTwoLang2)
        template1 = templates[templatesTwoLang2[0].split(':')[1]]
        #template1['params'] = sorted(template1['Params'].items(), key= lambda x: x[1],reverse=True)[:400]
        template1['params'] = [x for x in template1['Params'].items() if x[1]/len(template1['Params']) > .3] #appears at least X% of times
        template2 = templatesTarget[templatesTwoLang2[1].split(':')[1]]
        #template2['params'] = sorted(template2['Params'].items(), key= lambda x: x[1],reverse=True)[:400]
        template2['params'] = [x for x in template2['Params'].items() if x[1]/len(template2['Params']) > .05] #appears at least 1X of times


        for param1,data1 in template1['params']:
            try:
                vec1 = myModel.get_sentence_vector(param1.strip().replace('_',' '))
                distancesNoTemplateData[param1] = []
            except: pass
            for param2,data2 in template2['params']:
                    try:
                        vec2= myModel2.get_sentence_vector(param2.strip().replace('_',' '))
                        vec2T = apply_transform(vec2,transmat)
                        dist = distance.cosine(vec1,vec2T)
                        distancesNoTemplateData[param1].append([dist,param2])
                        if dist < .45:
                            node1= '%s_%s' % (sourceLang2,param1)
                            node2= '%s_%s' % (targetLang2,param2)
                            G.add_edge(node1,node2)
                            G[node1][node2]['w'] = dist
                    except:
                        pass    
        output[exampleTemplate2] = []
        print(exampleTemplate2,'======================')
        while G.edges():
            p = sorted(G.edges(data=True), key=lambda x: x[2]['w'])[0]
            psorted = sorted(list(p[:2]))       
            
            output[exampleTemplate2].append({psorted[0][:2]:psorted[0][3:],
                                            psorted[1][:2]:psorted[1][3:],
                                            'd':p[2]['w']})
            G.remove_node(p[0])
            G.remove_node(p[1])

    except:
        pass


# In[64]:


with open('templatesEsEN-top100.json','w') as o:
    json.dump(output,o)


# ## Value based - In progress

# In[551]:


import networkx as nx
G= nx.Graph()
exampleTemplate2 = 'Ficha de persona'
sourceLang2 ='es'
targetLang2 = 'en'
templatesTwoLang2 = getWikidataPair(['Plantilla:'+exampleTemplate2],sourceLang2,targetLang2)[0]

import random
random.seed(1)
pagesSource = random.sample(templates[exampleTemplate2]["Tpages"],50)
pagesPairs = getWikidataPair(pagesSource,sourceLang,targetLang)
templatesPairsPerPage = {}
for pages in pagesPairs:
    templateSource = [(name,data) for name,data in  extract_templates(getContent(pages[0],sourceLang)).items() if name.lower() in templatesTwoLang[0].lower()] 
    templateTarget = [(name,data) for name,data in  extract_templates(getContent(pages[1],targetLang)).items() if name.lower() in templatesTwoLang[1].lower()] 
    if templateSource:
        if templateTarget:
            templatesPairsPerPage[pages[0]] = templatesPairsPerPage.get(pages[0],[])

            templatesPairsPerPage[pages[0]].append((templateSource,templateTarget))
            
            


transmat = np.loadtxt('fastText_multilingual/my_alingments/apply_in_en_to_es.txt')

for pages, data in templatesPairsPerPage.items():
    pageSourceLang = data[0][0][0][1]
    pageTargetLang = data[0][1][0][1]
    for param1,value in pageSourceLang.items():
        try:
            vec1 = myModel.get_sentence_vector(value.strip())
            distancesNoTemplateData[param1] = []
            for param2,value2 in pageTargetLang.items():
                    vec2= myModel2.get_sentence_vector(value2.strip())
                    vec2T = apply_transform(vec2,transmat)
                    dist = distance.cosine(vec1,vec2T)
                    distancesNoTemplateData[param1].append([dist,param2])
        except:
            pass


# In[556]:


cNotFound = 0
for param,words in distancesNoTemplateData.items():
    try:
        if sorted(words)[0][0] < .9:
            print(param,sorted(words)[0:3])
        else:
            cNotFound +=1
    except:
        pass


# In[ ]:




