#!/usr/bin/python

import os
import sys
from lxml import etree
import utils

def create_changelog(dir, sqldir):
    changesets = utils.get_changesets(dir)
    if len(changesets) == 0:
        print('No sql file changes detected in %s' % dir)
        return

    installxml = os.path.join(sqldir, 'install.xml')
    #if utils.get_last_release is None or not os.path.exists(installxml) or
    if utils.is_new_file(dir, installxml):
        create_installxml(dir, changesets)
    else:
        #if not os.path.exists(os.path.join(dir, 'update.xml')):
        #    create_updatexml(dir)
        next_release = utils.get_next_release(dir)
        print(next_release)
        create_versionxml(dir, sqldir, next_release, changesets)

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

    if os.path.exists(xmlfile):
        os.remove(xmlfile)

    root = get_changelogxml(xmlfile)

    include = etree.Element('include')
    include.set('file', 'install.xml')
    include.set('relativeToChangelogFile', 'true')
    root.append(include)

    for version in utils.get_directory_versions(dir):
        include = etree.Element('include')
        masterxml = os.path.join(version, 'master.xml')
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

        #for elem in tree.xpath("//div[@id='slider1']")::

        include.set('file', version_xmlfile)
        include.set('relativeToChangelogFile', 'true')
        root.append(include)

        et = etree.ElementTree(root)
        et.write(xmlfile, pretty_print=True)

def create_versionxml(dir, sqldir, version, changesets):
    versiondir = os.path.join(dir, version)
    if not os.path.exists(versiondir):
        os.mkdir(versiondir)
    xmlfile = os.path.join(versiondir, 'master.xml')
    if os.path.exists(xmlfile):
        os.remove(xmlfile)
    root = get_changelogxml(xmlfile)

    for cs in changesets:
        elem_cs = etree.Element('changeSet')
        if cs.location == 'latest':
            # move back a directory for relative path
            relative_path = os.path.join('..', cs.file)
        else:
            # take off the version directory
            relative_path = cs.file[len(version) + 1:]
        elem_sf = etree.Element('sqlFile')
        elem_sf.set('file', relative_path)
        elem_sf.set('relativeToChangelogFile', 'true')
        elem_cs.append(elem_sf)

        # rollback element
        elem_rb = etree.Element('rollback')
        if utils.is_new_file(dir, os.path.join(sqldir, cs.file)):
            # if this is a new file then rollback is to drop
            if cs.type in ['package', 'trigger', 'view', 'table', 'procedure']:
                elem_rb.text = 'drop %s %s;' % (self.type, self.fullname)
        else:
            # for a latest object we can automatically create the rollback
            # by either droping or reverting the file to previous version
            if cs.location == 'latest':
                # rollback to a particular version of the file
                # use git checkout <tag> <filename> to revert this file
                elem_sqlfile = etree.Element('sqlFile')
                elem_sqlfile.set('file', relative_path)
                elem_sqlfile.set('relativeToChangelogFile', 'true')
                elem_rb.append(elem_sqlfile)
        elem_cs.append(elem_rb)

        root.append(elem_cs)

    if len(changesets) > 0:
        elem_tag = etree.Element('tagDatabase')
        elem_tag.set('tag', version)
        root.append(elem_tag)
        et = etree.ElementTree(root)
        et.write(xmlfile, pretty_print=True)

        create_updatexml(dir)

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
