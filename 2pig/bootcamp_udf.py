@outputSchema("num:long")
def count_buzzword(content, buzzword):
    content = content.upper()
    buzzword = buzzword.upper()
    return content.count(buzzword)
