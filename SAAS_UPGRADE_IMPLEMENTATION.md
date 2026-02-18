# SaaS Upgrade Implementation Guide

This document outlines the comprehensive SaaS upgrade for AutoMail. The implementation is being done systematically to ensure reliability and backward compatibility.

## Status

### ✅ Completed
- [x] Database migration for SaaS schema (users, templates, batches, analytics)
- [x] Authentication service (JWT with password hashing)
- [x] Auth routes (register, login, refresh)

### 🚧 In Progress
- [ ] Update existing routes to use authentication
- [ ] Update worker tasks to use Batch model
- [ ] Progress and batch APIs
- [ ] WebSocket real-time updates
- [ ] Templates CRUD
- [ ] Scheduling
- [ ] Analytics
- [ ] Frontend integration

## Implementation Plan

### Part A: Background Processing ✅ (Already implemented with RQ)
- RQ worker is already working
- Need to update to use Batch model

### Part B: Database Schema ✅
- Migration created: `003_saas_upgrade.py`
- Models updated with User, Batch, Template, AnalyticsSnapshot

### Part C: Progress & Results APIs
**Endpoints to implement:**
- `GET /jobs/{job_id}/batches/{batch_id}` - Already exists, needs Batch model
- `GET /jobs/{job_id}/batches/{batch_id}/progress` - New endpoint
- `GET /jobs/{job_id}/batches` - List batches
- `POST /jobs/{job_id}/batches/{batch_id}/retry_failed` - Retry failed

### Part D: WebSocket Real-time Updates
**Implementation:**
- Use Redis pub/sub for multi-worker support
- Worker publishes progress events
- FastAPI WebSocket endpoint relays to clients
- Client falls back to polling if WS unavailable

### Part E: Authentication ✅ (Partially done)
**Completed:**
- JWT token creation/validation
- Password hashing
- Register/login endpoints

**Remaining:**
- Update all job routes to require authentication
- Add user_id filtering to queries
- Create default user for existing data migration

### Part F: Email Templates
**Endpoints:**
- `GET /templates` - List user's templates
- `POST /templates` - Create template
- `GET /templates/{id}` - Get template
- `PUT /templates/{id}` - Update template
- `DELETE /templates/{id}` - Delete template
- Template variable rendering ({{variable}} replacement)

### Part G: Scheduling
**Implementation:**
- Add scheduled_for to Batch model ✅
- Scheduler loop to check for due batches
- Update worker to process scheduled batches
- Endpoint: `POST /jobs/{job_id}/schedule`

### Part H: Analytics
**Endpoints:**
- `GET /analytics/overview` - Daily totals
- `GET /analytics/batch/{batch_id}` - Batch breakdown
- Pre-compute analytics snapshots for performance

### Part I: Frontend Integration
**Pages to create/update:**
- `/login` - Login page
- `/register` - Registration page
- `/templates` - Template management
- Update job detail page for scheduling
- Analytics dashboard
- WebSocket progress updates

### Part J: Deployment
**Docker Compose:**
- backend service
- redis service
- worker service
- (optional) postgres for production-like testing

**Environment Variables:**
- Document all required env vars
- Separate dev/prod configs

## Next Steps

1. **Fix dependencies.py import** ✅
2. **Update worker_tasks.py to use Batch model**
3. **Update jobs router to require auth and use Batch**
4. **Implement progress APIs**
5. **Add WebSocket support**
6. **Implement templates**
7. **Add scheduling**
8. **Add analytics**
9. **Update frontend**
10. **Create docker-compose.yml**

## Migration Notes

When running the migration:
1. Existing jobs will have `user_id = NULL`
2. Need to create a default user or migrate existing data
3. Existing send_logs will be linked to batches automatically
4. Backward compatibility maintained where possible

## Testing Checklist

- [ ] Migration runs successfully
- [ ] Auth endpoints work
- [ ] Existing routes still work (with auth)
- [ ] Worker processes batches correctly
- [ ] Progress APIs return correct data
- [ ] WebSocket updates work
- [ ] Templates save and render correctly
- [ ] Scheduling works
- [ ] Analytics compute correctly
- [ ] Frontend integrates properly
