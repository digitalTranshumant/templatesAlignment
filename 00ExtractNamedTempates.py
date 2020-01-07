#!/usr/bin/env python
# coding: utf-8

# ## Retrieve Named Template from Dumps

# In[ ]:


#call parser
import mwxml
import glob
import re
import json
import sys
import pandas as pd
import mwparserfromhell

#config
dumpDate = 'latest'
langs = ['en','ru','id', 'jv', 'bn', 'ml', 'tl', 'sq'] #wiki

templates_RE = re.compile(r'{{(.+?)}}')

def extract_templates(text):
    wikicode = mwparserfromhell.parse(text)
    tmpdict = {}
    for template in wikicode.filter_templates():
        if template.params:
            values = dict([[t.name.strip(),t.value.strip()] for t in template.params if t.showkey])
            if values:
                tmpdict[template.name.strip()] = values
    yield tmpdict

def process_dump(dump, path):
    for page in dump:
        try:
            if int(page.namespace) == 0:  #if int(page.id) in pagesIds:
                    for revision in page: pass #pass all , go to the last revision
                    text =  revision.text
                    templates = list(extract_templates(text))[0] #I apply 'list' for 'expand' the generator object create by yield, for sure there is something better
                    if templates:
                        yield page.id,page.title,templates
        except:
            pass



for lang in langs:
    print(lang)
    paths = glob.glob('../../dumps/%swiki/%s/%swiki-%s-pages-meta-current*.xml*.bz2' % (lang,dumpDate,lang,dumpDate))
    if len(paths) > 1: #remove the single file when have, keep it for small wikis that came all togheter in one file
        paths.remove('../../dumps/%swiki/%s/%swiki-%s-pages-meta-current.xml.bz2' % (lang,dumpDate,lang,dumpDate))
    print(paths,'here')
    f = open('templates-articles_%s.json' % lang,'w')

    for result in mwxml.map(process_dump, paths, threads = 168):
        if result:
            f.write(json.dumps(result))
            f.write('\n')

            #print(result)
    f.close()


# ### Summarize templates

# In[19]:


import json
def summarizeTemplate(lang):
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
    f.close()
    with open('templates-summary_%s.json' % lang,'w') as f:
        json.dump(templates,f)


# In[ ]:


for l in langs:
    print(l)
    summarizeTemplate(l)


# In[ ]:




