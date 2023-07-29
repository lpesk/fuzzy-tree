#!/usr/bin/env python3

import argparse
import os

from datetime import datetime
from random import choice, random

H_CONNECT = '╟⊹ '
V_CONNECT = '╢'
D_CONNECT = '╚╧╤╗'
U_CONNECT = '╔╤╧╝'
COL_GREEN = '\33[32m'
COL_END = '\33[0m'
DIACRITICS = list(map(chr, range(768, 879)))

DAY = 60 * 60 * 24
WEEK = 7 * DAY
MONTH = 4 * WEEK

def space(depth):
    return ' ' * depth * len(H_CONNECT)

def color(is_dir):
    if is_dir:
        return COL_GREEN
    return COL_END

def decorate(name, modified):
    now = datetime.now().timestamp()
    age = now - modified

    def choose(prob):
        if prob > random():
            return choice(DIACRITICS)
        return ''

    if age < WEEK:
        return name
    else:
        return ''.join([c + choose( (1.0/60.0) * (age // MONTH) ) for c in name])

class Tree:
    def __init__(self, root, max_depth, dirs_only):
        self.root = Node(root, "", 0)
        self.max_depth = max_depth
        self.dirs_only = dirs_only
        self.depth = 0
        self._build()

    def _build(self):
        current = []
        if self.root.is_dir or not self.dirs_only:
            current = [self.root]
        while current and (self.max_depth < 0 or self.depth < self.max_depth):
            future = []
            for node in current:
                node.get_children(self.dirs_only)
                for child in node.children:
                    future.append(child)
            current = future
            self.depth += 1

    def display(self):
        print(self.root.display_subtree())

class Node:
    def __init__(self, dirname, basename, depth):
        self.basename = basename
        self.dirname = dirname
        self.depth = depth
        self.path = os.path.join(dirname, basename)
        self.is_dir = os.path.isdir(self.path)
        self.children = []

    def get_children(self, dirs_only):
        children = []
        if not self.is_dir:
            return
        for name in os.listdir(self.path):
            child = Node(self.path, name, self.depth+1)
            if child.is_dir or not dirs_only:
                children.append(Node(self.path, name, self.depth+1))
        children.sort(key=lambda x: x.basename)
        self.children = children

    def display_subtree(self):
        lines = self._display()

        # Represent this node's descendents
        for (i, child) in enumerate(self.children):
            if i == 0:
                lines += f"{space(self.depth)}{D_CONNECT}\n"
##           uncomment for more vertical space between items
#            elif not self.children[i-1].children:
#                lines += f"{space(self.depth+1)}{V_CONNECT}\n"

            lines += child.display_subtree()

            if i == len(self.children) - 1:
                lines += f"{space(self.depth)}{U_CONNECT}\n"
        return lines

    def _display(self):
        lines = ""
        if self.depth > 0:
            lines += f"{space(self.depth)}{H_CONNECT}{color(self.is_dir)}{decorate(self.basename, os.path.getatime(self.path))}{COL_END}\n"
        else:
            lines += f"{U_CONNECT}\n"
            lines += f"{H_CONNECT}{color(self.is_dir)}{decorate(self.path, os.path.getatime(self.path))}{COL_END}\n"
        return lines

    def __repr__(self):
        return f"Node at depth {self.depth} with path {self.path}"

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--root", default=os.getcwd(), help="the directory to use as the tree root")
    parser.add_argument("-d", "--dirs-only", action="store_true", help="list directories only")
    parser.add_argument("-m", "--max-depth", default=-1, type=int, help="the max depth of the tree")
    args = parser.parse_args()

    try:
        os.stat(args.root)
    except:
        print(f"invalid path: {args.root}")
        exit()

    tree = Tree(args.root, args.max_depth, args.dirs_only)
    tree.display()
