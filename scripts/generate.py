#!/usr/bin/python

import os
import sys
from lxml import etree
import utils

def create_changelog(dir):
    changesets = utils.get_changesets(dir)

    if not os.path.exists('install.xml'):
        create_installxml(dir, changesets)
    else:
        if not os.path.exists('update.xml'):
            create_updatexml(dir)

        next_release = utils.get_next_release(dir)
        create_versionxml(dir, next_release, changesets)


def create_installxml(dir, changesets):
    xmlfile = os.path.join(dir, 'install.xml')
    root = get_changelogxml(xmlfile)

    # another child with text
    child = etree.Element('child')
    child.text = 'some text'
    root.append(child)

    for cs in changesets:

        include = etree.Element('include')
        include.set('file', cs.file)
        include.set('relativeToChangelogFile', 'true')
        root.append(include)

    et = etree.ElementTree(root)
    et.write(xmlfile, pretty_print=True)

def create_updatexml(dir):
    xmlfile = os.path.join(dir, 'update.xml')
    root = get_changelogxml(xmlfile)

    include = etree.Element('include')
    include.set('file', 'install.xml')
    include.set('relativeToChangelogFile', 'true')
    root.append(include)

    for version in utils.get_directory_versions(dir):
        include = etree.Element('include')
        include.text = os.path.join(dir, 'master.xml')
        root.append(include)

    et = etree.ElementTree(root)
    et.write(xmlfile, pretty_print=True)

def update_updatexml(dir, version_xmlfile):
    xmlfile = os.path.join(dir, 'update.xml')
    root = get_changelogxml(xmlfile)

    include = etree.Element('include')
    include.set('file', 'install.xml')
    include.set('relativeToChangelogFile', 'true')
    root.append(include)

    et = etree.ElementTree(root)
    et.write(xmlfile, pretty_print=True)

def create_versionxml(dir, version, changesets):
    xmlfile = os.path.join(dir, 'master.xml')
    root = get_changelogxml(xmlfile)

    for cs in changesets:

        elem = etree.Element('changeSet')
        elem.set('file', cs.file)
        elem.set('relativeToChangelogFile', 'true')
        # for a latest object we can automatically create the rollback
        if cs.location == 'latest':
            elem_rb = etree.Element('rollback')
            if utils.is_new_file(dir, cs.file):
                if cs.type in ['package', 'trigger', 'view']:
                    elem_rb.text = 'drop %s %s;' % (self.type, self.fullname)
            else:
                # rollback to a particular version of the file
                # use git checkout <tag> <filename> to revert this file
                elem_sqlfile = etree.Element('sqlFile')
                # move back a directory for relative path
                elem_sqlfile.set('file', os.path.join('..', cs.file))
                elem_sqlfile.set('relativeToChangelogFile', 'true')
                elem_rb.append(elem_sqlfile)
            elem.append(rollback)
        root.append(elem)

    et = etree.ElementTree(root)
    et.write(xmlfile, pretty_print=True)

def get_changelogxml(xmlfile):
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
        changelog = etree.fromstring(xml)
    return changelog
