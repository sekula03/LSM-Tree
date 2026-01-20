from bisect import bisect_left


class BPlusTreeNode:
    def __init__(self, is_leaf):
        self.is_leaf = is_leaf
        self.keys = []
        self.children = []
        self.next = None


class BPlusTree:
    def __init__(self, degree):
        if degree < 3:
            raise ValueError("Degree must be at least 3")
        self.root = BPlusTreeNode(True)
        self.degree = degree

    def search(self, value):
        start_key = (value, 0)
        end_key = (value, float('inf'))
        result = self._range(start_key, end_key)
        return result

    def insert(self, key, record):
        root = self.root
        if len(root.keys) == self.degree - 1:
            new_root = BPlusTreeNode(False)
            new_root.children.append(self.root)
            self._split(new_root, 0)
            self.root = new_root
        self._insert(self.root, key, record)

    def bottom_up(self, records):
        if not records:
            return BPlusTreeNode(True)
        degree = self.degree
        leaves = []
        for i in range(0, len(records), degree - 1):
            part = records[i:i + (degree - 1)]
            node = BPlusTreeNode(True)
            node.keys = [k for k, _ in part]
            node.children = [v for _, v in part]
            if leaves:
                leaves[-1].next = node
            leaves.append(node)
        level = leaves
        while len(level) > 1:
            new_level = []
            for i in range(0, len(level), degree):
                part = level[i:i + degree]
                node = BPlusTreeNode(False)
                node.children = part
                node.keys = [child.keys[0][0] for child in part[1:]]
                new_level.append(node)
            level = new_level
        return level[0]

    def _insert(self, node, key, record):
        if node.is_leaf:
            i = bisect_left(node.keys, key)
            node.keys.insert(i, key)
            node.children.insert(i, record)
        else:
            value = key[0]
            i = bisect_left(node.keys, value)
            child = node.children[i]
            if len(child.keys) == self.degree - 1:
                self._split(node, i)
                i = bisect_left(node.keys, value)
            self._insert(node.children[i], key, record)

    def _split(self, parent, index):
        degree = self.degree
        node = parent.children[index]
        new_node = BPlusTreeNode(node.is_leaf)
        mid = degree // 2
        if node.is_leaf:
            new_node.keys = node.keys[mid:]
            new_node.children = node.children[mid:]
            node.keys = node.keys[:mid]
            node.children = node.children[:mid]
            new_node.next = node.next
            node.next = new_node
            parent.keys.insert(index, new_node.keys[0][0])
            parent.children.insert(index + 1, new_node)
        else:
            parent.keys.insert(index, node.keys[mid])
            new_node.keys = node.keys[mid + 1:]
            node.keys = node.keys[:mid]
            new_node.children = node.children[mid + 1:]
            node.children = node.children[:mid + 1]
            parent.children.insert(index + 1, new_node)

    def _range(self, start_key, end_key):
        results = []
        node = self.root
        while not node.is_leaf:
            value = start_key[0]
            i = bisect_left(node.keys, value)
            node = node.children[i]
        while node:
            for k, v in zip(node.keys, node.children):
                value, pk = k[0], k[1]
                if start_key[0] <= value <= end_key[0] and start_key[1] <= pk <= end_key[1]:
                    results.append((k, v))
                elif value > end_key[0] or (value == end_key[0] and pk > end_key[1]):
                    return results
            node = node.next
        return results
