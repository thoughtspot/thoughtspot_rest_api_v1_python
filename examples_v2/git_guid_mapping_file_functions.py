# This example has several functions for interacting with the data structure in the files
# that store the GUID Mapping used by the Git Deploy command
# https://developers.thoughtspot.com/docs/guid-mapping

# The structure of the files is:

"""
[
{
  "originalGuid" : "a5fc94bc-1d0f-4fa9-b7b6-7ce4dc6bd526",
  "mappedGuid" : "67804442-2568-4184-bbe4-2ee058e31431",
  "counter" : 0,
  "additionalMapping" : { }
},
{
  "originalGuid" : "cb04e13a-7969-42d5-9469-c3beb5182af6",
  "mappedGuid" : "91864ed5-63c2-4c9d-8d20-ba9a1e77a888",
  "counter" : 1,
  "additionalMapping" : {
    "bc46684e-d8f4-4a82-a38b-b6233329c1cd" : "c79fd844-5a1b-4645-87e7-2fb70f0f3421",
    "e0c0fb87-a9fe-43e1-93c6-f6a058711986" : "5872f7eb-24fc-4f4e-8f96-95afd24dc707",
    "941271b6-86fa-4777-a189-46a0e85d3917" : "09b90dc1-6f95-47b4-857e-b83ec98dda00",
  }
}
]
"""

# Functon to take entire mapping object structure and swap all keys and values
# Useful if you are moving content in existing Org to a new "dev" Org, and then want to reverse
# the mapping around to put changes back into the original (now "prod") Org
def swap_original_and_mapped_guids(guid_mapping_object):
    swapped_object = []
    for o in guid_mapping_object:
        n = o.copy()
        n['originalGuid'] = o['mappedGuid']
        n['mappedGuid'] = o['originalGuid']
        if len(o['additionalMapping']) > 0:
            n['additionalMapping'] = {}
            for a in o['additionalMapping']:
                n['additionalMapping'][o['additionalMapping'][a]] = a

        swapped_object.append(n)
    return swapped_object