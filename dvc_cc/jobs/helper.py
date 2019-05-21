#!/usr/bin/env python3

import os

def getListOfFiles(dirName = '.', allow_hidden_directories_and_files = False, add_only_files_that_ends_with = None):
    """ This script gets from a directory all files in this folder and all subdirectories.
        Parameters:
            dirName (str): The path to the directory from which you want all files. Default is '.' which means the current path.
            allow_hidden_directories_and_files (bool): If true also Dot-Files and Dot-Directories get included in this search.
            add_only_files_that_ends_with (str): A string that must match the filename. If None every file get added to the list.
        Returns: A list of all found files.
    """
    listOfFile = os.listdir(dirName)
    allFiles = list()

    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        if not entry.startswith('.') or allow_hidden_directories_and_files:
            fullPath = os.path.join(dirName, entry)
            # If entry is a directory then get the list of files in this directory 
            if os.path.isdir(fullPath):
                    allFiles = allFiles + getListOfFiles(fullPath, allow_hidden_directories_and_files, add_only_files_that_ends_with)
            elif add_only_files_that_ends_with is None or entry.endswith(add_only_files_that_ends_with):
                allFiles.append(fullPath)
                
    return allFiles
