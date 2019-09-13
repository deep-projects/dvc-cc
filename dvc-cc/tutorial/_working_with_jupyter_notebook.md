This site is an extension of the [main tutorial](Get_Started.md). Make sure you read it before you read this site.

# DVC-CC: Working with the Jupyter-Notebook

DVC-CC can handle Jupyter-Notebooks very well. So if you want to program and debug in Jupyter-Notebooks and run longer
experiments with different settings on the cluster, DVC-CC is the right software for you. You can work with 
Jupyter-Notebook locally. If you want that this script run on the server, DVC-CC will convert all the 
Jupyter-Notebooks to Py-Files in the command `dvc-cc run`. The only thing that you need to do is to use the flag `-nb`.

The basic idea is allow you to work with Jupyter-Notebooks local and if you want to run this script on the server,
 
 convert the Jupyter-Notebooks to Py-Files if the script should run at the cluster.

The Idea is to convert automaticly convert the Jupyter-Notebooks to py-files in the `cc_` and `rcc_` branches of 
DVC-CC. That DVC-CC can do this for you, you need to use the `-nb` flag on the `dvc-cc run` command. Everything else 
will handle DVC-CC for you.

You can also hide or include cells so that they






If you want to work with a jupyter notebook to make fast changes but run parallel larger experiments on the server you just can use DVC-CC ;-)

If you call `dvc-cc run` with the `-nb` parameter it will convert all jupyter notebook to py files so that they can be executed on the server. By defining your pipeline you would just use a .py file instead of the ipynb file.

If the first line of a cell starts with `#%% dvc-cc-hide` it will ignore this cell by converting from a jupyter notebook to a py file. If you have a multiline commend that starts with `"""dvc-cc-show` than this commend will be uncommend and will be executed on the server. With this you can define some code that only runs in your jupyter notebook or only runs on the server in the py file.
