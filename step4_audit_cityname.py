import re
from collections import defaultdict


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


def clean_city_name(filename, cleaned_filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    
    for tag in root.findall('*/tag'):
        if is_city_name(tag):
            name = tag.get('v')
            better_name = update_city_name(name)
            tag.set('v', better_name)

    return tree.write(cleaned_filename)




if __name__ == "__main__":
    filename = 'kenmore.osm'
    city_name_list = ['Bothell','Edmonds','Kenmore','Kirkland','Lake Forest Park','Mountlake Terrace'
                         ,'Seattle','Shoreline','Woodinville']

    city_type = audit_city(filename)
    cleaned_city_name = 'kenmore_updated_streetcity.xml'
    clean_city_name(cleaned_street_name, cleaned_city_name)
