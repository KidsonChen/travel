# Implementation Plan: Split Billing D1 Migration

## Overview

This tasks document provides a detailed implementation plan for migrating the split billing feature from localStorage to Cloudflare D1 database. The implementation is organized into 5 phases covering database setup, API development, frontend modifications, testing, and deployment.

## Tasks

### Phase 1: D1 Database Setup

- [ ] 1.1 Create Cloudflare D1 Database
  - **Estimated Effort**: 15 minutes
  - **Dependencies**: None
  - **Verification**: D1 database appears in Cloudflare dashboard with name "split-billing"
  - **Steps**:
    1. Navigate to Cloudflare dashboard
    2. Go to Workers & Pages → D1
    3. Click "Create Database"
    4. Name: `split-billing`
    5. Select region closest to users
    6. Click "Create"

- [ ] 1.2 Create Database Schema (expenses table)
  - **Estimated Effort**: 10 minutes
  - **Dependencies**: 1.1
  - **Verification**: `expenses` table exists with correct schema in D1
  - **Steps**:
    1. Open D1 database in dashboard
    2. Go to Query Editor
    3. Run the following SQL:
    ```sql
    CREATE TABLE expenses (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      amount REAL NOT NULL,
      payer TEXT NOT NULL,
      note TEXT,
      shared TEXT NOT NULL,
      date TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX idx_payer ON expenses(payer);
    CREATE INDEX idx_date ON expenses(date);
    CREATE INDEX idx_created_at ON expenses(created_at);
    ```
    4. Verify table creation in Tables list

- [ ] 1.3 Configure wrangler.toml for D1 binding
  - **Estimated Effort**: 10 minutes
  - **Dependencies**: 1.1
  - **Verification**: wrangler.toml has correct D1 configuration with database ID
  - **Steps**:
    1. Create or update `wrangler.toml` in project root
    2. Add D1 database binding with actual database ID from Step 1.1
    3. Verify configuration with `npx wrangler d1 list`

### Phase 2: Cloudflare Worker API Implementation

- [ ] 2.1 Create Cloudflare Worker project structure
  - **Estimated Effort**: 5 minutes
  - **Dependencies**: None
  - **Verification**: Worker project has `worker.js` and `wrangler.toml`
  - **Steps**:
    1. Create new directory for worker
    2. Initialize with `npx wrangler init split-billing-api`
    3. Verify project structure

- [ ] 2.2 Implement API routes (worker.js)
  - **Estimated Effort**: 30 minutes
  - **Dependencies**: 1.2
  - **Verification**: All API endpoints respond correctly with test data
  - **Steps**:
    1. Create `worker.js` with fetch handler
    2. Implement GET `/api/expenses` endpoint
    3. Implement POST `/api/expenses` endpoint
    4. Implement DELETE `/api/expenses/:id` endpoint
    5. Implement POST `/api/migrate` endpoint
    6. Add CORS headers to all responses
    7. Test each endpoint with curl or Postman

- [ ] 2.3 Add error handling and logging
  - **Estimated Effort**: 15 minutes
  - **Dependencies**: 2.2
  - **Verification**: Errors are caught and logged properly without breaking responses
  - **Steps**:
    1. Add try-catch blocks to all API functions
    2. Implement console.error for debugging
    3. Return proper error responses with appropriate status codes
    4. Add request logging for monitoring

- [ ] 2.4 Configure CORS and security
  - **Estimated Effort**: 10 minutes
  - **Dependencies**: 2.2
  - **Verification**: CORS headers configured for specific domains
  - **Steps**:
    1. Replace wildcard CORS (`*`) with specific allowed origins
    2. Add rate limiting (optional but recommended)
    3. Implement request validation middleware
    4. Test CORS preflight requests

- [ ] 2.5 Deploy and test Worker
  - **Estimated Effort**: 10 minutes
  - **Dependencies**: 2.3, 2.4
  - **Verification**: Worker deployed and API endpoints accessible
  - **Steps**:
    1. Run `npx wrangler deploy`
    2. Copy deployed worker URL
    3. Test all API endpoints with worker URL
    4. Verify D1 database updates via API

### Phase 3: Frontend Implementation (splitbill.html)

- [ ] 3.1 Add D1 API configuration and state variables
  - **Estimated Effort**: 10 minutes
  - **Dependencies**: 2.5
  - **Verification**: API_BASE_URL configured correctly
  - **Steps**:
    1. Add `API_BASE_URL` constant pointing to deployed worker
    2. Add state variables: `localExpenses`, `isOnline`, `hasMigrated`
    3. Test URL configuration with fetch in browser console

- [ ] 3.2 Implement D1 data loading functions
  - **Estimated Effort**: 20 minutes
  - **Dependencies**: 3.1
  - **Verification**: `loadFromD1()` successfully retrieves and displays expenses
  - **Steps**:
    1. Implement `loadFromD1()` function
    2. Convert D1 format to internal format
    3. Handle API failures and fallback to localStorage
    4. Update `splitbill_migrated` flag on successful load

- [ ] 3.3 Implement D1 data saving functions
  - **Estimated Effort**: 20 minutes
  - **Dependencies**: 3.2
  - **Verification**: `saveToD1()` successfully stores expenses to D1
  - **Steps**:
    1. Implement `saveToD1()` function
    2. Detect expenses that need to be synced
    3. Implement batch sending if needed
    4. Handle save failures gracefully

- [ ] 3.4 Implement migration function
  - **Estimated Effort**: 15 minutes
  - **Dependencies**: 3.3
  - **Verification**: `migrateToD1()` successfully migrates localStorage data to D1
  - **Steps**:
    1. Implement `migrateToD1()` function
    2. POST all localStorage expenses to `/api/migrate`
    3. Update `splitbill_migrated` flag on success
    4. Handle migration failures gracefully

- [ ] 3.5 Modify addExpense function
  - **Estimated Effort**: 15 minutes
  - **Dependencies**: 3.4
  - **Verification**: New expenses are saved to both D1 and localStorage
  - **Steps**:
    1. Modify `addExpense()` to call `saveToD1()`
    2. Trigger migration on first expense if not already migrated
    3. Ensure localStorage save always happens for offline fallback

- [ ] 3.6 Modify deleteExpense function
  - **Estimated Effort**: 10 minutes
  - **Dependencies**: 3.5
  - **Verification**: Deleted expenses are removed from D1
  - **Steps**:
    1. Modify `deleteExpense()` to call DELETE API
    2. Handle API failures gracefully (delete locally anyway)
    3. Ensure localStorage always updates

- [ ] 3.7 Add network status monitoring
  - **Estimated Effort**: 10 minutes
  - **Dependencies**: None
  - **Verification**: App detects online/offline status and notifies user
  - **Steps**:
    1. Add event listeners for 'online' and 'offline' events
    2. Implement `showOfflineNotification()` function
    3. Update `isOnline` state variable
    4. Auto-sync when network restored

- [ ] 3.8 Modify DOMContentLoaded handler
  - **Estimated Effort**: 10 minutes
  - **Dependencies**: 3.2, 3.7
  - **Verification**: App loads from D1 if migrated, localStorage otherwise
  - **Steps**:
    1. Check for `splitbill_migrated` flag
    2. Load from D1 or localStorage based on flag
    3. Auto-trigger migration if data exists and not migrated
    4. Initialize online status

- [ ] 3.9 Update UI functions
  - **Estimated Effort**: 15 minutes
  - **Dependencies**: 3.7
  - **Verification**: Online/offline status displayed in UI
  - **Steps**:
    1. Override `updateUI()` to show network status
    2. Add status indicator to header
    3. Override `exportData()` to ensure localStorage is current
    4. Override `importData()` to handle both storage locations

### Phase 4: Testing and Verification

- [ ] 4.1 Test D1 database creation and schema
  - **Estimated Effort**: 5 minutes
  - **Dependencies**: 1.2
  - **Verification**: All database tables and indexes exist
  - **Steps**:
    1. Query `sqlite_master` to verify tables
    2. Verify column definitions
    3. Verify index creation

- [ ] 4.2 Test API endpoints
  - **Estimated Effort**: 15 minutes
  - **Dependencies**: 2.2
  - **Verification**: All endpoints work correctly with proper responses
  - **Steps**:
    1. Test GET `/api/expenses` (empty and with data)
    2. Test POST `/api/expenses` with valid data
    3. Test POST `/api/expenses` with invalid data (400 response)
    4. Test DELETE `/api/expenses/:id`
    5. Test POST `/api/migrate` with sample data

- [ ] 4.3 Test migration flow
  - **Estimated Effort**: 10 minutes
  - **Dependencies**: 3.4
  - **Verification**: Existing localStorage data migrates to D1 successfully
  - **Steps**:
    1. Add test data to localStorage
    2. Load page and verify migration notification
    3. Check D1 database has migrated data
    4. Verify `splitbill_migrated` flag is set

- [ ] 4.4 Test add/edit/delete operations
  - **Estimated Effort**: 15 minutes
  - **Dependencies**: 3.5, 3.6
  - **Verification**: All operations work and sync to D1
  - **Steps**:
    1. Add new expense, verify in D1
    2. Edit expense, verify D1 update
    3. Delete expense, verify removal from D1
    4. Check localStorage always updated

- [ ] 4.5 Test offline mode
  - **Estimated Effort**: 10 minutes
  - **Dependencies**: 3.7
  - **Verification**: App works offline with localStorage
  - **Steps**:
    1. Disconnect network
    2. Try adding expense
    3. Verify expense stored in localStorage
    4. Show offline notification
    5. Reconnect and verify sync

- [ ] 4.6 Test export/import functionality
  - **Estimated Effort**: 5 minutes
  - **Dependencies**: 3.9
  - **Verification**: Export/import still works correctly
  - **Steps**:
    1. Export data to JSON
    2. Verify JSON structure matches original
    3. Import JSON file
    4. Verify data appears correctly

- [ ] 4.7 Test calculations and UI
  - **Estimated Effort**: 10 minutes
  - **Dependencies**: None
  - **Verification**: All calculations and UI behavior identical to original
  - **Steps**:
    1. Add various expense combinations
    2. Verify settlement calculations match original
    3. Test all UI elements (tabs, inputs, buttons)
    4. Verify keyboard shortcuts still work

- [ ] 4.8 Test error handling
  - **Estimated Effort**: 10 minutes
  - **Dependencies**: 2.3
  - **Verification**: Errors don't break functionality
  - **Steps**:
    1. Mock API failures
    2. Verify graceful fallback to localStorage
    3. Verify user notifications for errors
    4. Verify app remains usable

### Phase 5: Deployment and Migration Strategy

- [ ] 5.1 Deploy Worker to production
  - **Estimated Effort**: 10 minutes
  - **Dependencies**: 2.5
  - **Verification**: Production worker accessible at intended URL
  - **Steps**:
    1. Configure production environment in wrangler.toml
    2. Run `npx wrangler deploy --env production`
    3. Verify production deployment in dashboard
    4. Test production endpoints

- [ ] 5.2 Update splitbill.html with production API URL
  - **Estimated Effort**: 5 minutes
  - **Dependencies**: 5.1
  - **Verification**: splitbill.html uses correct production URL
  - **Steps**:
    1. Update `API_BASE_URL` to production worker URL
    2. Test all functionality with production API
    3. Verify D1 integration in production

- [ ] 5.3 Monitor migration progress
  - **Estimated Effort**: Ongoing
  - **Dependencies**: 5.2
  - **Verification**: Migration data visible in D1 dashboard
  - **Steps**:
    1. Check D1 database for migrated records
    2. Monitor worker logs for errors
    3. Track migration success rate
    4. Address any issues promptly

- [ ] 5.4 Create rollback plan documentation
  - **Estimated Effort**: 15 minutes
  - **Dependencies**: 5.2
  - **Verification**: Rollback plan documented and accessible
  - **Steps**:
    1. Document how to revert to localStorage-only mode
    2. Create emergency rollback procedures
    3. Document how to manually migrate users
    4. Store rollback instructions in accessible location

- [ ] 5.5 Set up monitoring and alerts
  - **Estimated Effort**: 15 minutes
  - **Dependencies**: 5.1
  - **Verification**: Alerts configured for common failure modes
  - **Steps**:
    1. Configure D1 usage monitoring
    2. Set up worker error alerts
    3. Monitor API response times
    4. Track migration completion rates

## Verification Checklist

After completing all tasks, run this verification checklist:

- [ ] D1 database created with correct schema
- [ ] Worker deployed and accessible
- [ ] All API endpoints tested and working
- [ ] Migration works for existing localStorage data
- [ ] New expenses sync to D1
- [ ] Offline mode works with localStorage fallback
- [ ] Export/import functionality unchanged
- [ ] All calculations identical to original
- [ ] UI behavior unchanged
- [ ] Error handling prevents app crashes
- [ ] Network status notifications work
- [ ] Production deployment complete
- [ ] Monitoring configured

## Task Dependency Graph

```json
{
  "waves": [
    [
      {"id": "1.1"},
      {"id": "2.1"},
      {"id": "3.7"},
      {"id": "4.7"}
    ],
    [
      {"id": "1.2", "dependsOn": ["1.1"]},
      {"id": "1.3", "dependsOn": ["1.1"]},
      {"id": "2.2", "dependsOn": ["1.2"]},
      {"id": "3.1", "dependsOn": ["2.5"]},
      {"id": "4.1", "dependsOn": ["1.2"]},
      {"id": "4.2", "dependsOn": ["2.2"]},
      {"id": "4.7", "dependsOn": []},
      {"id": "4.8", "dependsOn": ["2.3"]},
      {"id": "5.1", "dependsOn": ["2.5"]},
      {"id": "5.3", "dependsOn": ["5.2"]},
      {"id": "5.4", "dependsOn": ["5.2"]},
      {"id": "5.5", "dependsOn": ["5.1"]}
    ],
    [
      {"id": "2.3", "dependsOn": ["2.2"]},
      {"id": "2.4", "dependsOn": ["2.2"]},
      {"id": "3.2", "dependsOn": ["3.1"]},
      {"id": "3.3", "dependsOn": ["3.2"]},
      {"id": "3.4", "dependsOn": ["3.3"]},
      {"id": "3.5", "dependsOn": ["3.4"]},
      {"id": "3.6", "dependsOn": ["3.5"]},
      {"id": "3.8", "dependsOn": ["3.2", "3.7"]},
      {"id": "3.9", "dependsOn": ["3.7"]},
      {"id": "4.3", "dependsOn": ["3.4"]},
      {"id": "4.4", "dependsOn": ["3.5", "3.6"]},
      {"id": "4.5", "dependsOn": ["3.7"]},
      {"id": "4.6", "dependsOn": ["3.9"]},
      {"id": "5.2", "dependsOn": ["5.1"]}
    ]
  ]
}
```

## Notes

- The implementation follows a dual-write strategy ensuring data is always stored in localStorage for offline fallback
- Migration is automatic and transparent to users
- All operations gracefully handle API failures by falling back to localStorage
- The `splitbill_migrated` flag prevents repeated migration attempts
- Offline mode is fully supported with automatic sync on reconnect