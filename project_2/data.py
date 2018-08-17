###
###
### data.py 
###
### This code is a modified version of my answer to:
###
### LESSON 13, QUIZ 10: Preparing for Database - SQL 
###
###

#!/usr/bin/env python
# -*- coding: utf-8 -*-


import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
from collections import defaultdict
import cerberus
import schema


OSM_PATH = "./osm_files/sample.osm" 


NODES_PATH = "./csv_files/nodes.csv"
NODE_TAGS_PATH = "./csv_files/nodes_tags.csv"
WAYS_PATH = "./csv_files/ways.csv"
WAY_NODES_PATH = "./csv_files/ways_nodes.csv"
WAY_TAGS_PATH = "./csv_files/ways_tags.csv"


LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


SCHEMA = schema.schema


# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


MAPPING = { "Ave": "Avenue","Ave.": "Avenue","ave": "Avenue",
            "Blvd": "Boulevard","Blvd.":"Boulevard","blvd": "Boulevard",
            "Dr": "Drive",
            "E": "East","W": "West",
            "Ln": "Lane","Ln.": "Lane",
            "Rd": "Road","Rd.": "Road","rd": "Road",
            "St": "Street","St.": "Street","Atreet": "Street","Sstreet": "Street","Steet": "Street",
            "ST": "Street","st": "Street","street": "Street","StreetPhiladelphia": "Street",
            }


def clean_street_name(street_name, mapping=MAPPING):
    street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type in mapping.keys():
            street_name = re.sub(m.group(), mapping[m.group()], street_name)
    return street_name 

def clean_vegan(the_key, the_value):
    # this function could be expanded to include other cuisine or diet tags 
    if the_key == 'cuisine' and the_value == 'vegan':
        # set the type/key/value 
        the_type = 'diet'
        the_key = 'vegan'
        the_value = 'only' 
        print "Flipped a cuisine=vegan to diet:vegan=only"
    if the_key == 'diet:vegan':
        the_type = 'regular'
        the_key = 'cuisine'
        the_value = 'vegan'
        print "Flipped a diet:vegan=only to a cuisine=vegan"

    return the_type, the_key, the_value 


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    if element.tag == 'node':
        node_id = element.attrib['id']

        # get all of the field data from the node element 
        for field in node_attr_fields:
            node_attribs[field] = element.get(field)

        # if this variable becomes true, then the diet:vegan tag is changed to cuisine to prevent duplicates
        flip_vegan = False 
            
        # go through the node tags 
        for tag in element.iter('tag'):
            ntag = {}
            ntag['id'] = node_id
            ntag['value'] = tag.attrib['v']
            
            # if the 'k' value contains any problematic characters, then skip the tag 
            if re.search(PROBLEMCHARS, tag.attrib['k']):
                continue 
                
            # if the tag "k" value contains a ":" 
            # then the characters before the ":" should be set as the tag type
            # and the characters after the ":" should be set as the tag key
            elif re.search(LOWER_COLON, tag.attrib['k']):
                colon = tag.attrib['k'].find(':')
                ntag['type'] = tag.attrib['k'][:colon]
                ntag['key'] = tag.attrib['k'][colon+1:]
               
                # CLEAN: street types
                if tag.attrib['k'] == 'addr:street':
                    if clean_street_name(tag.attrib['v']):
                        ntag['value'] = clean_street_name(tag.attrib['v'])  
                        
                # CLEAN: flip any duplicate diet:vegan tags to cuisine 
                if (ntag['type'] == 'diet') and (ntag['key'] == 'vegan') and flip_vegan:
                    ntag['type'], ntag['key'], ntag['value'] = clean_vegan(tag.attrib['k'],tag.attrib['v'])
                    print ntag 
                
            else:
                ntag['type'] = 'regular'
                ntag['key'] = tag.attrib['k']
               
                # CLEAN: cuisine to diet 
                if tag.attrib['k'] == 'cuisine' and tag.attrib['v'] == 'vegan':
                    ntag['type'], ntag['key'], ntag['value'] = clean_vegan(tag.attrib['k'],tag.attrib['v'])
                    print ntag   
                    # change any remaining diet:vegan tag to cuisine in order to avoid duplicates 
                    flip_vegan = True 
            tags.append(ntag)

        return {'node': node_attribs, 'node_tags': tags}

    elif element.tag == 'way':
        way_id = element.attrib['id']

        # get all of the field data from the way element 
        for field in way_attr_fields:
            way_attribs[field] = element.get(field)
            
        # go through the way tags 
        for tag in element.iter('tag'):
            wtag = {}
            wtag['id'] = way_id
            wtag['value'] = tag.attrib['v']
            # if the tag "k" value contains a ":" 
            # then the characters before the ":" should be set as the tag type
            # and the characters after the ":" should be set as the tag key
            k = tag.attrib['k']
            if re.search(LOWER_COLON, k):
                colon = k.find(':')
                wtag['type'] = tag.attrib['k'][:colon]
                wtag['key'] = tag.attrib['k'][colon+1:]
                
                # CLEAN: street types
                if tag.attrib['k'] == 'addr:street':
                    if clean_street_name(tag.attrib['v']):
                        wtag['value'] = clean_street_name(tag.attrib['v'])  
                    
            else:
                wtag['type'] = 'regular'
                wtag['key'] = tag.attrib['k']

            tags.append(wtag)
            
        # go through the way nodes 
        position = 0 
        for tag in element.iter('nd'):
            wnode = {}
            wnode['id'] = way_id
            wnode['node_id'] = tag.attrib['ref']
            wnode['position'] = position 
            position += 1 
            way_nodes.append(wnode)
            
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}




# ================================================== #
#               Helper Functions                     #
# ================================================== #
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the map when validating.
    process_map(OSM_PATH, validate=True)