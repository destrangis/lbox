import argparse
import sys
import time
import os
import re
from configparser import ConfigParser

from common import to_seconds, expiration_pattern, logging_setup

LOGGER = "EXPIRATOR"

def read_config(cpobject):
    sections = {}

    for secname in cpobject.sections():
        match = re.search(expiration_pattern, secname, re.IGNORECASE)
        if match:
            secs = to_seconds(int(match.group(1)), match.group(2))
            for var, directory in cpobject[secname].items():
                dirlst = directory.split()  # perhaps more than one per line...
                if secs in sections:
                    sections[secs] += dirlst
                else:
                    sections[secs] = dirlst
    return sections

def expire_directory(dirname, secs):
    with os.scandir(dirname) as it:
        for entry in it:
            if not entry.name.startswith(".") and entry.is_file():
                expire_entry(entry, secs)

def expire_entry(entry, secs):
    stat = entry.stat()
    now = time.time()
    if (now - stat.st_mtime) > secs:
        log.info("Removing '%s'", entry.path)
        os.remove(entry.path)

def expire_all(sections):
    for secs in sections.keys():
        for directory in sections[secs]:
            expire_directory(directory, secs)




def cli_options(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--config", "-c", metavar="CONFFILE", help="Configuration file")
    p.add_argument("--once", "-1", action="store_true", default=False, help="run just once instead of in a loop")
    p.add_argument("--sleep-interval", "-s", metavar="SECS", type=int, default=30, help="Polling interval default 30 secs")
    return p.parse_args(argv)

def main(argv=None):
    global log

    if argv is None:
        argv = sys.argv[1:]

    opts = cli_options(argv)
    if not opts.config:
        log.error("No configuration file provided. Exiting(1)")
        return 1

    cp = ConfigParser()
    cp.read(opts.config)

    log = logging_setup(cp, LOGGER)
    sections = read_config(cp)
    while 1:
        expire_all(sections)
        if opts.once:
            break
        time.sleep(opts.sleep_interval)

    return 0

if __name__ == "__main__":
    sys.exit(main())
