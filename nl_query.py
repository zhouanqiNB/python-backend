from nltk.tokenize import RegexpTokenizer


class CypherAttr:
    n_type = ""  # 节点的类型
    n_property_key = ""  # 节点property的key
    n_property_value = ""  # 节点property的value 及其对应的key
    n_property_value_2_key = []  # 节点property的value 及其对应的key

    r_type = ""  # 关系的类型
    r_property_key = ""  # 关系property的key
    r_property_value = ""  # 关系property的value 及其对应的key
    r_property_value_2_key = []  # 关系property的value 及其对应的key

    def __init__(self) -> None:
        self.n_type = ""  # 节点的类型
        self.n_property_key = ""  # 节点property的key
        self.n_property_value = ""  # 节点property的value 及其对应的key
        self.n_property_value_2_key = []  # 节点property的value 及其对应的key

        self.r_type = ""  # 关系的类型
        self.r_property_key = ""  # 关系property的key
        self.r_property_value = ""  # 关系property的value 及其对应的key
        self.r_property_value_2_key = []  # 关系property的value 及其对应的key


# 额这个n or r的标签的问题我还是 专门写一个模块吧
# 其实子串模糊匹配是可以的，但是大小写要对：match()-[r]->() where type(r) contains "ACT"  return r
def nl_query_handler(session, query_str, word_set, word_2_attr):
    query_str = "movie released in 1992"
    # MATCH (n: Movie { released: 1992 }) return n

    # 分词, 不保留标点
    tokenizer = RegexpTokenizer(r"\w+")
    query_tokens = tokenizer.tokenize(query_str)
    print(query_tokens)

    query_cypher = CypherAttr()

    for token in query_tokens:
        if token in word_set:
            if word_2_attr[token].n_type:
                if query_cypher.n_type == "":
                    query_cypher.n_type = word_2_attr[token].n_type_original
            if word_2_attr[token].n_property_key:
                if query_cypher.n_property_key == "":
                    query_cypher.n_property_key = token
            if word_2_attr[token].n_property_value:
                if query_cypher.n_property_value == "":
                    query_cypher.n_property_value = token
                    query_cypher.n_property_value_2_key.extend(
                        word_2_attr[token].n_property_value_2_key
                    )
            if word_2_attr[token].r_type:
                if query_cypher.r_type == "":
                    query_cypher.r_type = word_2_attr[token].r_type_original
            if word_2_attr[token].r_property_key:
                if query_cypher.r_property_key == "":
                    query_cypher.r_property_key = token
            if word_2_attr[token].r_property_value:
                if query_cypher.r_property_value == "":
                    query_cypher.r_property_value = token
                    query_cypher.r_property_value_2_key.extend(
                        word_2_attr[token].r_property_value_2_key
                    )

    cypher_query_n = "MATCH (n) "
    cypher_query_r = "MATCH ()-[r]-() "

    # query node
    # match (n) WHERE "Movie" in LABELS(n) and n.title =~ "(?i).*matrix.*" Return n
    where_added = False
    if query_cypher.n_type != "":
        cypher_query_n = cypher_query_n + "WHERE "
        where_added = True
        cypher_query_n = (
                cypher_query_n + '"' + query_cypher.n_type.title() + '"' + " in LABELS(n) "
        )
    print(cypher_query_n)

    if query_cypher.n_property_value != "":
        # 指定了key
        if (
                query_cypher.n_property_key != ""
                and query_cypher.n_property_key in query_cypher.n_property_value_2_key
        ):
            if not where_added:
                cypher_query_n = cypher_query_n + "WHERE "
                where_added = True
            else:
                cypher_query_n = cypher_query_n + " and "
            print(cypher_query_n)
            cypher_query_n = (
                    cypher_query_n
                    + "n."
                    + query_cypher.n_property_key
                    + " contains "
                    + '"'
                    + query_cypher.n_property_value
                    + '"'
            )
        # 没有指定key
        else:
            for key in query_cypher.n_property_value_2_key:
                if not where_added:
                    cypher_query_n = cypher_query_n + "WHERE "
                    where_added = True
                else:
                    cypher_query_n = cypher_query_n + " and "
                cypher_query_n = (
                        cypher_query_n
                        + "n."
                        + key
                        + " contains "
                        + '"'
                        + query_cypher.n_property_value
                        + '"'
                )

    print(cypher_query_n)

    print(word_2_attr["movie"])
    return word_2_attr["movie"].to_string()
