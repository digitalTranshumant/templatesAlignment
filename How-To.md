How To
======

0. Follow README.md and install everything you need.

1. Convert ipynb to Python files:
```bash
jupyter nbconvert --to python nb.ipynb
```
2. Update config.json, remove unneeded pair.

3. Put Wikipedia dumps under: `current directory/../../dumps/%swiki/latest/` only.

4. Rename dump date to reflect date as `latest` to simplify.

5. Run all scripts in order:

`01Download Models.py` need to run with ipython or just wget needed models
manually.

6. We also need https://github.com/babylonhealth/fastText_multilingual, See
issue #23 there for installation error.
