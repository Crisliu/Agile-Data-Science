import sys, os, re
sys.path.append("lib")
import utils

import wikipedia
from bs4 import BeautifulSoup
import tldextract
import codecs
import json


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
  return ary

# Load our airlines...
our_airlines = read_json_lines_file('data/our_airlines.jsonl')

# Build a new list that includes wikipedia data
with_url = []
for airline in our_airlines:
  # Get the wikipedia page for the airline name
  wikipage = wikipedia.page(airline['Name'])

  # Get the summary
  summary = wikipage.summary
  airline['summary'] = summary

  # Get the HTML of the page
  page = BeautifulSoup(wikipage.html())

  # Task: get the logo from the right 'vcard' column
  # 1) Get the vcard table
  vcard_table = page.find_all('table', class_='vcard')[0]
  # 2) The logo is always the first image inside this table
  first_image = vcard_table.find_all('img')[0]
  # 3) Set the url to the image
  logo_url = 'http:' + first_image.get('src')
  airline['logo_url'] = logo_url

  # Task: Get the company website
  # 1) Find the 'Website' table header
  th = page.find_all('th', text='Website')[0]
  # 2) find the parent tr element
  tr = th.parent
  # 3) find the a (link) tag within the tr
  a = tr.find_all('a')[0]
  # 4) finally get the href of the a tag
  url = a.get('href')
  airline['url'] = url

  # Get the domain to display with the url
  url_parts = tldextract.extract(url)
  airline['domain'] = url_parts.domain + '.' + url_parts.suffix

  with_url.append(airline)

utils.write_json_lines_file(with_url, 'data/our_airlines_with_wiki.jsonl')

