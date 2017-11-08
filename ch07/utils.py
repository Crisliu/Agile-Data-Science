import sys, os, re
import json
import codecs



#
# Utility functions to read and write json and jsonl files
#
def write_json_file(obj, path):
  '''Dump an object and write it out as json to a file.'''
  f = codecs.open(path, 'w', 'utf-8')
  f.write(json.dumps(obj, ensure_ascii=False))
  f.close()

def write_json_lines_file(ary_of_objects, path):
  '''Dump a list of objects out as a json lines file.'''
  f = codecs.open(path, 'w', 'utf-8')
  for row_object in ary_of_objects:
    json_record = json.dumps(row_object, ensure_ascii=False)
    f.write(json_record + "\n")
  f.close()

def read_json_file(path):
  '''Turn a normal json file (no CRs per record) into an object.'''
  text = codecs.open(path, 'r', 'utf-8').read()
  return json.loads(text)

def read_json_lines_file(path):
  '''Turn a json cr file (CRs per record) into an array of objects'''
  ary = []
  f = codecs.open(path, "r", "utf-8")
  for line in f:
    record = json.loads(line.rstrip("\n|\r"))
    ary.append(record)
  return ary