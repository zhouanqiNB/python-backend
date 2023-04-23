def get_relationship_handler(session, relationship_id):
    relationship = session.execute_read(query_relationship_by_id, relationship_id)
    return relationship


def query_relationship_by_id(tx, relationship_id):
    query = "MATCH ()-[r]->() WHERE ID(r) = " + relationship_id + " return r"
    records = tx.run(query)
    res = {}
    for record in records:
        relationship = record.get("r")

        print(relationship)
        relationship_properties = {}
        for key in relationship:
            relationship_properties[key] = relationship[key]

        res = {
            "element_id": int(relationship.element_id[39:]),
            "start_node_id": int(relationship.start_node.element_id[39:]),
            "end_node_id": int(relationship.end_node.element_id[39:]),
            "type": relationship.type,
            "properties": relationship_properties,
        }
    # print(res)
    return res
