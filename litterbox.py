import sys
import re
import os
import pathlib
import time
import argparse
from datetime import timedelta
from configparser import ConfigParser

import bottle

from common import expiration_pattern, to_seconds, logging_setup

LOGGER = "LBOX"


def cli_options(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--config", "-c", metavar="CONFFILE", help="Configuration file")
    return p.parse_args(argv)


lbox = bottle.Bottle()

def dir_list(dirname, ttl):
    files = {}
    with os.scandir(dirname) as it:
        for entry in it:
            if not entry.name.startswith(".") and entry.is_file():
                stat = entry.stat()
                files[entry.name] = (entry.path, stat.st_mtime, ttl, human_size(stat.st_size))
    return files


def get_all_files(config):
    all_files = {}
    for key, val in config.items():
        match = re.search(expiration_pattern, key, re.IGNORECASE)
        if match:
            ttl = to_seconds(int(match.group(1)), match.group(2))
            for key2, val2 in val.items():
                listdirs = val2.split()
                for d in listdirs:
                    all_files.update(dir_list(d, ttl))
    return all_files


def human_size(size):
    units = ["KB", "MB", "GB", "TB"]
    n = size
    lastu = "bytes"
    for u in units:
        lastn = n
        n = n / 1024
        if n < 1:
            return "{0:.2f} {1}".format(lastn, lastu)
        lastu = u
    else:
        return "{0:.2f} {1}".format(n, lastu)


@lbox.get("/file/<filename>")
def download(filename):
    all_files = get_all_files(lbox.config["mainconfig"])
    try:
        pn, mtime, ttl, size = all_files[filename]
    except KeyError:
        abort(404, f"We don't have {filename} [any longer]")
    filepath = pathlib.Path(pn)
    return bottle.static_file(filepath.name, root=str(filepath.parent), download=True)


@lbox.get("/file/")
def list():
    filelst = []
    all_files = get_all_files(lbox.config["mainconfig"])
    now = time.time()
    for filename, (pn, mtime, ttl, size) in all_files.items():
        time_left = mtime + ttl - now
        filelst.append( (filename, size, time_left) )
    return dict(files=sorted(filelst))

@lbox.get("/css/<filename>")
def sendcss(filename):
    csspath = lbox.config["mainconfig"]["webapp"]["css"]
    return bottle.static_file(filename, root=csspath)

@lbox.get("/html/<filename>")
def sendhtml(filename):
    htmlpath = lbox.config["mainconfig"]["webapp"]["html"]
    return bottle.static_file(filename, root=htmlpath)

@lbox.get("/js/<filename>")
def sendjs(filename):
    jspath = lbox.config["mainconfig"]["webapp"]["js"]
    return bottle.static_file(filename, root=jspath)

@lbox.get("/")
def mainpage():
    return sendhtml("index.html")

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    opts = cli_options(argv)
    cp = ConfigParser()
    cp.read(opts.config)
    lbox.config["mainconfig"] = cp
    log = logging_setup(lbox.config, LOGGER)
    bottle.run(app=lbox, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
