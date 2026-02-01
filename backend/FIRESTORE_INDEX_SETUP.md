# Firestore Index Setup Guide

## Issue
```
400 The query requires an index
```

This error occurs when querying Firestore with multiple fields (filtering + sorting).

## Your Query
The history API queries:
- Filter by: `user_id` 
- Sort by: `created_at` (descending)

This requires a **composite index**.

## Solution

### Quick Fix: Auto-Create Index

1. Click the link from your error message (or use the one below for your project):
   ```
   https://console.firebase.google.com/v1/r/project/prepit-200/firestore/indexes?create_composite=Clhwcm9qZWN0cy9wcmVwaXQtMjAwL2RhdGFiYXNlcy8oZGVmYXVsdCkvY29sbGVjdGlvbkdyb3Vwcy9wcmVwcm9jZXNzaW5nX2hpc3RvcnkvaW5kZXhlcy9fEAEaCwoHdXNlcl9pZBABGg4KCmNyZWF0ZWRfYXQQAhoMCghfX25hbWVfXxAC
   ```

2. Firebase will auto-fill the index configuration

3. Click **"Create index"**

4. Wait 1-2 minutes for index to build (status will change from "Building" to "Enabled")

5. Refresh your frontend - history should now load!

### Manual Setup (Alternative)

1. **Go to Firestore Indexes**:
   - https://console.firebase.google.com/project/prepit-200/firestore/indexes

2. **Click "Create Index"**

3. **Configure the index**:
   ```
   Collection ID: preprocessing_history
   
   Fields:
   - user_id      | Ascending
   - created_at   | Descending
   
   Query scope: Collection
   ```

4. **Click "Create"**

5. **Wait for index to build** (1-2 minutes)

## Why This is Needed

Firestore requires explicit indexes for queries that:
- Filter by one field AND sort by another field
- Use multiple inequality filters
- Use array-contains AND additional filters

In your case: filtering by `user_id` (equality) + sorting by `created_at` requires a composite index.

## Verification

After the index is created, test:

1. **Check Index Status**:
   - Go to: https://console.firebase.google.com/project/prepit-200/firestore/indexes
   - Status should show "Enabled" (not "Building")

2. **Test History API**:
   - Refresh your frontend
   - History should load without errors
   - Check backend logs - no more "requires an index" errors

## Troubleshooting

### Index Still Building
- Wait 2-5 minutes for large databases
- Status will change from "Building" → "Enabled"

### Still Getting Error After Index Created
1. Verify index fields match exactly:
   - `user_id` (Ascending)
   - `created_at` (Descending)
2. Check collection name: `preprocessing_history`
3. Clear browser cache and reload

### Multiple Index Errors
- If you get similar errors for other queries, click the link in each error
- Firebase will auto-create the needed index

## Index Details

**Collection**: `preprocessing_history`

**Index Fields**:
| Field | Type | Order |
|-------|------|-------|
| user_id | String | Ascending |
| created_at | Timestamp | Descending |

**Purpose**: Enables efficient querying of user-specific history sorted by date

**Query Pattern**:
```python
.where("user_id", "==", user_id)
.order_by("created_at", direction=firestore.Query.DESCENDING)
```

## Additional Indexes (If Needed)

If you implement filtering/sorting by other fields, you may need:

### By File Type
```
Fields:
- user_id      | Ascending
- file_type    | Ascending  
- created_at   | Descending
```

### By Status
```
Fields:
- user_id      | Ascending
- status       | Ascending
- created_at   | Descending
```

These can be created later if needed. Firestore will tell you when they're required.

## Best Practices

1. **Create indexes on-demand**: Only create indexes when Firestore requests them
2. **Monitor index usage**: Delete unused indexes to reduce storage costs
3. **Use error links**: The auto-generated links are the fastest way to create indexes
4. **Test queries**: After creating indexes, verify query performance improves

## Related Documentation

- [Firestore Index Documentation](https://firebase.google.com/docs/firestore/query-data/indexing)
- [Query Limitations](https://firebase.google.com/docs/firestore/query-data/queries#query_limitations)
- Your API code: [firestore_service.py](./app/services/firestore_service.py#L128)
