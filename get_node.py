def get_node_handler(session, node_id):
    node = session.execute_read(query_node_by_id, node_id)
    return node


def query_node_by_id(tx, node_id):
    query = "MATCH (n) WHERE ID(n) = " + node_id + " return n"
    records = tx.run(query)
    i = 0
    res = {}
    for record in records:
        node = record.get('n')

        node_properties = {}
        for key in node:
            node_properties[key] = node[key]

        res = {
            "element_id": int(node.element_id[39:]),
            "labels": list(node.labels),
            "properties": node_properties
        }
    # print(res)
    return res
