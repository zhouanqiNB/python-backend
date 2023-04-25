from nltk.tokenize import RegexpTokenizer
from analyze_database import formalize_token


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


# 额这个n or r的标签的问题我还是 专门写一个模块吧
# 其实子串模糊匹配是可以的，但是大小写要对：match()-[r]->() where type(r) contains "ACT"  return r
def nl_query_handler(session, query_str, word_set, word_2_attr):
    query_str = "movie with Tom Hanks"
    # MATCH (n: Movie { released: 1992 }) return n

    # 分词, 不保留标点
    tokenizer = RegexpTokenizer(r"\w+")
    query_tokens = tokenizer.tokenize(query_str)

    query_attr = analyze_query(query_tokens, word_set, word_2_attr)
    print(query_attr)

    cypher_query_n = "MATCH (n) "
    cypher_query_r = "MATCH ()-[r]-() "

    print(cypher_query_n)

    print(word_2_attr["tom"])
    return word_2_attr["acted"].to_string()


def analyze_query(query_tokens, word_set, word_2_attr):
    query_attr = CypherAttr()

    for query_token in query_tokens:
        query_token = formalize_token(query_token)
        # 是否匹配上，匹配上了哪些词
        matched, matched_word_set = do_matching(word_set, query_token)
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
def do_matching(word_set, token):
    matched_word_set = []
    if token in word_set:
        matched_word_set.append(token)
        return True, matched_word_set
    else:
        return False, matched_word_set
