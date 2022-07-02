import glob
import os
import ciso8601
import time

from typesense.api_call import ObjectNotFound
from acdh_cfts_pyutils import TYPESENSE_CLIENT as client, CFTS_SCHEMA_NAME
from acdh_cfts_pyutils import CFTS_COLLECTION
from acdh_tei_pyutils.tei import TeiReader
from tqdm import tqdm


files = glob.glob('./data/editions/*.xml')
SCHEMA_NAME = 'staribacher'


try:
    client.collections[SCHEMA_NAME].delete()
except ObjectNotFound:
    pass

current_schema = {
    'name': SCHEMA_NAME,
    'fields': [
        {
            'name': 'id',
            'type': 'string'
        },
        {
            'name': 'rec_id',
            'type': 'string'
        },
        {
            'name': 'title',
            'type': 'string'
        },
        {
            'name': 'full_text',
            'type': 'string'
        },
        {
            'name': 'year',
            'type': 'int32',
            'facet': True,
        },
        {
            'name': 'date',
            'type': 'int64',
            'facet': True,
        },
        {
            'name': 'persons',
            'type': 'string[]',
            'facet': True,
            'optional': True
        }
    ],
    'default_sorting_field': 'date',
}

client.collections.create(current_schema)

records = []
cfts_records = []
for x in tqdm(files, total=len(files)):
    record = {}
    cfts_record = {'project': SCHEMA_NAME}
    head, tail = os.path.split(x)
    date_str = tail.replace('staribacher__', '').replace('.xml', '')
    record['year'] = int(date_str[:4])
    cfts_record['year'] = int(date_str[:4])
    ts = ciso8601.parse_datetime(date_str)
    record['date'] = int(time.mktime(ts.timetuple()))
    cfts_record['date'] = record['date']
    record['id'] = os.path.split(x)[-1].replace('.xml', '')
    cfts_record['id'] = record['id']
    cfts_record['resolver'] = f"https://csae8092.github.io/staribacher-static/{record['id']}.html"
    record['rec_id'] = os.path.split(x)[-1]
    cfts_record['rec_id'] = record['rec_id']

    doc = TeiReader(x)
    record['title'] = doc.any_xpath('.//tei:titleStmt/tei:title[1]')[0].text
    cfts_record['title'] = record['title']
    body = doc.any_xpath('.//tei:body')[0]
    record['persons'] = [
        x.text for x in doc.any_xpath('.//tei:back//tei:person/tei:persName[1]')
    ]
    cfts_record['persons'] = record['persons']
    record['full_text'] = " ".join(''.join(body.itertext()).split())
    cfts_record['full_text'] = record['full_text']
    records.append(record)
    cfts_records.append(cfts_record)

make_index = client.collections[SCHEMA_NAME].documents.import_(records)
print(make_index)
print(f'done with indexing: {SCHEMA_NAME}')

make_index = CFTS_COLLECTION.documents.import_(cfts_records, {'action': 'upsert'})

print(make_index)
print(f'done with indexing: {CFTS_SCHEMA_NAME}')
