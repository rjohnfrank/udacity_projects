###
###
### audit.py 
###
### This code is a modified version of my answer to:
###
### LESSON 13, QUIZ 10: Improving Street Names 
###
###

#!/usr/bin/env python
# -*- coding: utf-8 -*-


import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint


# The sample file is used here because the original file is too large for upload
OSMFILE = "./osm_files/sample.osm" 
# PLEASE NOTE: using the sample file, the vegan cuisine audit produces no results, due to a lack of vegan tags
# However, the audit function can be tested by replacing "vegan" with "pizza" in (tag.attrib['v'] == "vegan") 


EXPECTED = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Alley", "Broadway", "East", "West", "North", "South", 
            "Pike", "Plaza", "Terrace", "Center", "Circle", "Green", "Highway", "Walk", "Way"]

def audit_street_types(osmfile):
    osm_file = open(osmfile, "r")
    # the street_types dictionary uses the street types as keys and street names as values
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        # go through all node and way tags, including their child tags 
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                # if the tag key indicates a street name, then audit the street type
                if tag.attrib['k'] == "addr:street":
                    # first find the street name from the tag value
                    street_name = tag.attrib['v']
                    # then use the regular expression module to find the last word 
                    street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
                    m = street_type_re.search(street_name)
                    if m:
                        # the street type will be the last word 
                        street_type = m.group()
                        # if the street type is not one of the expected types,
                        # then add it to the dictionary of street types, where the value is the street name 
                        if street_type not in EXPECTED:
                            street_types[street_type].add(street_name)                    
    osm_file.close()
    return street_types


def audit_cuisines(osmfile):
    osm_file = open(osmfile, "r")
    # the cuisine_types set is a collection of the different cuisine types 
    cuisine_types = set()
    for event, elem in ET.iterparse(osm_file, events=("start",)):
    # go through all node and way tags, including their child tags 
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter('tag'):
                # set the boolean below to print only if the elem has a "cuisine:vegan" tag
                print_elem = False 
                # if the tag is "cuisine:vegan" then change the boolean to True 
                if (tag.attrib['k'] == "cuisine") and (tag.attrib['v'] == "vegan"):
                    cuisine_types.add(tag.attrib['v'])
                    print_elem = True
                # when a "cuisine:vegan" tag is found, the entire element is printed
                if print_elem:
                    print elem
                    # print all of the tags within the element 
                    for vegan_tag in elem.iter('tag'):
                        print vegan_tag.attrib['k'], vegan_tag.attrib['v']
    osm_file.close()
    return cuisine_types


def test():
    
    # audit street types 
    st_types = audit_street_types(OSMFILE)
    print 'Street Types:'
    pprint.pprint(dict(st_types))
    
    # audit cuisines
    print 'Cuisines:'
    cuisines = audit_cuisines(OSMFILE)

if __name__ == '__main__':
    test()
