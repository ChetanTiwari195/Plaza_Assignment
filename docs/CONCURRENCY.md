# Concurrency & Race Condition Prevention

This application is designed to gracefully handle concurrent requests for ride booking, particularly preventing the notorious "double booking" race condition where two users attempt to claim the same nearest driver at the exact same time.

## 1. Serializable Isolation in SQLite

The backend uses standard library `sqlite3`. By default, SQLite has robust but limited concurrency modes. To handle high concurrency reliably, we employ the following configuration:

- **WAL Mode (`PRAGMA journal_mode=WAL`)**: Allows concurrent readers even when a writer is active.
- **Busy Timeout (`PRAGMA busy_timeout=5000`)**: If the database is locked, standard SQLite will immediately throw a `database is locked` error. By setting a busy timeout, the underlying C driver will intelligently back off and retry up to 5 seconds before throwing an error, allowing high throughput without manual application-layer retries.

## 2. Immediate Transactions

In `app/db.py`, the `transaction()` context manager executes `BEGIN IMMEDIATE`.
- Normal `BEGIN` defers obtaining a write lock until the first `INSERT`/`UPDATE` is encountered. If two concurrent threads try to upgrade from a read lock to a write lock simultaneously, a deadlock occurs (`database is locked`).
- `BEGIN IMMEDIATE` immediately attempts to acquire a write lock. Because of the `busy_timeout`, concurrent threads simply queue up for milliseconds and process write locks sequentially.
- Since we use `BEGIN IMMEDIATE` for the entire `book_ride` service block, the entire process of querying available drivers, computing distance, and booking is isolated and serialized at the database level. 

## 3. Atomic Driver Claiming (Check-and-Set)

Even with serialization, we use a defensive "Check-and-Set" pattern for the actual driver claim logic to absolutely guarantee no double booking can occur, even if transaction bounds were modified in the future.

```python
# app/repositories/rides.py
def claim_driver(conn: sqlite3.Connection, driver_id: int) -> bool:
    cur = conn.execute(
        "UPDATE drivers SET status = 'ON_RIDE' WHERE id = ? AND status = 'AVAILABLE'", 
        (driver_id,)
    )
    return cur.rowcount > 0
```

1. The service reads available drivers and sorts them.
2. It iterates through the nearest candidates.
3. For each candidate, it attempts to `UPDATE` their status strictly enforcing `AND status = 'AVAILABLE'`.
4. If `cur.rowcount > 0`, we successfully claimed the driver atomically. If it returns `0`, it means another thread claimed the driver between our initial read and our update. 
5. Because it's a loop, if a driver was snagged, the service simply moves to the next closest driver in the list.

### Summary

The combination of `BEGIN IMMEDIATE` yielding sequential write-lock queuing, coupled with optimistic atomic check-and-set loops (`rowcount > 0`), ensures that:
1. No driver is ever assigned to two concurrent rides.
2. Under heavy load, users seamlessly get the next best driver without facing internal 500 server errors or lock exceptions.
