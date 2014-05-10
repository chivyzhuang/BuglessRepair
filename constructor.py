#! /usr/bin/python
import os
import sys


BASE_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(BASE_DIR, "lib"))


import repairmanifest_pb2
import string


# global variables
VERSION = "Version 1.3"
MANIFEST_DIR = os.path.join(BASE_DIR, "manifest")
EXEC_DIR = os.path.join(BASE_DIR, "exec")
RAW_DIR = os.path.join(BASE_DIR, "raw")
RET_DIR = os.path.join(BASE_DIR, "result")
DEFAULT_MANIFEST_FILE_NAME = "manifest_default"
DEFAULT_REPAIR_PACKAGE_FILE_NAME = "RepairPackage"


# Delete files and folders
def removeFile(src):
  if os.path.isfile(src):
    try:
      os.remove(src)
    except:
      return False
  elif os.path.isdir(src):
    for item in os.listdir(src):
      itemsrc = os.path.join(src, item)
      if not removeFile(itemsrc):
        return False
    try:
      os.rmdir(src)
    except:
      return False
  return True


# initial directory structure
def opInit():
  if not os.path.exists(EXEC_DIR):
    os.mkdir(EXEC_DIR)
  if not os.path.exists(MANIFEST_DIR):
    os.mkdir(MANIFEST_DIR)
  if not os.path.exists(RET_DIR):
    os.mkdir(RET_DIR)
  if not os.path.exists(RAW_DIR):
    os.mkdir(RAW_DIR)


# show the content of manifest file
def showManifest(file_name):
  # find path
  manifest_path = os.path.join(MANIFEST_DIR, file_name)
  # check if it's exist
  if not os.path.exists(manifest_path):
    a, b = os.path.split(manifest_path)
    print "Manifest file '%s' can't be found in directory '%s'." % (b, a)
    sys.exit(-1)
  # show it
  exec_case = repairmanifest_pb2.ExecCase()
  try:
    f = open(manifest_path, "rb")
    exec_case.ParseFromString(f.read())
    f.close()
  except IOError:
    print "Can't read manifest file. IOError!"
    sys.exit(-1)
  print "Content of manifest file '%s'" % file_name
  print "================================================================================"
  type_name_mapping = {
    repairmanifest_pb2.Exec.BIN: "Binary File",
    repairmanifest_pb2.Exec.SHELL: "Shell Script",
    repairmanifest_pb2.Exec.DEX: "Dex File"
  }
  position = 0
  for item in exec_case.execs:
    position += 1
    print "Step %d:" % position
    print "  ", "File Name: ", item.file_name
    print "  ", "Type: ", type_name_mapping.get(item.type)
    print "  ", "Will Affect After: ", item.affect_after
    if item.verification_code != "":
      print "  ", "Success Result: ", item.verification_code
    print "--------------------------------------------------------------------------------"
  return position


def listDirExecptHiddenFile(dir_path):
  return [file_name for file_name in os.listdir(dir_path) if file_name[0] != '.']


def showAvaiableExecFiles():
  # raw dir can not be empty
  file_list = listDirExecptHiddenFile(EXEC_DIR)
  file_num = len(file_list)
  if file_num == 0:
    print "There is not file in %s." % EXEC_DIR
    return False
  i = 0
  for filename in file_list:
    i += 1
    print '%d. ' % i, filename
  return True


def addExec(interactive, file_name, target):
  if interactive:
    while showAvaiableExecFiles():
      print "Choose one file, e.g.'1' and you can input 'quit', press Ctrl-D or Ctrl-C to exit. "
      try:
        index = raw_input('>>')
        if index.isdigit():
          index = string.atoi(index)
          file_list = listDirExecptHiddenFile(EXEC_DIR)
          if index < 1 or index > len(file_list):
            print "Error input." 
          else:
            addExecDetail(file_list[index-1], target)
        else:
          if index == "quit":
            print "Bye."
            break
          else:
            print "Error input."
      except (IOError, EOFError, KeyboardInterrupt):
        print "\n", "Bye."
        break
  else:
    if not file_name:
      print "You must specify the exec file name(use -f) or use -i to add exec file in interactive mode."
      sys.exit(-1)
    addExecDetail(file_name, target)


def addExecDetail(file_name, target):
  # file must be exist
  file_path = os.path.join(EXEC_DIR, file_name)
  if not os.path.exists(file_path):
    a, b = os.path.split(file_path)
    print "File '%s' can't be found in directory '%s'." % (b, a)
    return
  # Read the existing manifest
  exec_case = repairmanifest_pb2.ExecCase()
  manifest_path = os.path.join(MANIFEST_DIR, target)
  try:
    f = open(manifest_path, "rb")
    exec_case.ParseFromString(f.read())
    f.close()
  except IOError:
    print target + ": Manifest file not found. Creating new one."
  # prompt input
  item = exec_case.execs.add()
  # name
  item.file_name = file_name
  # type
  type = raw_input("Is this a binary(input 'b'), shell script(input 's'), or dex file(input 'd')?\n")
  if type == "b":
    item.type = repairmanifest_pb2.Exec.BIN
  elif type == "s":
    item.type = repairmanifest_pb2.Exec.SHELL
  elif type == "d":
    item.type = repairmanifest_pb2.Exec.DEX
  else:
    print "Unknown file type. Try again."
    return
  # affect after
  ret = raw_input("Will it affect the result of next exec file?(y/n and leave blank will default set 'n')?\n") 
  if ret == 'y':
    item.affect_after = True
  elif ret == 'n':
    item.affect_after = False
  elif ret == "":
    item.affect_after = False
  else:
    print "Unknown input. Try again."
    return
  # verification_code
  if type != "d":
    item.verification_code = raw_input("Enter a result string after execution for verifing whether the execution succeeds(or leave blank to finish):\n")
  # Write the new manifest back to disk.
  f = open(manifest_path, "wb")
  f.write(exec_case.SerializeToString())
  f.close()


def createPackage(archive_name, manifest_name):
  # read manifest
  exec_case = repairmanifest_pb2.ExecCase()
  manifest_path = os.path.join(MANIFEST_DIR, manifest_name)
  try:
    f = open(manifest_path, "rb")
    exec_case.ParseFromString(f.read())
    f.close()
  except IOError:
    print manifest_name + ": Manifest file not found."
    sys.exit(-1)
  # add files
  import zipfile
  archive_path = os.path.join(RET_DIR, archive_name)
  if os.path.isdir(archive_path):
    removeFile(archive_path)
  f = zipfile.ZipFile(archive_path,'w', zipfile.ZIP_DEFLATED)
  print "Writing manifest..."
  f.write(manifest_path, 'manifest')
  print "Writing exec files..."
  i = 0
  for item in exec_case.execs:
    i += 1
    print "(%d/%d)Writing %s..." % (i, len(exec_case.execs), item.file_name)
    f.write(os.path.join(EXEC_DIR, item.file_name), item.file_name)
  file_list = listDirExecptHiddenFile(RAW_DIR)
  file_num = len(file_list)
  if file_num != 0:
    print "Writing raw files..."
    i = 0
    for filename in file_list:
      i += 1
      print "(%d/%d)Writing %s..." % (i, file_num, filename)
      f.write(os.path.join(RAW_DIR, filename), "raw/" + filename)
  f.close()
  print "Finish."
  from hashlib import md5
  m = md5()
  src_file = open(archive_path, 'rb')
  m.update(src_file.read())
  src_file.close()
  print "md5:", m.hexdigest()


def removeExec(manifest_name):
  # find path
  manifest_path = os.path.join(MANIFEST_DIR, manifest_name)
  while showManifest(manifest_name) > 0:
    # show it
    exec_case = repairmanifest_pb2.ExecCase()
    try:
      f = open(manifest_path, "rb")
      exec_case.ParseFromString(f.read())
      f.close()
    except IOError:
      sys.exit(-1)
    print "Choose one step to remove, e.g.'1' and you can input 'quit', press Ctrl-D or Ctrl-C to exit. "
    try:
      index = raw_input('>>')
      if index.isdigit():
        index = string.atoi(index)
        if index < 1 or index > len(exec_case.execs):
          print "Error input." 
        else:
          del exec_case.execs[index-1]
      else:
        if index == "quit":
          print "Bye."
          sys.exit(0)
        else:
          print "Error input."
    except (IOError, EOFError, KeyboardInterrupt):
      print "\n", "Bye."
      sys.exit(0)
    # Write the new manifest back to disk.
    f = open(manifest_path, "wb")
    f.write(exec_case.SerializeToString())
    f.close()
  print "There is no content in manifest '%s'" % manifest_name


def parse_args():
  import argparse
  parser = argparse.ArgumentParser(version=VERSION, description="Used for construct repair package of 'Bugless'.")
  subparsers = parser.add_subparsers()
  subparsers.add_parser('init', help='initial directory structure')
  parser_create = subparsers.add_parser('create', help='create repair package(zip) according to manifest file')
  parser_create.add_argument("-f","--file", help="specifiy the repair package(zip) file name", default=DEFAULT_REPAIR_PACKAGE_FILE_NAME)
  parser_create.add_argument("-m","--manifest", help="specify the manifest file, default is '%s'" % DEFAULT_MANIFEST_FILE_NAME, default=DEFAULT_MANIFEST_FILE_NAME)
  parser_show = subparsers.add_parser('show', help='show content of the manifest file')
  parser_show.add_argument("-m","--manifest", help="specify the manifest file, default is '%s'" % DEFAULT_MANIFEST_FILE_NAME, default=DEFAULT_MANIFEST_FILE_NAME)
  parser_add = subparsers.add_parser('add', help='add exec file')
  parser_add.add_argument('-i', "--interactive", help='interactive mode', action='store_true')
  parser_add.add_argument("-f","--file", help="specify the file that will be add to repair package.")
  parser_add.add_argument("-m","--manifest", help="specify the manifest file, default is '%s'" % DEFAULT_MANIFEST_FILE_NAME, default=DEFAULT_MANIFEST_FILE_NAME)
  parser_remove = subparsers.add_parser('remove', help='remove exec file')
  parser_remove.add_argument("-m","--manifest", help="specify the manifest file, default is '%s'" % DEFAULT_MANIFEST_FILE_NAME, default=DEFAULT_MANIFEST_FILE_NAME)
  return parser.parse_args()


# Main procedure
args = parse_args()
# process
if sys.argv[1] == 'init':
  opInit()
elif sys.argv[1] == 'create':
  createPackage(args.file, args.manifest)
elif sys.argv[1] == 'show':
  showManifest(args.manifest)
elif sys.argv[1] == 'add':
  addExec(args.interactive, args.file, args.manifest)
elif sys.argv[1] == 'remove':
  removeExec(args.manifest)