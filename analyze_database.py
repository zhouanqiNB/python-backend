def analyze_database(session):
    word_set = session.execute_read(get_word_set)
    return word_set


class WordAttribute:
    n_type = False  # 节点的类型
    n_property_key = False  # 节点property的key
    n_property_value = False  # 节点property的value 及其对应的key
    n_property_value_2_key = ""  # 节点property的value对应的key

    r_type = False  # 关系的类型
    r_property_key = False  # 关系property的key
    r_property_value = False  # 关系property的value 及其对应的key
    r_property_value_2_key = ""  # 关系property的value对应的key


# return两个东西，一个是word集，另一个是每个word对应的属性，可以用word集中的内容做key读取
"""
{
    word_set: {, , ,}
    word_2_attr: {
        word1: WordAttribute(),
        word2: WordAttribute(),
    }
}
"""


def get_word_set(tx):
    word_set = {}
    word_2_attr = {}

    # node
    # node label

    query = "MATCH (n) return n"
    records = tx.run(query)
    res = []
    for record in records:
        print(record)
        node_id = record.get("id")
        labels = list(record.get("labels"))
        edge_count = 1

    # relationship

    return "ok"
