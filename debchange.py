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
import subprocess
import filecmp

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

    if "-" in version:
        minor= version.split('-')[1]
        version = version.split('.')
        version[-1] = str(int(version[-1].split('-')[0]) + 1)
        info['pkg_version']= '.'.join(version)+'-'+minor
    else:
        version = version.split('.')
        version[-1] = str(int(version[-1]) + 1)
        info['pkg_version']= '.'.join(version)

    # Templated Changelog Entry 
    template = """%(pkg_name)s (%(pkg_version)s) %(pkg_distrib)s; urgency=low

  * 

 -- %(debfullname)s <%(debemail)s>  %(debian_formatted_date)s

"""

    pushed_content = template %info + info['changelog_content']

    with tempfile.NamedTemporaryFile() as f:

        # Write template contents
        f.write(pushed_content.encode())
        f.flush()

        # Spawn Editor 
        shutil.copyfile(f.name, "debian/check_tmp")
        call([EDITOR, f.name])

        # check if changes where made
        if not filecmp.cmp(f.name, 'debian/check_tmp'):
            print('Written updateded changelog')
            # Copy new file 
            shutil.copyfile(f.name, "debian/changelog")
            os.unlink('debian/check_tmp')
        else:
            print('Nothing changed')
            os.unlink('debian/check_tmp')


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
    info['changelog_content'] = changelog_content
    return info

def check_if_tag_exists(tag):
    info = getInformation()
    #print ('tags')
    #output = subprocess.check_output(['git', 'tag'],  shell=False, text=True).strip()
    cmd = subprocess.run(['git', 'tag'], capture_output=True, text=True)
    tags=[]
    for line in cmd.stdout.splitlines():
        tags.append(line)
    if tag in tags:
        return True
    else:
        return False

def tags():
    if not check_if_tag_exists('v'+info['pkg_version']):
        print ('Adding tag v'+info['pkg_version'])
        cmd = subprocess.run(['git', 'tag', 'v'+info['pkg_version']], capture_output=True, text=True)
        print (cmd.stdout)
        print ('Pushing tags')
        cmd = subprocess.run(['git', 'push', '--tags'], capture_output=True, text=True)
        print (cmd.stdout)
        #cmd = subprocess.run(['git', 'tag'], capture_output=True, text=True)
        print (cmd.stdout)
    else:
        print ('Tag v'+info['pkg_version']+' already exists')

def delete_last_tag():
    if check_if_tag_exists('v'+info['pkg_version']):
        cmd = subprocess.run(['git', 'tag', '-d', 'v'+info['pkg_version']], capture_output=True, text=True)
        print (cmd.stdout)
        cmd = subprocess.run(['git', 'push', '--delete', 'origin', 'v'+info['pkg_version']], capture_output=True, text=True)
        print (cmd.stdout)
    tags()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='debhelper alternative written in python')
    parser.add_argument('-v', dest='version', action='store_true', help='print the version and exit')
    parser.add_argument('-f', dest='force', action='store_true',
                    help='force recreation of last tag')
    parser.add_argument('-t', dest='tags', action='store_true',
                    help='update and push git tag')
    parser.add_argument('-u', dest='update', action='store_true',
                    help='update and iterate debian/changelog')
    args = parser.parse_args()
    if args.version:
        print (__version__)
        quit()
    if args.tags is not False:
        if args.force is not False:
            delete_last_tag()
        tags()
        quit()
    if args.update is not False:
        main()
        quit()
    else:
        parser.print_help()
