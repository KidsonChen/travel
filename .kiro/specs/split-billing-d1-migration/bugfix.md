# Bugfix Requirements Document

## Introduction

This document describes the migration of the split billing (記帳) feature from localStorage to Cloudflare D1 database. Currently, the splitbill.html application stores expense data in the browser's localStorage, which prevents data synchronization across devices and limits collaboration among the four users (佑任, 煌其, 芯慬, 嘉蕙).

The migration will implement a Cloudflare Workers API with D1 backend storage while maintaining backward compatibility through a fallback mechanism. The system will automatically migrate existing localStorage data on first launch and provide continued offline functionality through dual-write strategy.

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN users access splitbill.html from different browsers/devices THEN the expense data is NOT synchronized and each device shows different data

1.2 WHEN the browser's localStorage is cleared (cache clearing, private browsing, browser reset) THEN ALL expense records are PERMANENTLY LOST without any recovery option

1.3 WHEN multiple users need to collaborate on shared expenses THEN each user must manually export/import JSON files to share data, creating workflow friction and potential data loss

1.4 WHEN network connectivity is unavailable THEN the application completely FAILS to function with no graceful degradation path

1.5 WHEN users attempt to access expenses from mobile devices while traveling THEN they CANNOT view or update the shared expense database because localStorage is browser- and device-specific

### Expected Behavior (Correct)

2.1 WHEN users access splitbill.html from different browsers/devices THEN the expense data IS automatically synchronized through Cloudflare D1 database

2.2 WHEN the browser's localStorage is cleared THEN the expense data IS RECOVERED from the D1 database through automatic migration on first launch

2.3 WHEN multiple users collaborate on shared expenses THEN they CAN view and update the same expense records in real-time through the Workers API

2.4 WHEN network connectivity is unavailable THEN the application CONTINUES TO function with all features working locally using localStorage as fallback

2.5 WHEN users first access the application after migration deployment THEN existing localStorage data IS AUTOMATICALLY migrated to D1 and stored for future synchronization

2.6 WHEN API requests to D1 fail THEN the application SHOWS a user notification about offline mode before falling back to localStorage functionality

### Unchanged Behavior (Regression Prevention)

3.1 WHEN the application runs in browsers without Cloudflare Workers API access THEN the system SHALL CONTINUE TO function with localStorage as the sole storage mechanism

3.2 WHEN users add, edit, or delete expense records THEN the data structure and all calculation logic (total expenses, per-person split, settlement calculations) SHALL REMAIN IDENTICAL to the current behavior

3.3 WHEN users export/import JSON files THEN the existing export/import functionality SHALL CONTINUE TO work exactly as before for backup and data transfer purposes

3.4 WHEN users configure the application settings or UI preferences THEN the local UI state (active tab, form inputs, display preferences) SHALL CONTINUE TO be stored in localStorage without database dependency

3.5 WHEN the Cloudflare Workers API is not deployed or unavailable AND fallback is disabled by user THEN the application SHALL CONTINUE TO operate in read-only mode showing cached data

3.6 WHEN the application performs expense calculations THEN the settlement algorithm (who owes whom and by how much) SHALL CONTINUE TO use the exact same mathematical logic and rounding rules as the current implementation
