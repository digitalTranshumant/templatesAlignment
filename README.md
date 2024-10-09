# Aligning named templates on Wikipedia

One challenge for the [Content Translation](https://en.wikipedia.org/wiki/Wikipedia:Content_translation_tool) tool is translate [mediwiki templates](https://www.mediawiki.org/wiki/Help:Templates). While finding the template in target language can be done through Wikidata, finding the mapping between template parameters is not trivial. 

Here we aim to solve this problem by using [multilingual fasttext vectors](https://github.com/Babylonpartners/fastText_multilingual).

This repository contains:

* [The Align Experiments notebook](Align&#32;Experiments.ipynb) shows the results for different strategies to produce such aligments.
* A pipeline of 4 files (from 00 to 03) to produce your own alignments.
* A [list of template paramters alignments](https://github.com/digitalTranshumant/templatesAlignment/tree/master/templatesAligned) between this languages: ["es", "en", "fr", "ar", "ru", "uk", "pt", "vi", "zh", "ru", "he", "it", "ta", "id", "fa", "ca"]

## Installation 

### Setup the enviroment 
* Clone this repository
```bash
git clone https://github.com/digitalTranshumant/templatesAlignment.git
```
* Install python3 requirements 
```bash
 pip install -r requirements.txt
 ```
* Download the [Wikipedia Dumps](https://dumps.wikimedia.org) for all the languages that you want to align.
* Write the languages codes that you want to use in [config.json](config.json) file ex: {"langs": ["es", "en", "fr", "ar", "ru", "uk", "pt", "vi", "zh", "ru", "he", "it", "ta", "id", "fa", "ca"]}


### Run the python scripts
* [00ExtractNamedTempates.ipynb](00ExtractNamedTempates.ipynb): Run this notebook to extract all templates from dumps. This process can be slow, for example, in a machine with 8 cores, and 64Gb of Ram, it takes around 24 hours (in total) for the 18 languages listed before.
* [01Download.ipynb](01Download&#32;Models.ipynb): This scripts download the pre-trained fasttext models. Each model unziped would use around 15Gb of hard drivee.
* [02alignmentsSpark.ipynb](02alignmentsSpark.ipynb): This script create the alignment matrices for each language pair. The script is create to work in a Spark cluster, but you can modified for using in normal python, replacing the parquet data by a SQL dump from  [this public table](https://www.mediawiki.org/wiki/Wikibase/Schema/wb_items_per_site).
* [03ProduceAlignments.ipynb](03ProduceAlignments.ipynb): This script creates the alignments. It can take around 10 hours to run.

## TODOs

### Remove hardcoded parameters

The script [ProduceAlignments Notebook](03ProduceAlignments.ipynb) have few hard coded parameters that should be moved to the config file and adjusted more properly:
* Currently we are considering templates that appears at least 50 times in each edition. That number is arbitrary. Increasing the number will result in less templates to be consider. USing that number very low, would include nois (typos) and make the process too slow.
```python
templates1Popular = dict([ (name,data)for name,data in templates1.items() if data['Tcount'] >50 ])
```
* The number of parameters considered is also hardcoded, now we are considering paramters that appears at least the 30%  that the template is used. The tradeoff of moving this number is similar with the previous case:
```python
template1['params'] = [x[0] for x in template1['Params'].items() if x[1]/len(template1['Params']) > .3] #appears at least X% of times
```
* The minimum similarity accepted to validate an alignment  is also arbitrarily defined at .45
```python
 if dist < .45:
 ```

To learn to correct value for all this parameters we need some ground-truth that is currently missing. 
