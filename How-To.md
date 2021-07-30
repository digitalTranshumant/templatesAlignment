How To
======

0. Follow README.md and install everything you need.

Initial setup
-------------
Login to stat1007:

```$ ssh stat1007```

Setup proxy
-----------
```
$ export https_proxy=https://webproxy.eqiad.wmnet:8080

$ export http_proxy=http://webproxy.eqiad.wmnet:8080
```

Create virtualenv
-----------------
<code>$  virtualenv --python=/usr/bin/python3 python3</code>

Active the virtual environment by:

```$ source python3/bin/activate```

Now, install jupyter notebook:

```$ pip install jupyter```

Next, add the following lines to your .profile file:

```bash
export PYSPARK_DRIVER_PYTHON=jupyter
export PYSPARK_DRIVER_PYTHON_OPTS='notebook'
export PYSPARK_PYTHON=/usr/bin/python3.7
export PYSPARK_PYTHON=/srv/home/USER/python3/bin/python
```

You can additionally add these two lines to make your life easier:

```bash
alias venvspark="source python3/bin/activate; source ~/.profile"
alias startspark="pyspark2 --master yarn --deploy-mode client --executor-memory 8g --driver-memory 8g --conf spark.dynamicAllocation.maxExecutors=128"
```
You can adjust memory as per need.

Close the session, and you will have everything configured.

Starting notebook
-----------------
Make sure to check Kerberos authentication timeout first. Default is set to 48 hours now.

```$ klist```

Extend it by running kinit:

```$ kinit```

Now, you can login again and you will just need to do this:

```$ venvspark```

```$ startspark```

Press ESC,

And check in which port the jupyter notebook is running (usually you should have 8888 or 8889), in this example is 8889

```http://localhost:8889```

Then, in your local machine, create a tunnel by running:

```$ ssh -N stat1007 -L 8889:127.0.0.1:8889```

And then using your browser you will see the normal notebook in:

```http://localhost:8889```

Running scripts
---------------
1. Run all notebooks in order.

2. 00ExtractNamedTempates.ipynb overwrites existing output if runs again, so it is better to save products json files somewhere to save time.

Notes
-----
1. 02alignmentsSpark.py can not be run on local machine.

2. If running locally, `01Download Models.py` need to run with ipython or just download needed models.

3. fastText_multilingual module is available at: https://github.com/babylonhealth/fastText_multilingual

Apply patch given at #23 to fix ModuleNotFound error while running script.

4. `03ProduceAlignments.py` requires https://github.com/facebookresearch/fastText/tree/master/python instead of version provided by pip.

Also see
--------
* Issues related to Kerberos access: https://wikitech.wikimedia.org/wiki/SWAP#Access_and_infrastructure

Running using Python
--------------------
<!--Not recommeded -->

1. Convert ipynb to Python files:
```bash
jupyter nbconvert --to python nb.ipynb
```
2. Update config.json, remove unneeded pair.

3. Put Wikipedia dumps under: `templatesAlignment/../../dumps/%swiki/latest/` only.

4. Rename dump to reflect dumpdate as `latest` to simplify script run.

5. Run all scripts in order.

6. `02alignmentsSpark.py` can not be run on local machine at moment.
