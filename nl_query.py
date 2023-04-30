from nltk.tokenize import RegexpTokenizer
from analyze_database import formalize_token
import json


class CypherAttr:
    n_type = []  # 节点的类型，还原过的
    n_property_key = []  # 节点property的key
    n_property_value = []  # 节点property的value 及其对应的key
    n_property_value_2_key = []  # 节点property的value 及其对应的key

    r_type = []  # 关系的类型
    r_property_key = []  # 关系property的key
    r_property_value = []  # 关系property的value 及其对应的key
    r_property_value_2_key = []  # 关系property的value 及其对应的key

    def __init__(self) -> None:
        self.n_type = []  # 节点的类型
        self.n_property_key = []  # 节点property的key
        self.n_property_value = []  # 节点property的value 及其对应的key
        self.n_property_value_2_key = []  # 节点property的value 及其对应的key

        self.r_type = []  # 关系的类型
        self.r_property_key = []  # 关系property的key
        self.r_property_value = []  # 关系property的value 及其对应的key
        self.r_property_value_2_key = []  # 关系property的value 及其对应的key

    def __str__(self):
        return (
            "n_type: {};n_property_key: {}; n_property_value: {}; n_property_value_2_key: {};\nr_type: {}; "
            "r_property_key: {};r_property_value: {}; r_property_value_2_key: {};\n".format(
                self.n_type,
                self.n_property_key,
                self.n_property_value,
                self.n_property_value_2_key,
                self.r_type,
                self.r_property_key,
                self.r_property_value,
                self.r_property_value_2_key,
            )
        )

    def to_string(self):
        return (
            "n_type: {};n_property_key: {}; n_property_value: {}; n_property_value_2_key: {};\nr_type: {}; "
            "r_property_key: {};r_property_value: {}; r_property_value_2_key: {};\n".format(
                self.n_type,
                self.n_property_key,
                self.n_property_value,
                self.n_property_value_2_key,
                self.r_type,
                self.r_property_key,
                self.r_property_value,
                self.r_property_value_2_key,
            )
        )


class QueryResp:
    query_results = []

    def __init__(self) -> None:
        self.query_results = []

    def __str__(self):
        return "query_results:{}\n".format(self.query_results)

    def to_string(self):
        return "query_results:{}\n".format(self.query_results)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class QueryResult:
    query_str = ""
    query_records = {}

    def __init__(self, query, nodes, links) -> None:
        self.query_str = query
        self.query_records = {"nodes": nodes, "links": links}

    def __str__(self):
        return "query_str:{}; query_records:{}\n".format(
            self.query_str, self.query_records
        )

    def to_string(self):
        return "query_str:{}; query_records:{}\n".format(
            self.query_str, self.query_records
        )

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


# 额这个n or r的标签的问题我还是 专门写一个模块吧
# 其实子串模糊匹配是可以的，但是大小写要对：match()-[r]->() where type(r) contains "ACT"  return r
def nl_query_handler(session, query_str, word_set_syn, word_set, word_2_attr) -> str:
    query_response = QueryResp()

    # query_str = "film publish in 1992"
    # MATCH (n: Movie { released: 1992 }) return n

    # 分词, 不保留标点
    tokenizer = RegexpTokenizer(r"\w+")
    query_tokens = tokenizer.tokenize(query_str)

    query_attr = analyze_query(query_tokens, word_set_syn, word_set, word_2_attr)
    print(query_attr)

    cypher_query_n_list = pack_cypher_n(query_attr)
    print(cypher_query_n_list)
    # execute every possible query and get results
    for query in cypher_query_n_list:
        records = session.run(query)
        nodes = []
        for record in records:
            nodes.append(int(record.get("n").element_id[39:]))
        query_response.query_results.append(QueryResult(query, nodes, []))

    print(query_response.to_json())

    # print(cypher_query_n)
    # cypher_query_r = "MATCH ()-[r]-() "

    # print(word_2_attr["tom"])

    # res1 = QueryResult("test1", [1], [10])
    # res2 = QueryResult("test2", [2, 3], [6, 8])

    # resp = QueryResp()
    # resp.query_results.append(res1)
    # resp.query_results.append(res2)

    return query_response.to_json()


def pack_cypher_n(query_attr: CypherAttr) -> list:
    """根据统计信息 返回可能的查询节点的cypher语句

    Args:
        query_attr (CypherAttr)

    Returns:
        list: 可能的cypher语句列表
    """
    # 第一可能是完全匹配的key和value

    # 目前全部按照and来算
    matched_kvs = get_matched_kv(query_attr)
    cypher_n_list = []
    if len(query_attr.n_type) == 0:
        cypher_n_list.extend(generate_cypher_n("", matched_kvs))
    else:
        for label in query_attr.n_type:
            cypher_n_list.extend(generate_cypher_n(label, matched_kvs))

    return cypher_n_list


def generate_cypher_n(label, kvs):
    res = []

    if label == "":
        if len(kvs) == 0:
            cypher = "MATCH (n) RETURN n"
            res.append(cypher)
            return res
        else:
            cypher = "MATCH (n) WHERE n." + generate_property_condition(
                kvs[0][0], kvs[0][1]
            )
            kvs = kvs[1:]
            for kv in kvs:
                cypher += " AND n." + generate_property_condition(kv[0], kv[1])
            cypher += " RETURN n"
            res.append(cypher)
            return res
    else:
        # label condition
        cypher = "MATCH (n) WHERE " + generate_label_condition(label)
        for kv in kvs:
            cypher += " AND n." + generate_property_condition(kv[0], kv[1])
        cypher += " RETURN n"
        res.append(cypher)
        return res


def generate_property_condition(key, value):
    if not value.isnumeric():
        return key + "=~'(?i).*" + value + ".*'"
    else:
        return key + "=" + value


def generate_label_condition(label):
    return "'" + label + "'" + " in LABELS(n)"


def get_matched_kv(query_attr: CypherAttr) -> list:
    """根据给定的统计信息 返回完全符合的key-value对

    Args:
        query_attr (CypherAttr)

    Returns:
        list: 返回根据query_attr给出的信息做好的kv对
    """
    matched_kvs = []
    keys = query_attr.n_property_key
    values = query_attr.n_property_value
    value_2_keys = {}
    for i in range(len(values)):
        value_2_keys[values[i]] = query_attr.n_property_value_2_key[i]
    # print(value_2_keys)
    for value in value_2_keys:
        for key in value_2_keys[value]:
            if key in keys:
                matched_kvs.append([key, value])

    # print(matched_kvs)
    return matched_kvs


def analyze_query(
    query_tokens: list, word_set_syn, word_set, word_2_attr
) -> CypherAttr:
    """将自然语言字符串分词后的token与数据集词库比对 返回统计信息

    :param word_2_attr:
    :param word_set:
    :param query_tokens: 自然语言字符串分词后的token
    :param word_set_syn:
    """

    query_attr = CypherAttr()

    # 对每个token
    for query_token in query_tokens:
        query_token = formalize_token(query_token)
        # 是否匹配上，匹配上了哪些词
        matched, matched_word_set = do_matching(word_set_syn, query_token)
        print(matched_word_set)
        if not matched:
            continue
        # 对这个query_token匹配上的所有word，做统计
        for token in matched_word_set:
            # 这个token是node label
            if word_2_attr[token].n_type:
                query_attr.n_type.append(word_2_attr[token].n_type_original)
            # 这个token是node key
            if word_2_attr[token].n_property_key:
                query_attr.n_property_key.append(token)
            # 这个token是node value
            if word_2_attr[token].n_property_value:
                query_attr.n_property_value.append(token)
                query_attr.n_property_value_2_key.append(
                    word_2_attr[token].n_property_value_2_key
                )
            # 这个token是relationship label
            if word_2_attr[token].r_type:
                query_attr.r_type.append(word_2_attr[token].r_type_original)
            # 这个token是relationship key
            if word_2_attr[token].r_property_key:
                query_attr.r_property_key.append(token)
            # 这个token是relationship value
            if word_2_attr[token].r_property_value:
                query_attr.r_property_value.append(token)
                query_attr.r_property_value_2_key.append(
                    word_2_attr[token].r_property_value_2_key
                )
    return query_attr


# 还没引入向量匹配，单纯地in和not in
def do_matching(word_set_syn, token):
    """给定某个token和数据库字符集 返回匹配结果

    Args:
        :param token:
        :param word_set_syn:
    Returns:
        :return bool: 是否匹配到
        :return matched_word_set: 匹配到的词集
    """
    matched_word_set = []
    # for every token
    # if token in word_set_syn,
    if token in word_set_syn:
        if word_set_syn[token] == set():
            matched_word_set.append(token)
            return True, matched_word_set
        else:
            # 如果是匹配上同义词了，把同义词的可能原型都返回
            for i in word_set_syn[token]:
                matched_word_set.append(i)
        return True, matched_word_set
    else:
        return False, matched_word_set
