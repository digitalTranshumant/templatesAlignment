Initial setup
=============
Login to stat100X,

<code>ssh stat100X</code>

Setup proxy
-----------
<code>export https_proxy=https://webproxy.eqiad.wmnet:8080</code>

<code>export http_proxy=http://webproxy.eqiad.wmnet:8080</code>

Setup repository
----------------
<code>git clone https://github.com/digitalTranshumant/templatesAlignment.git</code>

<code>cd templatesAlignment</code>

Create virtualenv
-----------------
<code>virtualenv --python=/usr/bin/python3 python3</code>

Active the virtual environment by:

<code>source python3/bin/activate</code>

Now, install jupyter notebook:

<code>pip install jupyter</code>

Next, add the following lines to your .profile file:

<code>export PYSPARK_DRIVER_PYTHON=jupyter</code>

<code>export PYSPARK_DRIVER_PYTHON_OPTS='notebook'</code>

<code>export PYSPARK_PYTHON=/usr/bin/python3.7</code>

<code>export PYSPARK_PYTHON=/srv/home/USER/python3/bin/python</code>

You can additionally add these two lines to make your life easier:

<code>alias venvspark="source python3/bin/activate; source ~/.profile"</code>

<code>alias startspark="pyspark2 --master yarn --deploy-mode client --executor-memory 8g --driver-memory 8g --conf spark.dynamicAllocation.maxExecutors=128"</code>

Close the session, and you will have everything configured.

Starting notebook
=================
Make sure to check Kerberos authentication timeout first. Default is set to 48 hours now.

<code>klist</code>

Extend it by running kinit:

<code>kinit</code>

Now, you can login again and you will just need to do this:

<code>venvspark</code>

<code>startspark</code>

Press ESC,

And check in which port the jupyter notebook is running (usually you should have 8888 or 8889), in this example is 8889

<code>http://localhost:8889</code>

Then, in your local machine, create a tunnel by running:

<code>ssh -N stat100X -L 8889:127.0.0.1:8889</code>

And then using your browser you will see the normal notebook in:

<code>http://localhost:8889</code>

Running scripts
===============
1. Run all notebooks in order.
2. 00ExtractNamedTempates.ipynb overwrites existing output if runs again, so it is better to save products json files somewhere to save time.

Notes
=====
1. 02alignmentsSpark.py can not be run on local machine.
2. If running locally, `01Download Models.py` need to run with ipython or just download needed models.
3. fastText_multilingual module is available at: https://github.com/babylonhealth/fastText_multilingual Apply patch given at #23 to fix ModuleNotFound error while running script.
4. 03ProduceAlignments.py requires https://github.com/facebookresearch/fastText/tree/master/python instead of version provided by pip.

Also see
========
* Issues related to Kerberos access: https://wikitech.wikimedia.org/wiki/SWAP#Access_and_infrastructure
