import re
from collections import defaultdict
from datetime import datetime
import json
import codecs
import xml.etree.ElementTree as ET
import pprint
import re

#step3 audit streetname
def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)
            
            
def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(filename):
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    return street_types


def update_name(name, mapping):
    name_list = re.findall(r"[\w#]+", name)
    end_of_street_name = len(name_list)
    
    
    for i in range(len(name_list)):
        word = name_list[i].lower()
        if word in mapping:
            name_list[i] = mapping[word]
        if "#" in word:
            name_list[i] = name_list[i].replace("#","No ")
            name_list = [name_list[i]] + name_list[0:i]
        
    name_list = name_list[:(end_of_street_name+1)]
    better_name = ' '.join(name_list)
    return better_name



def clean_street_name(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    
    for tag in root.findall('*/tag'):
        if is_street_name(tag):
            name = tag.get('v')
            better_name = update_name(name, mapping)
            tag.set('v', better_name)

    return tree


#step4 audit city name
def is_city_name(elem):
    return (elem.attrib['k'] == "addr:city")


def audit_city(filename):
    city_types = set()
    for event, elem in ET.iterparse(filename, events=("start",)):
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_city_name(tag):
                    city_types.add(tag.get('v'))
    return city_types


def update_city_name(name):
    if name in ['BOTHELL','Bothel']:
        better_name = 'Bothell'
    elif name == 'Woodenville':
        better_name = 'Woodinville'
    elif name == 'kenmore':
        better_name = 'Kenmore'
    else:
        better_name = name
    return better_name


def clean_city_name(cleaned_street_name):
    tree = cleaned_street_name
    root = tree.getroot()
    
    for tag in root.findall('*/tag'):
        if is_city_name(tag):
            name = tag.get('v')
            better_name = update_city_name(name)
            tag.set('v', better_name)

    return tree


#step 5 convert osm to json
def shape_element(element):
    lower = re.compile(r'^([a-z]|_)*$')
    lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
    problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
    node = {}
    CREATED = ["version", "changeset", "timestamp", "user", "uid"]
    
    if element.tag == "node" or element.tag == "way" :
        node['type'] = element.tag
        
        # Parse attributes
        for a in element.attrib:
            
            # Parse details of data creation
            if a in CREATED:
                if 'created' not in node:
                    node['created'] = {}
                
                if a == "timestamp":
                    node['created'][a] = str(datetime.strptime(element.attrib[a], '%Y-%m-%dT%H:%M:%SZ').date())
                else:
                    node['created'][a] = element.attrib[a]
    
            # Parse coordinates
            elif a in ['lat', 'lon']:
                if 'pos' not in node:
                    node['pos'] = [None, None]
                
                    if a == 'lat':
                        node['pos'][0] = float(element.attrib[a])
                else:
                        node['pos'][1] = float(element.attrib[a])
            
            else:
                node[a] = element.attrib[a]

        # Iterate tag children
        for tag in element.iter("tag"):
                if not problemchars.search(tag.attrib['k']):
        
                    # Tags with single colon and beginning with addr
                    if lower_colon.search(tag.attrib['k']) and tag.attrib['k'].find('addr') == 0:
                        if 'address' not in node:
                            node['address'] = {}
                    
                        sub_attr = tag.attrib['k'].split(':', 1)
                    
                        node['address'][sub_attr[1]] = tag.attrib['v']
                
                # All other tags that don't begin with "addr"
                elif not tag.attrib['k'].find('addr') == 0:
                    if tag.attrib['k'] not in node:
                        node[tag.attrib['k']] = tag.attrib['v']
                else:
                    node["tag:" + tag.attrib['k']] = tag.attrib['v']
    
        # Iterate nd children building a list
        for nd in element.iter("nd"):
            if 'node_refs' not in node:
                node['node_refs'] = []
            
            node['node_refs'].append(nd.attrib['ref'])

        return node
    else:
        return None






def process_map(file_in, pretty = False):
    file_out = "final.json"
    data = []
    with codecs.open(file_out, "w") as fo:
        for element in file_in.getroot():
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


if __name__ == "__main__":
    filename = 'kenmore.osm'
    street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
    city_name_list = ['Bothell','Edmonds','Kenmore','Kirkland','Lake Forest Park','Mountlake Terrace'
                      ,'Seattle','Shoreline','Woodinville']
    expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
                "Trail", "Parkway", "Commons"]


    mapping = { "pl": "Place",
                "st": "Street",
                "ave": "Avenue",
                "rd": "Road",
                "w": "West",
                "n": "North",
                "s": "South",
                "e": "East",
                "blvd":"Boulevard",
                "sr": "Drive",
                "ct": "Court",
                "ne": "Northeast",
                "se": "Southeast",
                "nw": "Northwest",
                "sw": "Southwest",
                "dr": "Drive",
                "sq": "Square",
                "ln": "Lane",
                "trl": "Trail",
                "pkwy": "Parkway",
                "ste": "Suite",
                "lp": "Loop",
                "hwy": "Highway"}
#do step3 first

    #get street names with problem
    street_types = audit(filename)

    #print those names and there revised name
    for str_type, namel in street_types.iteritems():
        for name in namel:
            better_name = update_name(name, mapping)
            if name != better_name:
                print name, " => ", better_name
    #clean the names and saved to a new filw
    cleaned_street_name = clean_street_name(filename)

#then, do step4
    city_type = audit_city(filename)
    cleaned_city_name = clean_city_name(cleaned_street_name)

#process step 5
    process_map(cleaned_city_name)

