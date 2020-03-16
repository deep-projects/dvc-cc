#!/usr/bin/env python3

import dvc_cc.run.helper as helper
from argparse import ArgumentParser
from dvc.repo import Repo as DVCRepo
from git import Repo as GITRepo
import yaml
import os
from subprocess import check_output
from subprocess import Popen, PIPE
import json
import numpy as np
import subprocess
#import dvc_cc.hyperopt.dummy_to_dvc as dummy_to_dvc
import nbformat
from nbconvert import PythonExporter
import keyring
import requests
from dvc_cc.hyperopt.variable import *
from dvc_cc.hyperopt.hyperoptimizer import *
import uuid
from pathlib import Path

def read_params_from_parametercell(path_to_ipynb):
    """
     search for cells with the tag "parameters" and read this cells.
     returns a list of parameters back with three values each parameter: varname, vartype, help message
     if no parameter was found, it will return an empty list.
    """
    with open(path_to_ipynb) as f:
        notebook = json.load(f)
    founded_parameters = []
    cells = notebook["cells"]
    for i in range(len(cells)):
        c = cells[i]
        if 'tags' in c['metadata'] and 'parameters' in c['metadata']['tags']:
            commentar = ''
            for line in c['source']:
                line = line.strip()
                if line.find('#') >= 0:
                    commentar = commentar + line[line.find('#')+1:].strip()
                    line = line[:line.find('#')].strip()

                if line.find('=') > 0:
                    line_sep = line.split('=')
                    varname = line_sep[0].strip()
                    default_value = line_sep[1].strip()

                    if default_value.find("'") >= 0 or default_value.find('"')  >= 0:
                        datatype = 'not-supported'
                    elif default_value.isdigit():
                        datatype = 'int'
                    elif default_value.startswith('-') and default_value[1:].isdigit():
                        datatype = 'int'
                    elif default_value.find('.') >= 0:
                        datatype = 'float'
                    else:
                        datatype = 'not-supported'

                    if datatype != 'not-supported':
                        founded_parameters.append([varname, datatype, commentar])

                    commentar = ''
    return founded_parameters