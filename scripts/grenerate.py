#!/usr/bin/python

import os
import sys
from lxml import etree


def main(argv):

   """try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print('%s -i <inputfile> -o <outputfile>' % (__file__))
      sys.exit(2)
   """

    gitdir = os.getcwd()
    sqldir = os.path.join(gitdir, 'sql')
    generate(gitdir, sqldir)

def generate(dir, changed_files=None):

    if not os.path.exists('install.xml'):
        create_installxml(dir)

    if not os.path.exists('update.xml'):
        create_updatexml(dir)

    for f in sorted(changed_files) if f[0].lower() == 'v':
        version = f.split('/')[0]
        create_version_xml(dir, f)
    else:
        # Interate the whole directory if no changed_files
        prev_version = None
        for version in get_directory_versions(dir):
            changes = get_changed_files(dir, prev_version, version)
            create_version_xml(dir, version, changes)
            prev_version = version

def create_install_xml(dir):
    xmlfile = os.path.join(dir, 'install.xml')
    changelog = get_changelog(xmlfile)


    # another child with text
    child = etree.Element('child')
    child.text = 'some text'
    changelog.append(child)

    changelog.write(xmlfile, pretty_print=True)

def create_update_xml(dir):
    xmlfile = os.path.join(dir, 'update.xml')
    changelog = get_changelog(xmlfile)

    include = etree.Element('include')
    include.text = 'install.xml'
    changelog.append(include)

    for version in get_directory_versions(dir):
        include = etree.Element('include')
        include.text = os.path.join(dir, 'master.xml')
        changelog.append(include)

def update_update_xml(dir, version_xmlfile):
    xmlfile = os.path.join(dir, 'update.xml')
    changelog = get_changelog(xmlfile)

    include = etree.Element('include')
    include.set('file', 'install.xml')
    include.set('relativeToChangelogFile', 'true')
    changelog.append(include)

def create_versionxml(dir, version, changed_files):
    xmlfile = os.path.join(dir, 'master.xml')
    changelog = get_changelog(xmlfile)

    for f in changed_files:
        # get the type base on what folder it is in
        type = f.split('/')[0]
        if type == 'latest'
            # create a rolback for the latest
            sqlfile = etree.Element('sqlFile')

            changeset = etree.Element('changeSet')
            changeset.set('file', 'install.xml')
            changeset.set('relativeToChangelogFile', 'true')
            changeset.append(rollback)
            changelog.append(changeset)
    else:
        for root, dir, files in os.walk(dir):


def get_changelog:
    if os.path.exists(xmlfile):
        changelog = etree.iterparse()
    else:
        xml = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
                 <databaseChangeLog
                     xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
                     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                     xmlns:ext="http://www.liquibase.org/xml/ns/dbchangelog-ext"
                     xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-3.1.xsd
                     http://www.liquibase.org/xml/ns/dbchangelog-ext http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-ext.xsd"/>
               """
        changelog = etree.fromstring(xml
    return changelog

def get_changed_files(gitdir, prev_version, version):
    if changed_files:
        return changed_files
    repo = Repo('.')
    t = repo.head.commit.tree
    repo.git.diff(t)

def get_directory_versions(dir):
    for version in sorted(dir) if version[0].lower() == 'v' and not os.path.isfile(os.path.join(dir, version)):
        yield version



if __name__ == '__main__':
   main(sys.argv[1:])
