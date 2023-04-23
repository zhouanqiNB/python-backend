import json


def query_all_handler(session):
    node_list = session.execute_read(do_query_all_node)
    relationship_list = session.execute_read(do_query_all_relationship)
    res = {"nodes": node_list, "links": relationship_list}
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
    # 统计节点边的数量
    query2 = "match (n)-[]-() return ID(n) as id,count(*) as count"
    records2 = tx.run(query2)
    id_2_edge_count = {}
    for record in records2:
        id_2_edge_count[record.get("id")] = record.get("count")

    # 节点基本信息
    query = "MATCH (n) return ID(n) as id, LABELS(n) as labels"
    records = tx.run(query)
    res = []
    for record in records:
        node_id = record.get("id")
        labels = list(record.get("labels"))
        edge_count = 1
        if node_id in id_2_edge_count:
            edge_count = id_2_edge_count[node_id]
        res.append({"node_id": node_id, "label": labels[0], "value": edge_count})
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
    query = "MATCH (n1)-[r]->(n2) return ID(n1) as id_n1 ,ID(r) as id_r,ID(n2) as id_n2"
    res = []
    for record in tx.run(query):
        relationship_id = record.get("id_r")
        node_id_1 = record.get("id_n1")
        node_id_2 = record.get("id_n2")

        res.append(
            {
                "relationship_id": relationship_id,
                "source": node_id_1,
                "target": node_id_2,
            }
        )

    return res
