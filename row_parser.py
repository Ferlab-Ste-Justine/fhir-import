class RowParser(object):

    def __init__(self, keys):
        self.keys = keys

    def col(self, row, key):
        return row[self.keys[key]]

    def as_dict(self, row):
        return {self.keys[idx]: r for idx, r in enumerate(row)}