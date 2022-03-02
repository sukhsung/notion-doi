import os
from notion_client import Client
import py_journal

notion = Client(auth=os.environ["NOTION_TOKEN"])

database_id = "91d096542c42427b9541e1b3483b7e0e"

results = []
query = notion.databases.query(database_id=database_id)
results.extend(query['results'])
while query['next_cursor']:
    query = notion.databases.query(database_id=database_id, start_cursor=query['next_cursor'])
    result = query['results']
    results.extend( result )


m_list = []
for result in results:
    try:
        doi = result['properties']['doi']['rich_text'][0]['plain_text'] 
    except:
        doi = ''
    if len(doi) >0 and not result['properties']['Managed']['checkbox']:
        print(doi)
        m = py_journal.manuscript( doi ) 
        if len(m.authors) > 0:
            m_list.append( m )

            page_id = result['id']
            new_props = m.make_properties()
            notion.pages.update( page_id, **new_props )

