from argparse import ArgumentParser
import os
from dvc_cc.bcolors import *
import yaml

def parse_one_of(content):
    if len(content["dtype"]) == 0:
        return None
    elif len(content["dtype"]) == 1:
        r = content["dtype"][0]
    else:
        if "question" in content:
            print(content["question"])
        else:
            print("Please choose one of the following options:")
        dtype_dict = {}
        print("!!!!DTYPE:", content["dtype"])
        for o in content["dtype"]:
            if "name" in o and 'help' in o:
                dtype_dict[o['name']] = o
                print(o['name'] + ': ' + o['help'])
        user_input = None
        while user_input is None:
            user_input = input("Your choise: ").lower()
            if  user_input not in dtype_dict:
                print('Error, please use one of the above terms.')
                user_input = None
        r = dtype_dict[user_input]
    return parse(r)

def parse(content, interactive=True):
    """
    This helper becomes a prototype of for a config file and fill it.

    :param content: The content of the prototype config file.
    :param interactive: If True than the user will get interactive ask what he wants, if False it will take always the
                        default values or None as values.
    :return: You get the filled settings.
    """
    result = {}
    if type(content) is dict:
        if "dtype" in content:
            if type(content["dtype"]) is list:
                parse_one_of(content)

            """
                #print("DTYPE=LIST")
            elif content["dtype"].lower() is "string":
                print("DTYPE=STRING")
            elif content["dtype"].lower() is "int":
                print("DTYPE=int")
            elif content["dtype"].lower() is "int>0":
                print("DTYPE=int>0")
            elif content["dtype"].lower() is "int>=0":
                print("DTYPE=int>=0")
            """
        else:
            summary = {}
            for k in content.keys():
                if type(k) is dict:
                    summary[k] = parse(content[k])


            if "value" in content:
                result[]


    # if dtype is a list
    # if dtype is int, int>0, ...