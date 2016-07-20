#!/usr/bin/python

import os
import sys
from lxml import etree
import utils

def create_changelog(dir):
    changesets = utils.get_changesets(dir)
    if len(changesets) == 0:
        print('No sql file changes detected in %s' % dir)
        return

    installxml = os.path.join(dir, 'install.xml')
    #if utils.get_last_release is None or not os.path.exists(installxml) or
    if utils.is_new_file(dir, installxml):
        if os.path.exists(installxml):
            os.path.remove(installxml)
        create_installxml(dir, changesets)
    else:
        if not os.path.exists(os.path.join(dir, 'update.xml')):
            create_updatexml(dir)

        next_release = utils.get_next_release(dir)
        create_versionxml(dir, next_release, changesets)


def create_installxml(dir, changesets):
    xmlfile = os.path.join(dir, 'install.xml')
    root = get_changelogxml(xmlfile)

    for cs in changesets:

        include = etree.Element('include')
        include.set('file', cs.file)
        include.set('relativeToChangelogFile', 'true')
        root.append(include)

    if len(changesets) > 0:
        elem_tag = etree.Element('tagDatabase')
        elem_tag.set('tag', 'install')
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
        masterxml = os.path.join(dir, version, 'master.xml')
        if os.path.exists(masterxml):
            include.set('file', masterxml)
            include.set('relativeToChangelogFile', 'true')
            root.append(include)

    et = etree.ElementTree(root)
    et.write(xmlfile, pretty_print=True)

def update_updatexml(dir, version_xmlfile):
    xmlfile = os.path.join(dir, 'update.xml')
    root = get_changelogxml(xmlfile)

    if os.path.exists(version_xmlfile):
        include.set('file', version_xmlfile)
        include.set('relativeToChangelogFile', 'true')
        root.append(include)

        et = etree.ElementTree(root)
        et.write(xmlfile, pretty_print=True)

def create_versionxml(dir, version, changesets):
    versiondir = os.path.join(dir, version)
    if not os.path.exists(versiondir):
        os.mkdir(versiondir)
    xmlfile = os.path.join(versiondir, 'master.xml')
    root = get_changelogxml(xmlfile)

    for cs in changesets:
        elem = etree.Element('changeSet')
        # move back a directory for relative path
        relative_path = os.path.join('..', cs.file)
        elem.set('file', relative_path)
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
                elem_sqlfile.set('file', relative_path)
                elem_sqlfile.set('relativeToChangelogFile', 'true')
                elem_rb.append(elem_sqlfile)
            elem.append(elem_rb)
        root.append(elem)

    if len(changesets) > 0:
        elem_tag = etree.Element('tagDatabase')
        elem_tag.set('tag', version)
        root.append(elem_tag)
        et = etree.ElementTree(root)
        et.write(xmlfile, pretty_print=True)

        update_updatexml(dir, xmlfile)

def get_changelogxml(xmlfile):
    if os.path.exists(xmlfile):
        changelog = etree.iterparse(xmlfile)
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
