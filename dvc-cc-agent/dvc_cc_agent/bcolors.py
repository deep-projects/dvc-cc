import os

class bcolors:
    HEADER = '\033[95m' if os.name!='nt' else ''
    OKBLUE = '\033[94m' if os.name!='nt' else ''
    OKGREEN = '\033[92m' if os.name!='nt' else ''
    WARNING = '\033[93m' if os.name!='nt' else ''
    FAIL = '\033[91m' if os.name!='nt' else ''
    ENDC = '\033[0m' if os.name!='nt' else ''
    BOLD = '\033[1m' if os.name!='nt' else ''
    UNDERLINE = '\033[4m' if os.name!='nt' else ''
