from BPlusTree import BPlusTree


def latest(key_list):
    last = {}
    for k, v in key_list:
        pk = k[1]
        seq = k[2]
        if pk not in last or seq > last[pk][0][2]:
            last[pk] = (k, v)
    return last


class LSM:
    def __init__(self, index, degree=100):
        self.degree = degree
        self.index = index
        self.L = [BPlusTree(degree), BPlusTree(degree), BPlusTree(degree)]
        self.size = [0, 0, 0]
        self.max_size = [1000, 3000, 9000]
        self.seq_counter = 1

    def insert(self, record):
        seq = self.seq_counter
        key = (record[self.index], record[0], seq, 1)
        if self.size[0] == self.max_size[0]:
            self._merge(0, 1)
        self.L[0].insert(key, record)
        self.size[0] += 1
        self.seq_counter += 1

    def delete(self, record):
        seq = self.seq_counter
        key = (record[self.index], record[0], seq, 0)
        self.L[0].insert(key, "TOMBSTONE")
        self.seq_counter += 1

    def search(self, value):
        records = []
        for tree in self.L:
            results = tree.search(value)
            records.extend(results)
        last = latest(records)
        valid = [v for k, v in last.values() if k[3] == 1]
        return valid

    def _merge(self, id1, id2):
        records = []
        for tree in (self.L[id1], self.L[id2]):
            node = tree.root
            while not node.is_leaf:
                node = node.children[0]
            while node:
                for k, v in zip(node.keys, node.children):
                    records.append((k, v))
                node = node.next
        last = latest(records)
        all_records = [(k, v) for k, v in last.values() if k[3] == 1]
        all_records.sort(key=lambda x: (x[0][0], x[0][1]))
        new_tree = BPlusTree(self.degree)
        new_tree.root = new_tree.bottom_up(all_records)
        self.L[id1] = BPlusTree(self.degree)
        self.size[id1] = 0
        self.L[id2] = new_tree
        self.size[id2] = len(all_records)
        if id2 + 1 < len(self.L) and self.size[id2] > self.max_size[id2]:
            self._merge(id2, id2 + 1)
