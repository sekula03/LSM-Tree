# LSM Tree Mini-Project

A Python implementation of Log-Structured Merge (LSM) trees built as a learning project to understand how LSM trees function internally.

## Overview

This project simulates an LSM tree-based indexing system. It's important to note that this is a **simulation** - there's no actual disk access or database interaction. All operations happen in memory, demonstrating the core concepts of LSM trees without the complexity of real storage management.

## What are LSM Trees?

LSM trees are write-optimized data structures commonly used in modern databases. They work by buffering writes in memory and periodically merging them into larger, sorted structures on disk. This project implements a simplified three-level LSM tree with automatic compaction when size thresholds are exceeded.

## Features

- **B+ Tree backing**: Each LSM level uses a B+ tree for sorted storage
- **Multi-level architecture**: Three levels (L0, L1, L2) with increasing capacities (1000, 3000, 9000 records)
- **Automatic compaction**: Levels merge automatically when full
- **MVCC support**: Maintains record versions using sequence numbers
- **Tombstone deletion**: Soft deletes using tombstone markers
- **Range queries**: Efficient searches across indexed columns

## File Structure

- `BPlusTree.py` - B+ tree implementation for each LSM level
- `LSM.py` - Core LSM tree logic with insert, delete, search, and merge operations
- `main.py` - Interactive CLI for table operations
- `person.csv` - Table with 1000 rows of data for testing

## Usage

### Table Format

Tables are stored as CSV files with a special header format:
```
id:int,name:str,age:int,salary:int,height:int,weight:int
```

The first row must specify column names and types (`int`, `float`, or `str`).

### Running the Program

```bash
python main.py
```

You'll be prompted to enter a table name (without `.csv` extension). You can use the provided table or create your own.

### Available Operations

1. **Create Index** - Build an LSM index on a specific column
2. **Insert** - Add new records to the table
3. **Delete** - Remove records by ID
4. **Search** - Query with WHERE conditions (supports AND/OR) and aggregate functions (AVG, SUM, MIN, MAX, COUNT)
5. **Index Stats** - View current record counts per LSM level

### Testing with Your Own Data

You can test this implementation with your own CSV files:

1. Create a CSV file with the header format: `column1:type,column2:type,...`
2. Add your data rows below the header
3. Run the program and enter your table name
4. Create indexes and perform operations

## Example

person.csv:
```csv
id:int,name:str,age:int,salary:int,height:int,weight:int
1,William,19,58774,177,116
2,Alexander,27,58878,156,87
3,Emily,30,140121,159,50
...
```
