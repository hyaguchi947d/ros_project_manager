#!/usr/bin/env python

import xml.etree.ElementTree as ET

class PackageXmlParser:
  def __init__(self):
    self.root = ET.Element('package')
    self.pack_version = '2'


  def parse(self, filename):
    # xml parse
    tree = ET.parse(filename)
    self.root = tree.getroot()

    # root tag
    self.pack_version = ''
    try:
      self.pack_version = self.root.attrib['format']
    except(KeyError):
      pass

    if self.pack_version == '2':
      print 'package xml == v2'
    else:
      print 'package version is not v2 or not defined'

    # header information
    self.name = self.root.find('name').text
    print 'package: ' + self.name

    self.version = self.root.find('version').text
    print 'version: ' + self.version

    self.description = self.root.find('description').text
    print 'description: ' + self.description

    maintainer_elem = self.root.find('maintainer')
    self.email = maintainer_elem.attrib['email']
    self.maintainer = maintainer_elem.text
    print 'maintainer: ' + self.maintainer + ' <' + self.email + '>'

    self.license = self.root.find('license').text
    print 'license: ' + self.license

    # buildtool_depend
    self.buildtool_depend = self.root.find('buildtool_depend').text
    print 'buildtool_depend: ' + self.buildtool_depend

    # dependencies
    self.dependencies = {}
    if self.pack_version == '2':
      # depend = exec + build + build_export
      # build_depend
      # build_export_depend
      # exec_depend
      # test_depend
      # doc_depend
      depend_types = ({
        'depend': ['build', 'build_export', 'exec'],
        'build_depend': ['build'],
        'build_export_depend': ['build_export'],
        'exec_depend': ['exec'],
        'test_depend': ['test'],
        'doc_depend': ['doc'],
      })
    else:
      # build_depend
      # run_depend
      # test_depend
      depend_types = ({
        'build_depend': ['build'],
        'run_depend': ['exec'],
        'test_depend': ['test'],
      })

    for depend_type in depend_types.keys():
      for depend_elem in self.root.findall(depend_type):
        item = depend_elem.text
        print depend_type + ': ' + item
        if not self.dependencies.has_key(item):
          self.dependencies[item] = {}
        for depend_flag in depend_types[depend_type]:
          self.dependencies[item][depend_flag] = True
    print self.dependencies