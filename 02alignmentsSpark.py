#!/usr/bin/env python
# coding: utf-8

# # Compute alignments using Wikidata
# 
# This notebook create alignment matrices to be applied for align two different word embeddings.
# The matrices are created using [this approach](https://github.com/Babylonpartners/fastText_multilingual/blob/master/align_your_own.ipynb), but instead of using bilingual dictionaries we use the Wikidata labels.
# Here we use a parquet dump clo

import numpy as np
import os
from pyspark.sql.functions import regexp_replace
from fastText_multilingual.fasttext import FastVector

# from https://stackoverflow.com/questions/21030391/how-to-normalize-array-numpy
def normalized(a, axis=-1, order=2):
    """Utility function to normalize the rows of a numpy array."""
    l2 = np.atleast_1d(np.linalg.norm(a, order, axis))
    l2[l2==0] = 1
    return a / np.expand_dims(l2, axis)

def make_training_matrices(source_dictionary, target_dictionary, bilingual_dictionary):
    """
    Source and target dictionaries are the FastVector objects of
    source/target languages. bilingual_dictionary is a list of 
    translation pair tuples [(source_word, target_word), ...].
    """
    source_matrix = []
    target_matrix = []

    for (source, target) in bilingual_dictionary:
        try:
            source = source.lower().split()
            sourceVector = np.zeros(300) + sum([source_dictionary[word] for word in source  if word in source_dictionary])/len(source)
            target = target.lower().split()
            targetVector = np.zeros(300) + sum([target_dictionary[word] for word in target  if word in target_dictionary])/len(target)
            if (sourceVector.all() !=0) and (targetVector.all() != 0):
                    source_matrix.append(sourceVector)
                    target_matrix.append(targetVector)
        except:
            pass
    # return training matrices
    return np.array(source_matrix), np.array(target_matrix)

def learn_transformation(source_matrix, target_matrix, normalize_vectors=True):
    """
    Source and target matrices are numpy arrays, shape
    (dictionary_length, embedding_dimension). These contain paired
    word vectors from the bilingual dictionary.
    """
    # optionally normalize the training vectors
    if normalize_vectors:
        source_matrix = normalized(source_matrix)
        target_matrix = normalized(target_matrix)

    # perform the SVD
    product = np.matmul(source_matrix.transpose(), target_matrix)
    U, s, V = np.linalg.svd(product)

    # return orthogonal transformation which aligns source language to the target
    return np.matmul(U, V)

## Prepare folder
outputFolder = 'my_alingments'
if not os.path.exists(outputFolder):
    os.makedirs(outputFolder)

# In[2]:

# get wikidata data

#df = spark.read.parquet('/user/joal/wmf/data/wmf/wikidata/item_page_link/20190204')
#df = df[df['page_namespace'] == 0]
#df = df.withColumn('page', regexp_replace('page_title', '_', ' '))
#df = df.select('wiki_db','item_id','page')

# Use local data
import pandas
df = pandas.read_csv('WikidataItems.csv', error_bad_lines=False, sep=',')

# In[3]:

import glob,os
vectors = sorted(glob.glob('vectors/wiki.*.vec'), key=os.path.getsize) #sorted by size to load the largest files just once
lang2 = ''
while vectors:   
    lang1 = vectors.pop()
    lang1_code = lang1.split('.')[1]
    print(lang1_code)
    if lang1 == lang2:
        lang1_dictionary = lang2_dictionary
    else:
        lang1_dictionary = FastVector(vector_file=lang1)
    for lang2 in vectors:
        lang2_dictionary = FastVector(vector_file=lang2)
        lang2_code = lang2.split('.')[1]
        print('==',lang2_code)
        df2 = df[df.wiki_db == '%swiki' % lang1_code].join(df[df.wiki_db == '%swiki' % lang2_code].withColumnRenamed("page", "page2").withColumnRenamed('wiki_db','wiki_db2'),on='item_id')
        pairs = df2.toPandas()       
        bilingual_dictionary = list(zip(pairs['page'],pairs['page2']))
        ##common words
        #lang1_words = set(lang1_dictionary.word2id.keys()lang1_dictionary.word2id.keys())
        #lang2_words = set(lang2_dictionary.word2id.keys())
        #overlap = list(lang1_words & lang2_words)
        #bilingual_dictionary.extend([(entry, entry) for entry in overlap])
        # form the training matrices
        source_matrix, target_matrix = make_training_matrices(lang1_dictionary, lang2_dictionary, bilingual_dictionary)
        # learn and apply the transformation
        transform = learn_transformation(source_matrix, target_matrix)
        with open('%s/apply_in_%s_to_%s.txt' % (outputFolder,lang1_code,lang2_code),'w') as f:
            np.savetxt(f, transform)
        bilingual_dictionary = [(y,x) for x,y in bilingual_dictionary] #reverse pairs
        # form the training matrices
        source_matrix, target_matrix = make_training_matrices(lang2_dictionary, lang1_dictionary, bilingual_dictionary)
        # learn and apply the transformation
        transform = learn_transformation(source_matrix, target_matrix)
        with open('%s/apply_in_%s_to_%s.txt' % (outputFolder,lang2_code,lang1_code),'w') as f:
            np.savetxt(f, transform)
