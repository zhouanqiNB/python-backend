def nl_query_handler(session, query_str, word_set, word_2_attr):
    query_str = "movie released in 1992"
    # MATCH (n: Movie { released: 1992 }) return n

    print(word_2_attr["jerry"])
    return "hello"
