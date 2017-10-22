import xml.etree.ElementTree as ET
import pprint
import re


"""
Before adding it to Mongodb, we need to check if there're any data quality
issues in there. I will parse through it with ElementTree and start with
counting different elements.
"""
def count_tag(filename):
    tags = {}
    for event, elem in ET.iterparse(filename):
        if elem.tag in tags:
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
    pprint.pprint(tags)  


"""
looped through all tag keys and printed them.
"""
def audit_tag_keys(filename):
        keys_dict = {}
        for event, elem in ET.iterparse(filename):
            for attr in elem.iter("tag"):
                key = attr.attrib["k"]

                if key not in keys_dict:
                    keys_dict[key] = 1
                else:
                    keys_dict[key] += 1

        return keys_dict



"""
Finally, i also audited if there're any problematic tag keys that are not
available Mongodb, i printed number of keys for each type and found no
problematic keys.
"""
def key_type(element, keys):
    if element.tag == "tag":
        
        if problemchars.search(element.attrib['k']):
            keys['problemchars'] += 1
        elif lower.search(element.attrib['k']):
            keys['lower'] += 1
        elif lower_colon.search(element.attrib['k']):
            keys['lower_colon'] += 1 
        else:
            keys['other'] += 1
        
    return keys

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys



if __name__ == "__main__":
    filename = "kenmore.osm"
    count_tag(filename)

    tag_key = audit_tag_keys(filename)
    sorted(tag_key.items(), key=lambda x: (-x[1], x[0]))

    lower = re.compile(r'^([a-z]|_)*$')
    lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
    problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

    keys = process_map(filename)
    pprint.pprint(keys)
