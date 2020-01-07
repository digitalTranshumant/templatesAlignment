#!/usr/bin/env python
# coding: utf-8

# # Alignments 
# Based on the results "Align Experiments.ipynb" 

# In[19]:


#Load dependencies
import networkx as nx
import json
import numpy as np
import fastText
from scipy.spatial import distance



#Define supported languages 
#langs = ['es','en']#,'ru'] #,'ca']
with open('config.json') as f:
    langs = json.load(f)['langs']

#Load models & transformations 
models = {}
transmat = {}
for lang in langs:
    print(lang)
    transmat[lang] = {}
    for lang2 in langs:
        if lang!=lang2:
            transmat[lang][lang2] = np.loadtxt('my_alingments/apply_in_%s_to_%s.txt' % (lang2,lang))



# In[20]:


get_ipython().magic('matplotlib inline')
from matplotlib import pyplot
import requests
import json
import mwparserfromhell
from time import sleep


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
        
def getWikidataPair(titles,lang,target):
    """
    titles: list of pages titles
    lang:source lang (same of the titles)
    target: target lang
    returns a list: page_title_source,page_title_target
    """
    wikidataInfo =  []
    for tchunks in chunks(titles,50): #requests can have max 50 titles
        response= requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&sites=%swiki&titles=%s&props=sitelinks&format=json" % (lang,'|'.join(tchunks)))
        try:
            result = list(response.json()['entities'].items())
            if result:
                wikidataInfo.extend(result)
        except:
            pass
        sleep(0.5)
    output = []
    for entity,data in  wikidataInfo:
        if 'sitelinks' in data:
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
    results = response.json()['entities'].items()
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
    
def getWikidataPairMultiLangs(titles,lang,targets):
    """
    titles: list of pages titles
    lang:source lang (same of the titles)
    target: liist, target langs
    returns a list: page_title_source,page_title_target
    """
    wikidataInfo =  []
    c = 0
    print('Loading templates names in %s' % lang)
    for tchunks in chunks(titles,50): #requests can have max 50 titles
        c+=len(tchunks)
        print(int(100*c/len(titles)),'%', end=' - ')
        response= requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&sites=%swiki&titles=%s&props=sitelinks&format=json" % (lang,'|'.join(tchunks)))
        try:
            result = list(response.json()['entities'].items())
            if result:
                wikidataInfo.extend(result)
        except:
            pass
        sleep(0.5)
    output = []
    for entity,data in  wikidataInfo:
        outlangs = {}
        if 'sitelinks' in data:
            for target in targets:
                if data['sitelinks'].get(target+'wiki'):
                    s=data['sitelinks'][lang+'wiki']['title']
                    t=data['sitelinks'][target+'wiki']['title']
                    outlangs[target]  = t
            output.append([s,outlangs])
    return output


# In[7]:


#Get templates prefix (exs: Template:, Plantilla:)
#I use cite Web, because it exists in all the targeted languages
prefixes = {}
for lang in langs:
    pairsTemplate = getWikidataPair(['Template:Cite web'],'en',lang)
    prefixes[lang] = pairsTemplate[0][1].split(':')[0]


# In[8]:


def alignSets(set1,set2,sourceLang,targetLang):
    """
    Given two sets of words/sentences in two languages
    return the possible alignments between sentences
    set1: dict or list, ['hola','perro']
    set2: dict or list, ['hello','dog']
    sourceLang: str, 'es'
    targetLang: str, 'en'
    return list
    """
    global models
    global transmat
    output = []
    G= nx.Graph()
    for s1 in set1:
        vec1 = models[sourceLang].get_sentence_vector(s1.strip().replace('_',' '))
        for s2 in set2:
                    vec2= models[targetLang].get_sentence_vector(s2.strip().replace('_',' '))
                    vec2T = apply_transform(vec2,transmat[sourceLang][targetLang])
                    dist = distance.cosine(vec1,vec2T)
                    if dist < .45:
                        node1= '%s_%s' % (sourceLang,s1)
                        node2= '%s_%s' % (targetLang,s2)
                        G.add_edge(node1,node2)
                        G[node1][node2]['w'] = dist

                
    while G.edges():
            p = sorted(G.edges(data=True), key=lambda x: x[2]['w'])[0]
            psorted = sorted(list(p[:2]))
            output.append({psorted[0][:2]:psorted[0][3:],psorted[1][:2]:psorted[1][3:],'d':p[2]['w']})
            #print(psorted[0][3:],'->',psorted[1][3:])

            G.remove_node(p[0])
            G.remove_node(p[1])
    return output


# In[42]:


for lang1 in langs:
    print(lang1)
    with open('templates-summary_%s.json' % lang1) as f:
        templates1 = json.load(f)
    templates1Popular = dict([ (name,data)for name,data in templates1.items() if data['Tcount'] >50 ])
    pairs = getWikidataPairMultiLangs(['%s:%s' % (prefixes[lang1],templateName) for  templateName in templates1Popular.keys()],lang1,langs) 
    models = {}
    models[lang1] = fastText.load_model('vectors/wiki.%s.bin' % lang1)  
    print()
    for lang2 in langs:
        output = {}
        if lang1 != lang2:
            print('== %s' % lang2)
            models[lang2] = fastText.load_model('vectors/wiki.%s.bin' % lang2)  
            with open('templates-summary_%s.json' % lang2) as f:
                templates2 = json.load(f)
            for t1,t2 in pairs:
                if lang2 in t2:
                    t2 = t2[lang2]
                    try:
                        template1 = templates1[t1.split(':')[1]]
                        template2 = templates2[t2.split(':')[1]]
                        template1['params'] = [x[0] for x in template1['Params'].items() if x[1]/len(template1['Params']) > .3] #appears at least X% of times
                        template2['params'] = [x[0] for x in template2['Params'].items() if x[1]/len(template2['Params']) > .05] #appears at least 1X of times
                        alignments = alignSets(template1['params'],template2['params'],lang1,lang2)
                        output[t1] = alignments
                    except: 
                        pass
            with open('templatesAligned/templatesAligned_from_%s_to_%s.json' % (lang1,lang2),'w') as f:
                json.dump(output,f)
            del(models[lang2]) #free memory
    del(models)#free memory


# In[ ]:




