import csv
from bs4 import BeautifulSoup
import XML_Builder.xml_map



def get_oldxmldata(old_xml):
	nodes = []
	component_list, tree = xml_map.get_component_list(old_xml)
	for node in component_list:
		print(node)


def get_csvdata(csvfile):
	nodes = []
	with open(csvfile) as fileObject:
		readerObject = csv.reader(fileObject)
		for row in readerObject:
			nodes.append(row)

def begin(stored_csv, old_xml):
	csvdata = get_csvdata(stored_csv)
	oldxmldata = get_oldxmldata(old_xml)

