from zss import simple_distance, Node
import xml.etree.ElementTree as ET


def tree_edit_distance(gt_xml, generated_xml):
    gt_tree = ET.parse(gt_xml)
    gen_tree = ET.parse(generated_xml)

    gt_root = gt_tree.getroot()
    gen_root = gen_tree.getroot()

    gt_rootNode = Node(gt_root.attrib)
    gen_rootNode = Node(gen_root.attrib)

    loop(gt_rootNode, gt_root)
    loop(gen_rootNode, gen_root)

    res = simple_distance(gt_rootNode, gen_rootNode)

    return res


def loop(parentNode, parent):

    for child in parent:
        childNode = Node(child.attrib)
        parentNode.addkid(childNode)
        loop(childNode, child)


def get_ted(gt_xml, generated_xml):
    distance = tree_edit_distance(gt_xml, generated_xml)
    return distance
