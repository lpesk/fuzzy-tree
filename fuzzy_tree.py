#!/usr/bin/env python3

import argparse
import os

from collections import deque
from datetime import datetime
from random import choice, random

H_CONNECTS = ['╟⊹ ','╠⊹ ', '╬⊹ ', '\b⊹╫⊹ ']
V_CONNECT = '╢'
D_CONNECT = '╚╧╤╗'
U_CONNECT = '╔╤╧╝'
COL_GREEN = '\33[32m'
COL_END = '\33[0m'
DIACRITICS = list(map(chr, range(768, 879)))

DAY = 60 * 60 * 24
YEAR = 365.0 * DAY
MONTH =  YEAR / 12.0

class Tree:
    def __init__(self, root, max_depth, dirs_only):
        self.root = Node(root, "", 0)
        self.max_depth = max_depth
        self.dirs_only = dirs_only
        self.depth = 0
        self._build()

    def _build(self):
        queue = deque([self.root])
        while queue and (self.max_depth < 0 or self.depth < self.max_depth):
            for i in range(len(queue)):
                node = queue.popleft()
                node.collect_children(self.dirs_only)
                for child in node.children:
                    queue.append(child)
            self.depth += 1

    def display(self):
        print(self.root.display_subtree())

class Node:
    def __init__(self, dirname, basename, depth):
        self.basename = basename
        self.dirname = dirname
        self.path = os.path.join(dirname, basename)
        try:
            os.stat(self.path)
        except:
            raise
        self.depth = depth
        self.is_dir = os.path.isdir(self.path)
        self.modified = os.path.getatime(self.path)
        self.children = []

    def collect_children(self, dirs_only):
        children = []
        if not self.is_dir:
            return
        for name in os.listdir(self.path):
            try:
                child = Node(self.path, name, self.depth+1)
                if (child.is_dir or not dirs_only):
                    children.append(child)
            except:
                continue
        children.sort(key=lambda x: x.basename)
        self.children = children

    def display_subtree(self):
        def space(depth):
            return ' ' * depth * len(H_CONNECTS[0])

        # Draw this node
        lines = ""
        if self.depth > 0:
            lines += f"{space(self.depth)}{str(self)}\n"
        else:
            lines += f"{U_CONNECT}\n"
            lines += f"{str(self)}\n"

        # Draw this node's descendents
        for (i, child) in enumerate(self.children):
            if i == 0:
                lines += f"{space(self.depth)}{D_CONNECT}\n"

            lines += child.display_subtree()

            if i == len(self.children) - 1:
                lines += f"{space(self.depth)}{U_CONNECT}\n"
        return lines

    def __str__(self):
        now = datetime.now().timestamp()
        age = now - self.modified

        def choose(prob):
            if prob > random():
                return choice(DIACRITICS)
            return ''

        stem = H_CONNECTS[0]
        name = self.basename if self.depth > 0 else self.path
        col = COL_GREEN if self.is_dir else COL_END
        if age > MONTH:
            # Add progressively more random moss each month up to 5 years
            name = ''.join([c + choose( (1.0/60.0) * (age // MONTH) ) for c in name])
            # Make the vine deterministically knottier over time
            if self.depth > 0:
                if age > 2 * YEAR:
                    stem = H_CONNECTS[3]
                elif age > YEAR:
                    stem = H_CONNECTS[2]
                elif age > MONTH:
                    stem = H_CONNECTS[1]

        return f"{stem}{col}{name}{COL_END}"


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
