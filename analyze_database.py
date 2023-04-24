from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import nltk
from nltk.corpus import state_union
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.tokenize import RegexpTokenizer


def analyze_database(session):
    word_set, word_2_attr = session.execute_read(process_word_set)

    return word_set, word_2_attr


# 标记word属性的结构
class WordAttribute:
    n_type = False  # 节点的类型
    n_type_original = ""
    n_property_key = False  # 节点property的key
    n_property_value = False  # 节点property的value 及其对应的key
    # 同一个词可能是两个key的value。
    n_property_value_2_key = set()  # 节点property的value对应的key

    r_type = False  # 关系的类型
    n_type_original = ""
    r_property_key = False  # 关系property的key
    r_property_value = False  # 关系property的value 及其对应的key
    r_property_value_2_key = set()  # 关系property的value对应的key

    def __init__(self) -> None:
        self.n_type = False  # 节点的类型
        self.n_type_original = ""
        self.n_property_key = False  # 节点property的key
        self.n_property_value = False  # 节点property的value 及其对应的key
        self.n_property_value_2_key = set()  # 节点property的value对应的key

        self.r_type = False  # 关系的类型
        self.n_type_original = ""
        self.r_property_key = False  # 关系property的key
        self.r_property_value = False  # 关系property的value 及其对应的key
        self.r_property_value_2_key = set()  # 关系property的value对应的key

    def __str__(self):
        return (
            "n_type: {}; n_property_key: {}; n_property_value: {}; n_property_value_2_key: {};\nr_type: {}; "
            "r_property_key: {}; r_property_value: {}; r_property_value_2_key: {};\n".format(
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
            "n_type: {}; n_property_key: {}; n_property_value: {}; n_property_value_2_key: {};\nr_type: {}; "
            "r_property_key: {}; r_property_value: {}; r_property_value_2_key: {};\n".format(
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


def process_word_set(tx):
    word_set = set()
    word_2_attr = {}

    word_set, word_2_attr = get_node_word_set(tx, word_set, word_2_attr)
    word_set, word_2_attr = get_relationship_word_set(tx, word_set, word_2_attr)
    # print(word_2_attr["reviewed"])
    return word_set, word_2_attr


def get_node_word_set(tx, word_set, word_2_attr):
    # node
    query = "MATCH (n) return n"
    records = tx.run(query)

    # x代表处理好的
    for record in records:
        node = record["n"]
        # node label
        word_set, word_2_attr = do_node_label(list(node.labels), word_set, word_2_attr)

        # node properties
        for key in node:
            word_set, word_2_attr = do_node_key_value(
                str(node[key]), key, word_set, word_2_attr
            )

    return word_set, word_2_attr


def get_relationship_word_set(tx, word_set, word_2_attr):
    query = "MATCH ()-[r]->() return r"
    records = tx.run(query)
    for record in records:
        relationship = record["r"]
        # print(relationship)
        # print(relationship.type)
        # r type
        word_set, word_2_attr = do_relationship_type(
            relationship.type, word_set, word_2_attr
        )

        # r properties
        for key in relationship:
            word_set, word_2_attr = do_relationship_key_value(
                str(relationship[key]), key, word_set, word_2_attr
            )

    return word_set, word_2_attr


def do_node_label(labels, word_set, word_2_attr):
    for label in labels:
        labelx = formalize_token(label)
        word_set.add(labelx)
        if labelx not in word_2_attr:
            word_2_attr[labelx] = WordAttribute()
        word_2_attr[labelx].n_type = True
        word_2_attr[labelx].n_type_original = label
    return word_set, word_2_attr


def do_relationship_type(r_type, word_set, word_2_attr):
    r_type_tokens = r_type.split("_") if "_" in r_type else [r_type]

    stop_words = set(stopwords.words("english"))
    r_type_tokens = [w for w in r_type_tokens if not w in stop_words]

    for r_type_token in r_type_tokens:
        r_type_tokenx = formalize_token(r_type_token)
        word_set.add(r_type_tokenx)
        if r_type_tokenx not in word_2_attr:
            word_2_attr[r_type_tokenx] = WordAttribute()
        word_2_attr[r_type_tokenx].r_type = True
        word_2_attr[r_type_tokenx].r_type_original = r_type
    return word_set, word_2_attr


def do_node_key_value(value, key, word_set, word_2_attr):
    # print(key)
    # print(value)
    # print(value)
    keyx = formalize_token(key)
    word_set.add(keyx)
    if keyx not in word_2_attr:
        word_2_attr[keyx] = WordAttribute()
    word_2_attr[keyx].n_property_key = True

    # value 可能是句子
    # tokenize value, 不保留标点
    tokenizer = RegexpTokenizer(r"\w+")
    value_tokens = tokenizer.tokenize(value)

    # 去除stopwords
    stop_words = set(stopwords.words("english"))
    value_tokens = [w for w in value_tokens if not w in stop_words]

    for value_token in value_tokens:
        value_tokenx = formalize_token(value_token)  # 还原词性和统一小写
        word_set.add(value_tokenx)
        if value_tokenx not in word_2_attr:
            word_2_attr[value_tokenx] = WordAttribute()
        word_2_attr[value_tokenx].n_property_value = True
        word_2_attr[value_tokenx].n_property_value_2_key.add(keyx)
    return word_set, word_2_attr


def do_relationship_key_value(value, key, word_set, word_2_attr):
    keyx = formalize_token(key)
    word_set.add(keyx)
    if keyx not in word_2_attr:
        word_2_attr[keyx] = WordAttribute()
    word_2_attr[keyx].r_property_key = True

    # value 可能是句子
    # tokenize value, 不保留标点
    tokenizer = RegexpTokenizer(r"\w+")
    value_tokens = tokenizer.tokenize(value)

    # 去除stopwords
    stop_words = set(stopwords.words("english"))
    value_tokens = [w for w in value_tokens if not w in stop_words]

    for value_token in value_tokens:
        value_tokenx = formalize_token(value_token)  # 还原词性和统一小写
        word_set.add(value_tokenx)
        if value_tokenx not in word_2_attr:
            word_2_attr[value_tokenx] = WordAttribute()
        word_2_attr[value_tokenx].r_property_value = True
        word_2_attr[value_tokenx].r_property_value_2_key.add(keyx)
    return word_set, word_2_attr


def formalize_token(str):
    lemmatizer = WordNetLemmatizer()
    return lemmatizer.lemmatize(str).lower()
