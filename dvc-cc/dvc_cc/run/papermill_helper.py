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

                    if line.find('one_of:') > 0:
                        one_of_values = line.split('one_of:')[1].replace('"',"'")

                        if one_of_values.find("'") >= 0:
                            # first case, it was used ' at the beginning and ending of each possible value
                            one_of_list = one_of_values.split("'")[1::2]
                            do_strip = False
                        elif one_of_values.find(",") >= 0:
                            # second case, it was used , to seperate the possible values
                            one_of_list = one_of_values.split(",")
                            do_strip = True
                        else:
                            # third case, it was used space to seperate the values
                            one_of_list = one_of_values.split(" ")
                            do_strip = True

                        # build datatyoe:
                        datatype = '['
                        for constant in one_of_list:
                            if do_strip:
                                constant = constant.strip()
                                if len(constant) > 0:
                                    datatype = datatype + constant + ','
                            else:
                                datatype = datatype + constant + ','
                        if len(datatype) == 1:
                            raise ValueError('You need to set values for one_of constant in your jupyter notebook.\n'
                                             'Here are some examples:\n'
                                             'paraneter1 = 3.141 # one_of: 3.14159, 4.6692, 42\n'
                                             'paraneter2 = 1 # one_of: 1, 2, 3\n'
                                             'paraneter3 = 1 # one_of: \'1\', \'2\', \'3\'\n'
                                             'paraneter4 = 1 # one_of: 1 2 3'
                                             'paraneter5 = \'text1\' # one_of: \'text\',\'text2\',\'text3\'\n'
                                             'paraneter6 = \'text1\' # one_of: text, text2, text3\n'
                                             'paraneter7 = \'text1\' # one_of: text text2 text3\n'
                                             'paraneter8 = \'text1\' # SOME DESCRIPTION one_of: text text2 text3\n'
                                             '\nThe one_of values from which the user can choose, is in 2-4 and 5-8 '
                                             'the same.')
                        datatype = datatype[:-1] + ']'

                    elif default_value.find("'") >= 0 or default_value.find('"')  >= 0:
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