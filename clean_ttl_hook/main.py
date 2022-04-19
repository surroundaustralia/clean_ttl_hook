import argparse
import os
from pathlib import Path

import rdflib
from rdflib import Graph
from rdfx import File


# removes unused namespace entries and re-serializes a graph with the prefixes in sorted order
def clean_ttl(input_file_path:Path):
    #get a list of all leading comments in the file
    comments_list = []
    comment_flag = False
    with open(input_file_path, "r", encoding='utf-8', errors='ignore') as f:
        for index, line in enumerate(f):
            if len(line.strip()) > 0 and line.strip()[0] == '#' and index == 0:
                comments_list.append(line.strip()[1:])
                comment_flag = True

            elif len(line.strip()) > 0 and line.strip()[0] == '#' and comment_flag:
                comments_list.append(line.strip()[1:])

            elif len(line.strip()) > 0 and line.strip()[0] != '#':
                comment_flag = False

            elif not comment_flag:
                break

    g = Graph()
    g.parse(input_file_path)
    all_ns = [n for n in g.namespaces()]
    subjects = [s for s in g.subjects()]
    predicates = [p for p in g.predicates()]
    objects = [o for o in g.objects()]
    all_prefixes = set(subjects + predicates + objects)
    used_namespace = []
    for full_prefix in all_prefixes:
        for prefix in all_ns:
            if prefix[1] in full_prefix:
                used_namespace.append(prefix)

    used_namespace = list(set(used_namespace))
    used_namespace.sort(key=lambda tup: tup[0])
    f = rdflib.Graph()
    for name in used_namespace:
        f.bind(name[0], name[1])

    for s, p, o in g:
        f.add((s, p, o))
    os.remove(input_file_path)
    ps = File(directory=input_file_path.parent)
    if len(comments_list) > 0:
        ps.write(g=g, filename=input_file_path.stem, leading_comments=comments_list)
    else:
        ps.write(g=g, filename=input_file_path.stem)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    args = parser.parse_args()

    for file in args.filenames:
        clean_ttl(file)


if __name__ == "__main__":
    main()
