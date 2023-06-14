from sqlalchemy import false, true
from karmalegoweb.src.manage_data.save_data import (
    save_tirps_entities,
    save_root_entities,
    save_root_no_entities,
    save_tirps_no_entities,
)
from karmalegoweb.src.preprocessing.tirp import tirp


def separate_tirps_by_size(tirps, tirp_size=1):
    tirps_by_size = {}
    tirps_by_size[tirp_size] = [tirp for tirp in tirps if tirp.size == tirp_size]
    if len(tirps_by_size[tirp_size]) > 0:
        result = separate_tirps_by_size(tirps, tirp_size + 1)
        tirps_by_size.update(result)
    return tirps_by_size


def is_child_of(tirp, child):
    symbols_same = tirp.symbols == child.symbols[:-1]
    relations_num_diff = len(child.relations) - len(tirp.relations)
    relations_same = tirp.relations == child.relations[: -1 * relations_num_diff]
    return symbols_same and relations_same


def find_children(tirp, tirps_by_size):
    candidates = tirps_by_size[tirp.size + 1] if tirp.size + 1 in tirps_by_size else []
    return [child for child in candidates if is_child_of(tirp, child)]


def extend_tirp(tirp, tirps_by_size):
    children = find_children(tirp, tirps_by_size)
    if len(children) > 0:
        tirp.has_children = True
        tirp.children = children
        for child in children:
            extend_tirp(child, tirps_by_size)


def create_tree_structures(tirps):
    tirps_by_size = separate_tirps_by_size(tirps)

    root_tirps_children = tirps_by_size[1]
    for tirp in root_tirps_children:
        extend_tirp(tirp, tirps_by_size)

    return root_tirps_children


def findTirp(tirpsList, tirpToFind):
    for tirp in tirpsList:
        if tirp.equal(tirpToFind):
            return tirp
    return None


def merge_trees(tirps_root_cls0, tirps_root_cls1):
    """
    Accepts 2 tirp trees and return a combined tree of both.
    The combined tree is a union of the 2, meaning, every tirp that existed in one of the tirps
    will exists in the returned one.
    """
    for tirp_cls0 in tirps_root_cls0:
        tirp_cls1 = findTirp(tirps_root_cls1, tirp_cls0)
        if tirp_cls1 is not None:
            tirps_root_cls1.remove(tirp_cls1)
            tirp_cls0.stats_cls1 = tirp_cls1.stats_cls1
            tirp_cls0.has_children = tirp_cls0.has_children or tirp_cls1.has_children
            tirp_cls0.children = merge_trees(tirp_cls0.children, tirp_cls1.children)

    return tirps_root_cls0 + tirps_root_cls1


def __root_from_tree(tree):
    return [
        tirp(
            size=tirp_object.size,
            symbols=tirp_object.symbols,
            relations=tirp_object.relations,
            stats_cls0=tirp_object.stats_cls0,
            stats_cls1=tirp_object.stats_cls1,
            p_value_mhs=tirp_object.p_value_mhs,
            p_value_md=tirp_object.p_value_md,
            has_children=tirp_object.has_children,
            children=[],
        )
        for tirp_object in tree
    ]


def save_tree(dataset_name, visualization_id, tree):

    save_tirps_entities(dataset_name, visualization_id, tree)
    root = __root_from_tree(tree)
    save_root_entities(dataset_name, visualization_id, root)

    for tirp in tree:
        tirp.remove_entities()
    for tirp in root:
        tirp.remove_entities()

    save_tirps_no_entities(dataset_name, visualization_id, tree)
    save_root_no_entities(dataset_name, visualization_id, root)


def search_tirp(tree, symbols, relations) -> tirp:
    for tirp in tree:
        if tirp.symbols == symbols and tirp.relations == relations:
            return tirp

        else:
            contianed = true
            for i in range(len(tirp.symbols)):
                if tirp.symbols[i] != symbols[i]:
                    contianed = false

            # It can be more efficient if we check that the rels is contained in the given rels

            if len(symbols) > len(tirp.symbols) and contianed:
                found_tirp = search_tirp(tirp.children, symbols, relations)
                if found_tirp is not None:
                    return found_tirp
    return None
