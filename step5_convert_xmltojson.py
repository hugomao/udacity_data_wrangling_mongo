from datetime import datetime
import json
import codecs 

def shape_element(element):
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
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data


if __name__ == "__main__":
    process_map(cleaned_city_name)
