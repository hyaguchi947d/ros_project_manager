#!/usr/bin/env python

import sys
import rospy
import rospkg

import xml.etree.ElementTree as ET

import re

if __name__ == '__main__':
  argv = rospy.myargv(argv = sys.argv)
  if len(argv) < 2:
    print 'usage: package_parser.py PACKAGE'
    quit()

  rospack = rospkg.RosPack()
  pack_path = ''
  try:
    pack_path = rospack.get_path(sys.argv[1])
  except(rospkg.common.ResourceNotFound):
    print 'error: ' + sys.argv[1] + ' :unknown pacakge'
    quit()

  # xml parse
  tree = ET.parse(pack_path + '/package.xml')
  root = tree.getroot()

  # root tag
  pack_version = ''
  try:
    pack_version = root.attrib['format']
  except(KeyError):
    pass

  if pack_version == '2':
    print 'package xml == v2'
  else:
    print 'package version is not v2 or not defined'

  # header information
  name = root.find('name').text
  if name != sys.argv[1]:
    print 'mismatch package name?: ' + name
    quit()
  else:
    print 'package: ' + name

  version = root.find('version').text
  print 'version: ' + version

  description = root.find('description').text
  print 'description: ' + description

  maintainer_elem = root.find('maintainer')
  email = maintainer_elem.attrib['email']
  maintainer = maintainer_elem.text
  print 'maintainer: ' + maintainer + ' <' + email + '>'

  license = root.find('license').text
  print 'license: ' + license

  # buildtool_depend
  buildtool_depend = root.find('buildtool_depend')
  print 'buildtool_depend: ' + buildtool_depend.text

  # dependencies
  dependencies = {}
  if pack_version == '2':
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
    for depend_elem in root.findall(depend_type):
      item = depend_elem.text
      print depend_type + ': ' + item
      if not dependencies.has_key(item):
        dependencies[item] = {}
      for depend_flag in depend_types[depend_type]:
        dependencies[item][depend_flag] = True
  print dependencies


  # cmake parse
  command_list = []
  comment_pat = re.compile(r'(?P<bd>.*)(?:\#)')
  cmd_pat = re.compile(r'(?P<cmd>.*)(?:\()(?P<left>.*)')
  close_pat = re.compile(r'(?P<bd>.*)(?:.*)\)')
  current_cmd = None
  with open(pack_path + '/CMakeLists.txt', 'r') as cmakelists:
    for line in cmakelists:
      current_line = line.rstrip().lstrip()
      # erase comment
      res = comment_pat.match(current_line)
      if res:
        current_line = res.group('bd').rstrip()

      # command
      res = cmd_pat.match(current_line)
      if res:
        current_cmd = (
          {'command': res.group('cmd').strip(),
           'attrib' : []}) 
        current_line = res.group('left').rstrip()

      # closing brace
      res = close_pat.match(current_line)
      if res:
        current_line = res.group('bd')

      # split with wspace
      for item in current_line.split():
        current_cmd['attrib'].append(item)

      # close brace
      if res:
        command_list.append(current_cmd)
        current_cmd = None
  cmakelists.closed
  print command_list