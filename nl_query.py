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
    # query_str = "act role carole"
    # MATCH (n: Movie { released: 1992 }) return n

    # 分词, 不保留标点, 得到 query_tokens
    tokenizer = RegexpTokenizer(r"\w+")
    query_tokens = tokenizer.tokenize(query_str)

    # 分析 query_tokens，得到 query_attr
    query_attr = analyze_query(query_tokens, word_set_syn, word_set, word_2_attr)
    print(query_attr)

    # 根据 query_attr 得到可能的 query list
    formalized_tokens = []
    for token in query_tokens:
        formalized_tokens.append(formalize_token(token))
    cypher_query_n_list = pack_cypher_n(query_attr, word_2_attr, formalized_tokens)
    cypher_query_r_list = pack_cypher_r(query_attr, word_2_attr, formalized_tokens)
    # print(cypher_query_n_list)
    # print(cypher_query_r_list)

    # execute every possible query and get results
    for query in cypher_query_n_list:
        records = session.run(query)
        nodes = []
        for record in records:
            nodes.append(int(record.get("n").element_id[39:]))
        query_response.query_results.append(QueryResult(query, nodes, []))
    for query in cypher_query_r_list:
        records = session.run(query)
        links = []
        for record in records:
            links.append(int(record.get("n").element_id[39:]))
        query_response.query_results.append(QueryResult(query, [], links))

    # print(query_response.to_json())

    # print(cypher_query_n)
    # cypher_query_r = "MATCH ()-[r]-() "

    # print(word_2_attr["tom"])

    # res1 = QueryResult("test1", [1], [10])
    # res2 = QueryResult("test2", [2, 3], [6, 8])

    # resp = QueryResp()
    # resp.query_results.append(res1)
    # resp.query_results.append(res2)
    # print(word_set_syn["person"])

    # print(word_2_attr["albert"])

    return query_response.to_json()


def pack_cypher_r(query_attr: CypherAttr, word_2_attr, tokens) -> list:
    matched_kvs = get_matched_kv("r", query_attr, word_2_attr)
    print(matched_kvs)
    cypher_r_list = []
    if len(query_attr.r_type) == 0:
        cypher_r_list.extend(generate_cypher_r("", matched_kvs, tokens))
    else:
        for r_type in query_attr.r_type:
            cypher_r_list.extend(generate_cypher_r(r_type, matched_kvs, tokens))
    return cypher_r_list


def pack_cypher_n(query_attr: CypherAttr, word_2_attr, tokens) -> list:
    """根据统计信息 返回可能的查询节点的cypher语句

    Args:
        :param query_attr:
        :param word_2_attr:
    """
    # 第一可能是完全匹配的key和value

    # 目前全部按照and来算
    matched_kvs = get_matched_kv("n", query_attr, word_2_attr)
    cypher_n_list = []
    if len(query_attr.n_type) == 0:
        cypher_n_list.extend(generate_cypher_n("", matched_kvs, tokens))
    else:
        for label in query_attr.n_type:
            cypher_n_list.extend(generate_cypher_n(label, matched_kvs, tokens))

    return cypher_n_list


def generate_cypher_n(label, kvs, tokens):
    res = []

    if label == "":
        if len(kvs) == 0:
            cypher = "MATCH (n) RETURN DISTINCT n"
            res.append(cypher)
            return res
        else:
            cypher = "MATCH (n) WHERE " + generate_property_condition(
                kvs[0][0], kvs[0][1]
            )
            kvs = kvs[1:]
            for kv in kvs:
                # 默认是或，可以查出更多结果
                if "and" in tokens:
                    cypher += " AND " + generate_property_condition(kv[0], kv[1])
                else:
                    cypher += " OR " + generate_property_condition(kv[0], kv[1])
            cypher += " RETURN DISTINCT n"
            res.append(cypher)
            return res
    else:
        # label condition
        cypher = "MATCH (n) WHERE " + generate_label_condition(label)
        for kv in kvs:
            if "and" in tokens:
                cypher += " AND " + generate_property_condition(kv[0], kv[1])
            else:
                cypher += " OR " + generate_property_condition(kv[0], kv[1])
        cypher += " RETURN DISTINCT n"
        res.append(cypher)
        return res


def generate_cypher_r(r_type, kvs, tokens):
    res = []

    if r_type == "":
        if len(kvs) == 0:
            cypher = "MATCH ()-[n]-() RETURN DISTINCT n"
            res.append(cypher)
            return res
        else:
            cypher = "MATCH ()-[n]-() WHERE " + generate_property_condition(
                kvs[0][0], kvs[0][1]
            )
            kvs = kvs[1:]
            for kv in kvs:
                if "and" in tokens:
                    cypher += " AND " + generate_property_condition(kv[0], kv[1])
                else:
                    cypher += " OR " + generate_property_condition(kv[0], kv[1])
            cypher += " RETURN DISTINCT n"
            res.append(cypher)
            return res
    else:
        # label condition
        cypher = "MATCH ()-[n]-() WHERE " + generate_type_condition(r_type)
        for kv in kvs:
            if "and" in tokens:
                cypher += " AND " + generate_property_condition(kv[0], kv[1])
            else:
                cypher += " OR " + generate_property_condition(kv[0], kv[1])
        cypher += " RETURN DISTINCT n"
        res.append(cypher)
        return res


def generate_property_condition(key, value):
    return "ANY(str IN n.{} WHERE toString(str) =~ '(?i).*{}.*')".format(key, value)


def generate_type_condition(r_type):
    return "TYPE(n) = '{}'".format(r_type)


def generate_label_condition(label):
    return "'{}' IN LABELS(n)".format(label)


def get_matched_kv(type_name, query_attr: CypherAttr, word_2_attr) -> list:
    """根据给定的统计信息 返回完全符合的key-value对

    Args:
        :param word_2_attr:
        :param query_attr: CypherAttr
        :param type_name: node / relationship
    """
    matched_kvs = []
    keys_in_query = []

    if type_name == "n":
        for key in query_attr.n_property_key:
            keys_in_query.append(word_2_attr[key].n_property_key_original)
        values_in_query = query_attr.n_property_value
        values_in_query_2_keys = {}
        for i in range(len(values_in_query)):
            values_in_query_2_keys[
                values_in_query[i]
            ] = query_attr.n_property_value_2_key[i]
        for value in values_in_query_2_keys:
            for key in values_in_query_2_keys[value]:
                if key in keys_in_query:
                    matched_kvs.append([key, value])
        # 没有match的情况下才只做value匹配
        if len(matched_kvs) == 0:
            for value in values_in_query_2_keys:
                for key in values_in_query_2_keys[value]:
                    matched_kvs.append([key, value])

        # print(matched_kvs)
        return matched_kvs
    else:
        for key in query_attr.r_property_key:
            keys_in_query.append(word_2_attr[key].r_property_key_original)
        values_in_query = query_attr.r_property_value
        values_in_query_2_keys = {}
        for i in range(len(values_in_query)):
            values_in_query_2_keys[
                values_in_query[i]
            ] = query_attr.r_property_value_2_key[i]
        for value in values_in_query_2_keys:
            for key in values_in_query_2_keys[value]:
                if key in keys_in_query:
                    matched_kvs.append([key, value])
        # 没有match的情况下才只做value匹配
        if len(matched_kvs) == 0:
            for value in values_in_query_2_keys:
                for key in values_in_query_2_keys[value]:
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

    # for every token
    for query_token in query_tokens:
        query_token = formalize_token(query_token)
        # 是否匹配上，匹配上了哪些词
        # 在 word_set_syn 中的词也能匹配上，但是返回的 matched_word_set 必在 word_set 中
        matched, matched_word_set = do_matching(word_set_syn, word_set, query_token)
        # print(matched_word_set)
        if not matched:
            continue

        # 对这个query_token匹配上的所有word，做统计
        for token in matched_word_set:
            if word_2_attr[token].n_type:  # 这个token是node label
                query_attr.n_type.append(word_2_attr[token].n_type_original)
            if word_2_attr[
                token
            ].n_property_key:  # 这个token是node key （保存key原型的话在 word_set 查不到 attr
                query_attr.n_property_key.append(token)
            if word_2_attr[token].n_property_value:  # 这个token是node value
                query_attr.n_property_value.append(token)
                query_attr.n_property_value_2_key.append(
                    word_2_attr[token].n_property_value_2_key
                )

            if word_2_attr[token].r_type:  # 这个token是relationship label
                query_attr.r_type.append(word_2_attr[token].r_type_original)
            if word_2_attr[token].r_property_key:  # 这个token是relationship key
                query_attr.r_property_key.append(token)
            if word_2_attr[token].r_property_value:  # 这个token是relationship value
                query_attr.r_property_value.append(token)
                query_attr.r_property_value_2_key.append(
                    word_2_attr[token].r_property_value_2_key
                )
    return query_attr


# 不在 word_set_syn 就是不在了
def do_matching(word_set_syn, word_set, token):
    """`word_set_syn` is superset of `word_set`
    for `token`, if in `word_set_syn`, add all of its syns;
    if `token` itself in `word_set`, add `token`.

    Args:
        :param word_set:
        :param token:
        :param word_set_syn:
    Returns:
        :return bool: 是否匹配到
        :return matched_word_set: 匹配到的词集
    """
    if token not in word_set_syn:
        return False, []

    matched_word_set = []
    # for every token,if token in word_set_syn
    # print(token)
    for i in word_set_syn[token]:  # push all syns
        matched_word_set.append(i)
    if token in word_set:  # push itself
        matched_word_set.append(token)
    return True, matched_word_set
