import json


def query_all_handler(session):
    node_list = session.execute_read(do_query_all_node)
    relationship_list = session.execute_read(do_query_all_relationship)
    res = {
        "nodes": node_list,
        "relationships": relationship_list
    }
    # print(json.dumps(res))
    return json.dumps(res)


def do_query_all_node(tx):
    """
    res:
        records []record

    record:
        node_id
        labels
    """
    query = "MATCH (n) return n"
    query2 = "match (n)-[]-() return ID(n) as id,count(*) as count"
    records = tx.run(query)
    records2 = tx.run(query2)
    id2EdgeCount = {}
    for record in records2:
        id2EdgeCount[record.get("id")] = record.get("count")
    res = []
    for record in records:
        node_id = int(record.get('n').element_id[39:])
        labels = list(record.get('n').labels)
        edgeCount = 1
        if node_id in id2EdgeCount:
            edgeCount = id2EdgeCount[node_id]
        res.append({
            "node_id": node_id,
            "label": labels[0],
            "value": edgeCount
        })
    # print(res)
    return res


def do_query_all_relationship(tx):
    """
    res:
        records []record

    record:
        relationship_id
        node_id_1
        node_id_2
    """
    query = "MATCH (n1)-[r]->(n2) return n1,r,n2"
    res = []
    for record in tx.run(query):
        relationship_id = int(record.get('r').element_id[39:])
        node_id_1 = int(record.get('n1').element_id[39:])
        node_id_2 = int(record.get('n2').element_id[39:])

        res.append({
            "relationship_id": relationship_id,
            "node_id_1": node_id_1,
            "node_id_2": node_id_2
        })

    # print(res)
    return res
