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

def jupyter_notebook_to_source(root, file_name):
    with open(str(Path(root+'/'+file_name))) as f:
        notebook = json.load(f)

    cells = notebook["cells"]
    cleared_cells = []
    for i in range(len(cells)):
        c = cells[i]
        use_this_cell = True
        if c['cell_type'] == 'code':

            # ignore cells
            if 'pycharm' in c['metadata'] and 'name' in c['metadata']['pycharm']:
                if c['metadata']['pycharm']['name'].replace(' ', '').lower().startswith('#%%dvc-cc-h'):
                    use_this_cell = False
                elif c['metadata']['pycharm']['name'].replace(' ', '').lower().startswith('#%%dch'):
                    use_this_cell = False
            if len(c['source']) > 0:
                if c['source'][0].replace(' ', '').lower().startswith('#%%dvc-cc-h'):
                    use_this_cell = False
                elif c['source'][0].replace(' ', '').lower().startswith('#%%dch'):
                    use_this_cell = False
                elif c['source'][0].replace(' ', '').lower().startswith('#dvc-cc-h'):
                    use_this_cell = False
                elif c['source'][0].replace(' ', '').lower().startswith('#dch'):
                    use_this_cell = False

            # include code
            if use_this_cell:
                c_source_lines = []
                is_in_uncommand_line = False
                for source_line in c['source']:
                    source_line_tmp = source_line.replace('\t', '').replace(' ', '')
                    if is_in_uncommand_line == False and (source_line_tmp.find('"""dcs') >= 0 or source_line_tmp.find('"""dvc-cc-show') >= 0):
                        pos = source_line_tmp.find('"""dcs')
                        if pos == -1:
                            pos = source_line_tmp.find('"""dvc-cc-show')
                        if source_line_tmp.find('"""',pos+5) == -1:
                            is_in_uncommand_line = True
                    elif is_in_uncommand_line:
                        if source_line_tmp.find('"""') >= 0:
                            is_in_uncommand_line = False
                        else:
                            c_source_lines.append(source_line)
                    else:
                        c_source_lines.append(source_line)
                c['source'] = c_source_lines

            if 'outputs' in c:
                c['outputs'] = []
        if use_this_cell:
            cleared_cells.append(c)
    notebook["cells"] = cleared_cells

    nb = nbformat.reads(json.dumps(notebook), nbformat.NO_CONVERT)
    exporter = PythonExporter()
    source, meta = exporter.from_notebook_node(nb)

    # nicer output :)
    source = re.sub('\n\n# In\[[0-9\ ]*\]:\n\n\n', '\n#%%\n', source)

    return source
