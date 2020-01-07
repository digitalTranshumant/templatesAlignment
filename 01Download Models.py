#!/usr/bin/env python
# coding: utf-8

# # Download fasttext models
# 
# * This script download the fasttext pre-trained models in the languages listed in the config.json file.
# * **Note that each model file is around 8G **, and later you will need to unzip those models, using around 15G per model in total (plus the 8G from the zip file that you can delete later)

# In[1]:


get_ipython().system('mkdir vectors')


# In[1]:


import json

with open('config.json') as f:
    lang = json.load(f)['langs']

for l in lang:
    print(l)
    get_ipython().system("wget -P vectors/ {'https://dl.fbaipublicfiles.com/fasttext/vectors-wiki/wiki.%s.zip' % l}")


# In[ ]:




