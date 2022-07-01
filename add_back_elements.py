import os
import glob
from collections import defaultdict
from tqdm import tqdm
import lxml.etree as ET
from acdh_tei_pyutils.tei import TeiReader

all_ent_nodes = {}
doc = TeiReader('./data/indices/listperson.xml')
ent_nodes = doc.any_xpath('.//tei:body//*[@xml:id]')
for ent in ent_nodes:
    all_ent_nodes[ent.xpath('@xml:id')[0]] = ent

files = sorted(glob.glob('./data/editions/*.xml'))
for x in tqdm(files):
    try:
        doc = TeiReader(x)
        root_node = doc.any_xpath('.//tei:text')[0]
        for bad in doc.any_xpath('.//tei:back'):
            bad.getparent().remove(bad)
        refs = doc.any_xpath('.//tei:body//tei:name[@ref]/@ref')
        ent_dict = defaultdict(list)
        for ref in set(refs):
            # print(ref, type(ref))
            if ref.startswith('#'):
                ent_id = ref[1:]
            else:
                ent_id = ref
            try:
                index_ent = all_ent_nodes[ent_id]
                ent_dict[index_ent.tag].append(index_ent)
            except KeyError:
                continue
        back_node = ET.Element("{http://www.tei-c.org/ns/1.0}back")
        for key in ent_dict.keys():
            if key.endswith('person'):
                list_person = ET.Element("{http://www.tei-c.org/ns/1.0}listPerson")
                back_node.append(list_person)
                for ent in ent_dict[key]:
                    list_person.append(ent)
            if key.endswith('place'):
                list_place = ET.Element("{http://www.tei-c.org/ns/1.0}listPlace")
                back_node.append(list_place)
                for ent in ent_dict[key]:
                    list_place.append(ent)
            if key.endswith('org'):
                list_org = ET.Element("{http://www.tei-c.org/ns/1.0}listOrg")
                back_node.append(list_org)
                for ent in ent_dict[key]:
                    list_org.append(ent)
            if key.endswith('bibl') or key.endswith('biblStruct'):
                list_bibl = ET.Element("{http://www.tei-c.org/ns/1.0}listBibl")
                back_node.append(list_bibl)
                for ent in ent_dict[key]:
                    list_bibl.append(ent)
        root_node.append(back_node)
        doc.tree_to_file(file=x)
    except Exception as e:
        print(f"failed to process {x} due to {e}")