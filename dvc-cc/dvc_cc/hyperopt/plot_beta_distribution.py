from collections import OrderedDict
from dvc_cc.version import VERSION
from dvc_cc.cli_modes import cli_modes

from argparse import ArgumentParser
import matplotlib.pyplot as plt
import numpy as np
import seaborn

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


DESCRIPTION = 'DVC-CC (C) 2019  Jonas Annuscheit. This software is distributed under the AGPL-3.0 LICENSE.'

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    args = parser.parse_args()

    print('Use CTR+C to stop this process!')
    min = float(input('Min-Value: '))
    max = float(input('Max-Value: '))
    results = {}
    while True:
        a = float(input('A-Value: '))
        b = float(input('B-Value: '))
        print('Plotting')
        values = np.random.beta(a, b, size=1000000)
        values *= max - min
        values += min
        r = np.histogram(values,bins=100, density=True)
        r = r[0] ,  [(r[1][i]+r[1][i+1])/2.0 for i in range(len(r[1])-1)]
        name = 'A:'+str(a)+' ; B:'+str(b)
        results[name] = r
        for key in results:
            r = results[key]
            plt.bar(r[1],r[0], width=r[1][1]-r[1][0], alpha=0.4, label=key)
        plt.legend()
        plt.show()


