Initial setup
-------------
Login to stat1007:

$ ssh stat1007

Setup proxy:

$  export https_proxy=https://webproxy.eqiad.wmnet:8080
$  export http_proxy=http://webproxy.eqiad.wmnet:8080

$  virtualenv --python=/usr/bin/python3 python3

Active the virtual environment by doing this:

$  source python3/bin/activate

now install jupyter notebook:

$  pip install jupyter

Next, add the following lines to your .profile file

export PYSPARK_DRIVER_PYTHON=jupyter
export PYSPARK_DRIVER_PYTHON_OPTS='notebook'
export PYSPARK_PYTHON=/usr/bin/python3.5
export PYSPARK_PYTHON=/srv/home/USER/python3/bin/python

You can additionally add these two lines to make your life easier:

alias venvspark="source python3/bin/activate; source ~/.profile" 
alias startspark="pyspark2 --master yarn --deploy-mode client --executor-memory 8g --driver-memory 8g --conf spark.dynamicAllocation.maxExecutors=128"

Close the session, and you will have everything configured.

Starting notebook
-----------------
Now, you can login again and you will just need to do this:

$ venvspark
$ startspark

Press ESC

And check in which port the jupyter notebook is running (usually you should have 8888 or 8889), in this example is 8889

 http://localhost:8889

Then in your local machine (laptop), create a tunnel by running:

$  ssh -N stat1007.eqiad.wmnet -L 8889:127.0.0.1:8889

And then using your browser you will see the normal notebook in:

 http://localhost:8889

Also see
--------
* Issues related to Kerberos access: https://wikitech.wikimedia.org/wiki/SWAP#Access_and_infrastructure
