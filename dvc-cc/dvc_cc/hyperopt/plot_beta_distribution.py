from argparse import ArgumentParser
import matplotlib.pyplot as plt
import numpy as np
from dvc_cc.bcolors import *


DESCRIPTION = 'This script represents beta distributions. You can use this to work with '+bcolors.OKBLUE+'dvc-cc run'+bcolors.ENDC+ \
              ' and see from which distribution the hyperparemeter is drawn.'

def main():
    parser = ArgumentParser(description=DESCRIPTION)
    args = parser.parse_args()

    print('Here matplotlib.pyplot.show() will be called.')
    print('Use CTRL+C to stop this script.')
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


