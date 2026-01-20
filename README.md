# LSM-Tree Mini-Project

## Project Overview

This mini-project was created as a learning exercise to understand **LSM Trees (Log-Structured Merge-Trees)** and how they function. The implementation includes a basic LSM-Tree data structure with B+ Tree indexes, demonstrating the core concepts and operations of LSM-Trees in a practical, hands-on way.

## What is an LSM-Tree?

A **Log-Structured Merge-Tree (LSM-Tree)** is a data structure that provides indexed access to files with high insert and delete performance. LSM-Trees are widely used in modern database systems like Apache Cassandra, LevelDB, RocksDB, and HBase.

### Key Concepts

1. **Write Optimization**: LSM-Trees are optimized for write-heavy workloads by batching writes in memory before flushing to disk.

2. **Multiple Levels**: Data is organized in multiple levels (L0, L1, L2, etc.), where each level is larger than the previous one.

3. **Merge Operations**: When a level becomes full, data is merged (compacted) into the next level, maintaining sorted order and removing obsolete entries.

4. **Tombstones**: Deletions are handled using tombstone markers rather than immediate deletion, which are later removed during compaction.

## How LSM-Trees Function

### Write Path
1. New records are inserted into the smallest level (L0) with a sequence number for versioning.
2. When L0 reaches capacity, it triggers a merge operation with L1.
3. During merging, duplicate keys are resolved by keeping the latest version (highest sequence number).
4. Tombstones are used to mark deleted records.

### Read Path
1. Search across all levels for matching keys.
2. Collect all versions of a record across levels.
3. Return only the latest non-deleted versions based on sequence numbers.

### Compaction
- When a level exceeds its capacity, records from that level and the next level are merged.
- Only the latest version of each record is kept (identified by sequence number).
- Deleted records (tombstones) are filtered out during compaction.
- The merged data is written to the next level, and the current level is cleared.

## Project Structure

### Files

- **`LSM.py`**: Core LSM-Tree implementation
  - Manages multiple B+ Tree levels
  - Handles insert, delete, and search operations
  - Implements merge/compaction logic
  - Tracks sequence numbers for versioning

- **`BPlusTree.py`**: B+ Tree data structure implementation
  - Provides the underlying indexed storage for each LSM level
  - Supports range queries and sorted access
  - Implements node splitting and tree balancing

- **`main.py`**: Interactive command-line application
  - CSV-based table management
  - Index creation and management
  - Insert, delete, and search operations
  - Aggregate functions (AVG, SUM, MIN, MAX, COUNT)
  - Index statistics visualization

### LSM-Tree Configuration

This implementation uses 3 levels with the following capacities:
- **L0**: 1,000 records (in-memory tier)
- **L1**: 3,000 records
- **L2**: 9,000 records

Each level has a 3x capacity multiplier relative to the previous level.

## Implementation Details

### Key Structure

Each key in the LSM-Tree is a tuple containing:
- `(indexed_value, primary_key, sequence_number, is_valid)`

Where:
- `indexed_value`: The value being indexed
- `primary_key`: Unique identifier for the record
- `sequence_number`: Monotonically increasing counter for versioning
- `is_valid`: Flag indicating if record is active (1) or deleted (0)

### Core Operations

**Insert**:
```python
lsm.insert(record)  # Adds record with new sequence number
```

**Delete**:
```python
lsm.delete(record)  # Inserts tombstone marker
```

**Search**:
```python
results = lsm.search(value)  # Returns latest non-deleted records
```

## Usage

### Running the Application

```bash
python main.py
```

### Operations

The application provides an interactive menu with the following operations:

1. **Create Index**: Create an index on a specific column
2. **Insert**: Add new records to the table
3. **Delete**: Remove records by ID
4. **Search**: Query records with WHERE conditions (supports AND/OR operators)
5. **Index Stats**: View current size of each LSM level
6. **Exit**: Quit the application

### Example Workflow

```
Table name: person
Choose an operation:
--------------------
1 - create index
2 - insert into table
3 - delete from table
4 - search under condition
5 - index stats
0 - exit
```

## Learning Outcomes

Through this project, I learned:

1. **Write Optimization**: How LSM-Trees achieve high write throughput by deferring expensive merge operations
2. **Space-Time Tradeoffs**: Balancing write performance against read performance and space amplification
3. **Versioning**: Using sequence numbers to handle concurrent operations and maintain consistency
4. **Compaction Strategies**: How merge operations consolidate data and remove obsolete versions
5. **Practical Applications**: Why modern NoSQL databases choose LSM-Trees for write-intensive workloads

## Key Takeaways

- LSM-Trees trade read performance for significantly better write performance
- The merge process is crucial for maintaining query efficiency over time
- Tombstones allow deletions without immediate I/O operations
- Multi-level organization enables efficient space utilization
- B+ Trees provide an excellent foundation for sorted, indexed storage within each level

## Future Enhancements

Potential improvements to explore:
- Bloom filters for faster negative lookups
- Background compaction threads
- Write-ahead logging (WAL) for durability
- Size-tiered or leveled compaction strategies
- Compression for reduced storage footprint

## References

- O'Neil, P., Cheng, E., Gawlick, D., & O'Neil, E. (1996). The log-structured merge-tree (LSM-tree). *Acta Informatica*, 33(4), 351-385.
- Modern database systems: Cassandra, LevelDB, RocksDB, HBase

---

**Note**: This is an educational project designed for learning purposes. It demonstrates core LSM-Tree concepts but is not optimized for production use.
