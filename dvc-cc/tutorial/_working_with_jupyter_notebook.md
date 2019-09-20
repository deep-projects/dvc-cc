This site is an extension of the [main tutorial](Get_Started.md). Make sure you read it before you read this site.

# DVC-CC: Working with the Jupyter-Notebook
Jupyter Notebooks are an excellent tool to script and test some Python code. Your divide your python source code in 
the Jupyter Notebooks in cells and can run every cell by themself. You can also add MarkDown cells that allow you to 
include math formulas in your Jupyter Notebook.

> **Even more**: If you are only interested in dividing your script in executable cells than you can do this also with
                your py file by using PyCharm.


If you have a Jupyter-Notebook in your repository, DVC-CC  convert your Jupyter Notebook to a py file and execute 
this py file in the cluster. This all will done automaticly and the workflow is not different than this one from the 
main tutorial.

This means that you will also use `.py` file endings for you `.ipynb`-file in the `dvc-cc hyperopt new` or `dvc run 
--no-exec` command. If you have the same source as in the [main tutorial](Get_Started.md) you don't need 
anything to change. All commands from the main tutorial work the same. You can test it with the same source code just
in form of a jupyter notebook, by using `wget -O source/train.ipynb https://bit.ly/2mn49ms` instead of
`wget -O source/train.py https://bit.ly/2krHi8E` and do the
same commands from the [main tutorial](Get_Started.md).

If you tried the above you will detect some problems. For example the source code `args = parser.parse_args()` from 
the first cell will throw you an error if you run your script in the jupyter notebook. That means you have now a 
script that can run in the cluster but you can not really work locally with this.

To solve this issue DVC-CC gives you the possibility to influence the convertion from Jupyter-Notebook to a .py file 
by including comment out source code with `"""dvc-cc-show` (or short `"""dcs`) or excluding source cells with 
`#dvc-cc-hide` (or short `#dch`). For an 
example see the following Jupyter Notebook and the py file that was converted by DVC-CC from the Jupyter Notebook:

!TODO: IMAGE !!!

With the following command you can download the Jupyter Notebook that is shown above:
```
wget -O source/train.ipynb https://bit.ly/2kmYV9E
```


