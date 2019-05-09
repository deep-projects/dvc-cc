import sys
sys.path.insert(0,'code')
sys.path.insert(0,'code/helper')
from _utility import *
from argparse import ArgumentParser

def get_args():
    parser = ArgumentParser()
    parser.add_argument('-t','--is_test_run', action='store_true')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    print(get_name_of_experiment(get_args()))
