import argparse #for parsing command line arguments
import configparser #for reading configuration files
from datetime import datetime #for getting the current date and time
import grp, pwd #for getting user and group information 
from fnmatch import fnmatch #for matching file names
import hashlib #for hashing files: git uses SHA-1; for reference look merkle tree
from math import ceil #for rounding up numbers
import re #for regular expressions
import sys #for getting the current working directory
import zlib #for compressing and decompressing files
import os


argparser = argparse.ArgumentParser(description="A simple implementation of git named Gittu.")
argsubparser = argparser.add_subparsers(dest='command', required=True) #sub parsers are stored in the dest i.e command
argsubparser.required = True


def main(argv=sys.argv[1:]): # gittu add filename.txt 
    args = argparser.parse_args(argv)
    match args.command:
        # case "add"      :   cmd_add(args)
        # case "cat-file" :   cmd_cat_file(args)
        # case "check-ignore": cmd_check_ignore(args)
        # case "commit" : cmd_commit(args)
        # case "hash-object" : cmd_hash_object(args)
        case "init" : cmd_init(args)
        # case "log" : cmd_log(args)
        # case "ls-files" :cmd_ls_files(args)
        # case "ls-tree": cmd_ls_tree(args)
        # case "rm" : cmd_rm(args)
        # case "show-ref": cmd_show_ref(args)
        # case "status" : cmd_status (args)
        # case "tag" : cmd_tag(args)
        case _ : print("Bad command.")


"""
General Git repo structure is 

->working folder
    ->.git

"""
class GitRepository (object):
    workrepo = None
    gitdir = None
    conf = None

    def __init__(self, path, force=False):
        self.workrepo = path 
        self.gitdir = os.path.join(path, '.gittu')

        if not(force or os.path.isdir(self.gitdir)):
            raise Exception(f"Not a gittu repository {path}")
        
        self.conf = configparser.ConfigParser()
        cf = repo_file(self, "config")

        if cf and os.path.exists(cf):
            self.conf.read([cf])
        elif not force:
            raise Exception("Configuration is missing")
        
        ##dunno why this is used.
        if not force:
            vers = int(self.conf.get("core", "repositoryformatversion"))
            if vers != 0:
                raise Exception("Unsupported repositoryformatversion: {vers}")


def repo_path(repo, *path): # *(asterisk) represnts we can take multiple params under path
    return os.path.join(repo.gitdir, *path)


#create a repo file
def repo_file(repo, *path, mkdir=False):
    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)

#get a repo dir or create if mkdir set
def repo_dir(repo, *path, mkdir=False):
    path = repo_path(repo, *path)

    if os.path.exists(path):
        if os.path.isdir(path):
            return path
        else:
            raise Exception(f"Not a directory: {path}")
    

    if mkdir:
        os.makedirs(path)
        return path
    else:
        return None


def repo_create(path):

    repo = GitRepository(path, force=True)

    if os.path.exists(repo.workrepo):
        if not os.path.isdir(repo.workrepo):
            raise Exception(f"${path} is not a directory!")
        if os.path.exists(repo.gitdir) and os.listdir(repo.gitdir):
            raise Exception(f"${path} is a already a gittu repository!")
    else:
        os.makedirs(repo.workrepo)

    #initialize the git directory
    assert repo_dir(repo, "branches", mkdir=True)
    assert repo_dir(repo, "objects", mkdir=True)
    assert repo_dir(repo, "refs", "tags", mkdir=True)
    assert repo_dir(repo, "refs", "heads", mkdir=True)

    with open(repo_file(repo, "description"), "w") as f:
        f.write("Unnamed repository; edit this file 'description' to name the repository.\n")

    with open(repo_file(repo, "HEAD"), "w") as f:
        f.write("ref: refs/heads/master\n")
    
    with open(repo_file(repo, "config"), "w") as f:
        config = repo_default_config()
        config.write(f)

    return repo


def repo_default_config():
    config = configparser.ConfigParser()

    config.add_section("core")
    config.set("core", "repositoryformatversion", "0")
    config.set("core", "filemode", "true")
    config.set("core", "bare", "false")

    return config

arginit = argsubparser.add_parser("init", help="Initialize a new, empty repository.")
arginit.add_argument(
    "path",
    metavar="directory",
    nargs="?",
    default=".", #default should be current directory
    help="Path to the repository to be initialized.",
    )

def cmd_init(args):
    repo_create(args.path)