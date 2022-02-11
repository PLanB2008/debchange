#!/usr/bin/env python3 

###################################
# by andreas.till@netzint.de
# Version 1.1 from 11.02.2022
# needs: 
#   
###################################


import os, tempfile
from subprocess import call
import shutil
import sys
import re
import time
import argparse

EDITOR = os.environ.get('EDITOR','vim')
__version__ = 'version 0.1.0'

def main():



    info = getInformation()

    # Get environment values for template
    info['debfullname'] = os.environ.get('DEBFULLNAME', 'Firstname Lastname')
    info['debemail'] = os.environ.get('DEBEMAIL', 'name@example.org')
    info['debfullname'] = "Andreas Till"
    info['debemail'] = "andreas.till@netzint.de"



    # date format example: Fri, 13 Jul 2012 15:05:04 +0200
    info['debian_formatted_date'] = time.strftime("%a, %d %b %Y %H:%M:%S +0200", time.localtime())
    version = info['pkg_version']
    minor= version.split('-')[1]
    version = version.split('.')
    version[2] = str(int(version[2].split('-')[0]) + 1)
    info['pkg_version']= '.'.join(version)+'-'+minor

    # Templated Changelog Entry 
    template = """%(pkg_name)s (%(pkg_version)s) %(pkg_distrib)s; urgency=low

      * 

     -- %(debfullname)s <%(debemail)s>  %(debian_formatted_date)s

    """

    pushed_content = template %info + changelog_content

    with tempfile.NamedTemporaryFile() as f:

        # Write template contents
        f.write(pushed_content)
        f.flush()

        # Spawn Editor 
        call([EDITOR, f.name])

        # Copy new file 
        shutil.copyfile(f.name, "debian/changelog")

def getInformation():
    # read changelog file
    if os.path.exists("debian/changelog"):
        with open('debian/changelog') as f:
            changelog_content = f.read()
    else:
        print ("You must run debchange.py in a source package containing debian/changelog")
        sys.exit(1)
    # Get original information ( package_name (version) distrib; urgency )
    first_line = changelog_content.split('\n')[0].strip()
    template = re.compile(r"^(?P<pkg_name>.*) \((?P<pkg_version>.*)\) (?P<pkg_distrib>.*); (?P<pkg_urgency>.*)$" )
    m = template.match(first_line)
    info = m.groupdict()
    return info

def tags():
    info = getInformation()
    #print ('tags')
    print (info['pkg_version'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='debhelper alternative written in python')
    parser.add_argument('-v', dest='version', action='store_true', help='print the version and exit')
    parser.add_argument('-t', dest='tags', action='store_true',
                    help='show all tasks in the specified task list')
    args = parser.parse_args()
    if args.version:
        print (__version__)
		quit()
    
    if args.tags is not False:
        tags()
    else:
        main()
