from config import *
import xml.etree.ElementTree as ET
import csv

import pprint
pp = pprint.PrettyPrinter()

def generate_xml(filename,root_directory,tv):
    new_xml_dict = {}
    hierarchy = None

    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            # print(len(row))
            if line_count == 0:
                #print(f'{row[1]} {row[2]} {row[3]} {row[12]}')
                line_count += 1
            else:
                #print(f'{row[1]} {row[2]} {row[3]} {row[13]}')
                line_count += 1

                xml_level = row[1]
                xml_index = row[2]
                parent_location = row[3][1:-1]
                new_attributes = row[12]

                # xml level
                if xml_level not in new_xml_dict.keys():
                    new_xml_dict[xml_level] = {}
                # xml index under xml level
                new_xml_dict[xml_level][xml_index] = {}
                new_xml_dict[xml_level][xml_index]['parent_location'] = {}

                # parent location
                if(parent_location != ''):
                    parent_location_tuple = eval(parent_location)
                    new_xml_dict[xml_level][xml_index]['parent_location']['parent_xml_level'] = parent_location_tuple[0]
                    new_xml_dict[xml_level][xml_index]['parent_location']['parent_xml_index'] = parent_location_tuple[1]
                else:
                    new_xml_dict[xml_level][xml_index]['parent_location']['parent_xml_level'] = ''
                    new_xml_dict[xml_level][xml_index]['parent_location']['parent_xml_index'] = ''

                # new_attributes
                if(new_attributes != ''):
                    new_xml_dict[xml_level][xml_index]['new_attributes'] = eval(new_attributes)
                else:
                    new_xml_dict[xml_level][xml_index]['new_attributes'] = new_attributes

                # location
                if(xml_level == '0'):
                    hierarchy = ET.Element('hierarchy')
                    hierarchy.set('rotation', '0')
                    new_xml_dict[xml_level][xml_index]['location'] = hierarchy
                else:
                    parent_xml_level = new_xml_dict[xml_level][xml_index]['parent_location']['parent_xml_level']
                    if(parent_xml_level == 0):
                        parent_location_ref = new_xml_dict[str(parent_xml_level)]['0']['location']
                    else:
                        parent_xml_index = new_xml_dict[xml_level][xml_index]['parent_location']['parent_xml_index']
                        parent_location_ref = new_xml_dict[str(parent_xml_level)][str(parent_xml_index)]['location']
                    node = ET.SubElement(parent_location_ref, 'node', attrib = new_xml_dict[xml_level][xml_index]['new_attributes'])
                    # node.set('index', xml_index)
                    new_xml_dict[xml_level][xml_index]['location'] = node

    # pp.pprint(new_xml_dict)
    # create a new XML file with the results
    myfile = open(root_directory+"["+str(tv)+"]_dynamic.xml", "w")
    myfile.write("<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>")
    myfile.close()
    myfile = open(root_directory+"["+str(tv)+"]_dynamic.xml", "ab")
    mydata = ET.tostring(hierarchy)
    myfile.write(mydata)
    myfile.close()


