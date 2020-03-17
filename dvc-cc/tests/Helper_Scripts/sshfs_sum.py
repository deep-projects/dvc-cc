# This test use the Script: tests/Helper_Scripts/train.py

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--path1', type=str,default=None)
parser.add_argument('--path2', type=str,default=None)
parser.add_argument('--path3', type=str,default=None)
args = parser.parse_args()

import hashlib
import os

def hash_directory(path):
    # calculate the checksum only for the foldername and the files in it. it does not calculate the checksum for
    # subdirectories!
    digest = hashlib.sha1()

    for file in os.listdir(path):
        file_path = os.path.join(path, file)

        # Hash the path and add to the digest to account for empty files/directories
        digest.update(hashlib.sha1(file_path[len(path):].encode()).digest())

        # Per @pt12lol - if the goal is uniqueness over repeatability, this is an alternative method using 'hash'
        # digest.update(str(hash(file_path[len(path):])).encode())

        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f_obj:
                while True:
                    buf = f_obj.read(1024 * 1024)
                    if not buf:
                        break
                    digest.update(buf)

    return digest.hexdigest()

print(args.path1, ':', hash_directory(args.path1), ';', os.listdir(args.path1))
print(args.path2, ':', hash_directory(args.path2), ';', os.listdir(args.path2))
print(args.path3, ':', hash_directory(args.path3), ';', os.listdir(args.path3))