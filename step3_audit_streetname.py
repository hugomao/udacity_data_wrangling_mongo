import re
from collections import defaultdict


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



def clean_street_name(filename, cleaned_filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    
    for tag in root.findall('*/tag'):
        if is_street_name(tag):
            name = tag.get('v')
            better_name = update_name(name, mapping)
            tag.set('v', better_name)

    return tree.write(cleaned_filename)




if __name__ == "__main__":
    filename = 'kenmore.osm'
    street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


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

    #get street names with problem
    street_types = audit(filename)

    #print those names and there revised name
    for str_type, namel in street_types.iteritems():
        for name in namel:
            better_name = update_name(name, mapping)
            if name != better_name:
                print name, " => ", better_name
    #clean the names and saved to a new filw
    cleaned_street_name = 'kenmore_updated_street.xml'
    clean_street_name(filename, cleaned_street_name)
