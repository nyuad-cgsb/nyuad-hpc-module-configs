#!/usr/bin/env python3

import hashlib
import glob
import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.DEBUG)

def md5(fname):

    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def find_files():

    create_env = False
    files = glob.glob("**/environment*.yml", recursive=True)

    for tfile in files:

        logging.debug("Trying file {}".format(tfile))

        if not os.path.exists(tfile + ".md5"):

            create_env = try_conda_create_env(tfile)

        elif os.path.exists(tfile + ".mdf5"):

            orig_md5 = open(tfile + ".md5", "rb").read()
            new_md5 = md5(tfile)

            if not orig_md5 == new_md5:
                create_env = try_conda_create_env(tfile)
            else:
                create_env = True

        if create_env:
            md5sum = md5(tfile)
            fh = open(tfile+".md5", "w")
            fh.write(md5sum)
            fh.close()
            os.system("touch {}.build.pass".format(tfile) )
        else:
            os.system("rm -rf {}.build.pass".format(tfile) )

def try_conda_create_env(fname):

    retries_max = 3
    retries_count = 0
    create_env = False

    while retries_count <= retries_max:
        retries_count = retries_count + 1
        ec = run_conda_env_create(fname)
        if ec == 0:
            logging.info('Conda Env for {} created successfully'.format(fname) )
            create_env = True
            break
        else:
            logging.warn('Conda Env was NOT created successfully! Retrying {}'.format(retries_count))

    return create_env


def run_conda_env_create(fname):

    readSize = 1024 * 8
    cmd = "conda env create -f {}".format(fname)

    try:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             stdin=subprocess.PIPE, close_fds=True, executable="/bin/bash")
    except OSError as err:
        print("OS Error: {0}".format(err))

    p.stdin.close()

    ec = p.poll()

    while ec is None:
        # need to read from time to time.
        # - otherwise the stdout/stderr buffer gets filled and it all stops working
        logging.debug(p.stdout.read(readSize).decode("utf-8"))
        ec = p.poll()
        logging.debug("Exit Code {}".format(ec))

    # read remaining data (all of it)
    logging.debug(p.stdout.read().decode("utf-8"))

    return ec

##MAIN

if __name__ == "__main__":
    find_files()
