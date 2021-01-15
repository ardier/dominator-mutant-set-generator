def total_subsumed_size(mutant):
    result = mutant.size
    descendents = mutant.get_descendents()
    for descendent in descendents:
        result += descendent.size
    return result
