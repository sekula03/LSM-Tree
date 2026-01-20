import csv

from LSM import LSM

indexes = {}
table_name = ""
headers = {}
next_id = 0


def create():
    global indexes, headers
    column = input("Column name: ")
    if column in indexes:
        print("There is already an index on this column")
        return
    if column in headers:
        idx, t = headers[column]
        indexes[column] = LSM(idx)
    else:
        print("Invalid column name")


def insert():
    global next_id, headers, table_name, indexes
    row = [str(next_id)]
    record = [next_id]
    items = sorted(headers.items(), key=lambda kv: kv[1][0])
    for name, (_, t) in items[1:]:
        val = input(f"Enter value for {name}: ")
        casted_val = t(val)
        row.append(str(casted_val))
        record.append(casted_val)
    with open(table_name, 'a', newline='') as table:
        writer = csv.writer(table)
        writer.writerow(row)
    for _, lsm in indexes.items():
        lsm.insert(record)
    next_id += 1


def delete():
    global table_name, headers, indexes
    row_id = input("Enter id to delete: ")
    rows = []
    found = False
    items = sorted(headers.items(), key=lambda kv: kv[1][0])
    _, col_types = zip(*[(name, typ) for name, (idx, typ) in items])
    with open(table_name, 'r', newline='') as table:
        reader = csv.reader(table)
        next(reader, None)
        for row in reader:
            if row[0] == row_id:
                found = True
                record = [t(v) for t, v in zip(col_types, row)]
                for col, lsm in indexes.items():
                    lsm.delete(record)
            else:
                rows.append(row)
    if not found:
        print("Invalid id")
        return
    with open(table_name, 'w', newline='') as table:
        writer = csv.writer(table)
        items = sorted(headers.items(), key=lambda kv: kv[1][0])
        headers_row = [f"{name}:{t.__name__}" for name, (idx, t) in items]
        writer.writerow(headers_row)
        writer.writerows(rows)


def search():
    global headers, indexes, table_name
    where_clause = input("Enter WHERE condition: ").strip()
    use_indexes = input("Use indexes? (Y/N) ").strip().upper() == "Y"
    aggregate_clause = input("Enter aggregate functions and columns: ").strip()
    tokens = where_clause.split()
    conditions = []
    operators = []
    for i, token in enumerate(tokens):
        if i % 2 == 0:
            col, val = token.split("=", 1)
            if col not in headers:
                print("Invalid column")
                return
            t = headers[col][1]
            val_casted = t(val)
            conditions.append((col, val_casted))
        else:
            op = token.upper()
            if op not in ("AND", "OR"):
                print("Invalid logical operator")
                return
            operators.append(op)
    aggregates = []
    if aggregate_clause:
        tokens = aggregate_clause.split()
        for i in range(0, len(tokens), 2):
            func, col = tokens[i].upper(), tokens[i + 1]
            if func not in ("AVG", "SUM", "MIN", "MAX", "COUNT"):
                print("Invalid aggregate function")
                return
            if col not in headers:
                print("Invalid column")
                return
            aggregates.append((func, col))
    records = {}
    if use_indexes:
        for i, (col, val) in enumerate(conditions):
            if col not in indexes:
                print(f"No index on column {col}")
                return
            tmp_res = indexes[col].search(val)
            tmp_dict = {r[0]: r for r in tmp_res}
            if i == 0:
                records = tmp_dict
            else:
                op = operators[i - 1]
                if op == "AND":
                    records = {pk: rec for pk, rec in records.items() if pk in tmp_dict}
                else:
                    records.update(tmp_dict)
    else:
        with open(table_name, "r", newline="") as table:
            reader = csv.reader(table)
            next(reader, None)
            items = sorted(headers.items(), key=lambda kv: kv[1][0])
            col_names, col_types = zip(*[(name, typ) for name, (idx, typ) in items])
            for row in reader:
                record = [t(v) for t, v in zip(col_types, row)]
                record_dict = dict(zip(col_names, record))
                satisfied = None
                for i, (col, val) in enumerate(conditions):
                    condition_result = (record_dict[col] == val)
                    if i == 0:
                        satisfied = condition_result
                    else:
                        op = operators[i - 1]
                        if op == "AND":
                            satisfied = satisfied and condition_result
                        else:
                            satisfied = satisfied or condition_result
                if satisfied:
                    records[record[0]] = record
    if not records:
        print("No matching rows found")
        return
    result = sorted(records.values(), key=lambda r: r[0])
    if aggregates:
        out = []
        for func, col in aggregates:
            idx, _ = headers[col]
            values = [r[idx] for r in result]
            res = 0
            if func == "AVG":
                res = sum(values) / len(values)
            elif func == "SUM":
                res = sum(values)
            elif func == "MIN":
                res = min(values)
            elif func == "MAX":
                res = max(values)
            elif func == "COUNT":
                res = len(values)
            out.append(res)
        print(out)
    else:
        for r in result:
            print(r)


def stats():
    global indexes
    if not indexes:
        print("No indexes created")
        return
    for col, lsm in indexes.items():
        line = f"{col} - "
        parts = []
        for i, level in enumerate(lsm.L):
            parts.append(f"L{i} : {lsm.size[i]}")
        line += ", ".join(parts)
        print(line)


def _fill():
    global table_name, headers, indexes, next_id
    copy_file = "copy.csv"
    try:
        with open(copy_file, "r", newline="") as src, open(table_name, "a", newline="") as dst:
            reader = csv.reader(src)
            writer = csv.writer(dst)
            for row in reader:
                writer.writerow(row)
                items = sorted(headers.items(), key=lambda kv: kv[1][0])
                _, col_types = zip(*[(name, typ) for name, (idx, typ) in items])
                record = [t(v) for t, v in zip(col_types, row)]
                for _, lsm in indexes.items():
                    lsm.insert(record)
                next_id = int(row[0]) + 1
    except FileNotFoundError:
        print("copy.csv not found")


def _init():
    global next_id, table_name, headers
    table_name = input("Table name: ") + ".csv"
    try:
        with open(table_name, 'r', newline='') as table:
            reader = csv.reader(table)
            header_row = next(reader, None)
            for idx, col in enumerate(header_row):
                col_name, col_type = col.split(":", 1)
                if col_type == "int":
                    t = int
                elif col_type == "float":
                    t = float
                elif col_type == "str":
                    t = str
                headers[col_name] = (idx, t)
            last = None
            for row in reader:
                last = row
            if last:
                next_id = int(last[0]) + 1
            else:
                next_id = 1
        return True
    except FileNotFoundError:
        print("Invalid table name")
        return False


def main():
    if not _init():
        return
    while True:
        print("\nChoose an operation:")
        print("--------------------")
        print("1 - create index")
        print("2 - insert into table")
        print("3 - delete from table")
        print("4 - search under condition")
        print("5 - index stats")
        print("0 - exit")
        op = int(input())
        while op not in (0, 1, 2, 3, 4, 5, 6):
            print("Invalid input")
            op = int(input())
        if op == 1:
            create()
        elif op == 2:
            insert()
        elif op == 3:
            delete()
        elif op == 4:
            search()
        elif op == 5:
            stats()
        elif op == 6:
            _fill()
        else:
            break


if __name__ == "__main__":
    main()
