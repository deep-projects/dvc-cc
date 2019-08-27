# Sorry
This tutorial is in work!
![IN WORK](work-2062096_640.jpg)

If you want to work with a jupyter notebook to make fast changes but run parallel larger experiments on the server you just can use DVC-CC ;-)

If you call `dvc-cc run` with the `-nb` parameter it will convert all jupyter notebook to py files so that they can be executed on the server. By defining your pipeline you would just use a .py file instead of the ipynb file.

If the first line of a cell starts with `#%% dvc-cc-hide` it will ignore this cell by converting from a jupyter notebook to a py file. If you have a multiline commend that starts with `"""dvc-cc-show` than this commend will be uncommend and will be executed on the server. With this you can define some code that only runs in your jupyter notebook or only runs on the server in the py file.
