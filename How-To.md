How To
======

0. Follow README.md and install everything you need.

Running using Python
====================
1. Convert ipynb to Python files:
```bash
jupyter nbconvert --to python nb.ipynb
```
2. Update config.json, remove unneeded pair.

3. Put Wikipedia dumps under: `templatesAlignment/../../dumps/%swiki/latest/` only.

4. Rename dump to reflect dumpdate as `latest` to simplify script run.

5. Run all scripts in order.

6. 02alignmentsSpark.py can not be run on local machine at moment.

Notes
=====

1. `01Download Models.py` need to run with ipython or just download needed models.

2. fastText_multilingual is available at: https://github.com/babylonhealth/fastText_multilingual
Apply patch given at #23 to fix ModuleNotFound error while running script.

3. 03ProduceAlignments.py requires https://github.com/facebookresearch/fastText/tree/master/python
instead of version provided by pip.

