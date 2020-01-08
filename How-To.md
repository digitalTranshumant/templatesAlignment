How To
======

0. Follow README.md and install everything you need.

1. Convert ipynb to Python files:
```bash
jupyter nbconvert --to python nb.ipynb
```
2. Update config.json, remove unneeded pair.

3. Put Wikipedia dumps under: `templatesAlignment/../../dumps/%swiki/latest/` only.

4. Rename dump to reflect dumpdate as `latest` to simplify script run.

5. Run all scripts in order:

`01Download Models.py` need to run with ipython or just download needed models.

6. Unzip .zip files.

7. Download: https://github.com/babylonhealth/fastText_multilingual
And apply patch given at #23 to fix ModuleNotFound error while running script.
