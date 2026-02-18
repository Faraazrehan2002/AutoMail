# Frontend Integration Guide

This guide outlines what needs to be updated in the Next.js frontend to support all SaaS features.

## Required Frontend Updates

### 1. Authentication Pages

**Create `/web/app/login/page.tsx`:**
- Login form (email + password)
- Call `POST /api/auth/login`
- Store JWT token in httpOnly cookie (via Next.js API route)
- Redirect to dashboard on success

**Create `/web/app/register/page.tsx`:**
- Registration form (email + password + full_name)
- Call `POST /api/auth/register`
- Store JWT token
- Redirect to dashboard

**Update `/web/app/api/auth/login/route.ts`:**
```typescript
// Set httpOnly cookie with JWT token
// Forward to backend /auth/login
```

**Update `/web/app/api/auth/register/route.ts`:**
```typescript
// Set httpOnly cookie with JWT token
// Forward to backend /auth/register
```

### 2. API Client Updates

**Update `/web/src/lib/api.ts`:**
- Add auth token to all requests (from cookie)
- Add template endpoints:
  - `getTemplates()`
  - `createTemplate()`
  - `updateTemplate()`
  - `deleteTemplate()`
- Add scheduling endpoint:
  - `scheduleSend()`
- Add analytics endpoints:
  - `getAnalyticsOverview()`
  - `getBatchAnalytics()`
- Add WebSocket client helper

### 3. Templates Page

**Create `/web/app/templates/page.tsx`:**
- List all templates
- Create new template form
- Edit/delete templates
- Template variable preview
- Use template in send flow

### 4. Job Detail Page Updates

**Update `/web/app/jobs/[jobId]/page.tsx`:**
- Add template selector dropdown
- Add scheduling UI (datetime picker)
- Add "Send Now" vs "Schedule" toggle
- Integrate WebSocket for real-time progress
- Show batch list
- Add retry failed button

### 5. WebSocket Integration

**Create `/web/src/lib/websocket.ts`:**
```typescript
export function useBatchProgress(jobId: string, batchId: string) {
  // Connect to WS /ws/jobs/{jobId}/batches/{batchId}
  // Fallback to polling if WS unavailable
  // Return progress state
}
```

**Update batch status display:**
- Use WebSocket hook
- Auto-update progress
- Show real-time status

### 6. Analytics Dashboard

**Create `/web/app/analytics/page.tsx`:**
- Overview charts (recharts)
- Daily metrics graph
- Success rate visualization
- Batch breakdown views

### 7. Navigation Updates

**Update layout/navbar:**
- Add login/logout buttons
- Add templates link
- Add analytics link
- Show user info if logged in

### 8. API Route Proxies

**Create/Update Next.js API routes:**
- `/web/app/api/templates/route.ts` - List/create templates
- `/web/app/api/templates/[id]/route.ts` - Get/update/delete template
- `/web/app/api/jobs/[jobId]/schedule/route.ts` - Schedule send
- `/web/app/api/analytics/overview/route.ts` - Analytics overview
- `/web/app/api/analytics/batch/[batchId]/route.ts` - Batch analytics

All routes should:
- Read JWT from httpOnly cookie
- Forward to backend with `X-APP-KEY` header
- Handle errors gracefully

### 9. Auth Middleware

**Create `/web/middleware.ts`:**
```typescript
// Protect routes that require auth
// Redirect to /login if not authenticated
// Allow public routes: /login, /register
```

### 10. Batch List Component

**Create component to show:**
- All batches for a job
- Batch status badges
- Scheduled batches with countdown
- Retry failed functionality

## Implementation Priority

1. **High Priority:**
   - Authentication (login/register)
   - API client updates
   - WebSocket progress integration
   - Template selector in send flow

2. **Medium Priority:**
   - Templates CRUD page
   - Scheduling UI
   - Analytics dashboard

3. **Low Priority:**
   - Advanced analytics charts
   - Batch management UI
   - User settings

## Example Code Snippets

### WebSocket Hook
```typescript
// web/src/hooks/useBatchProgress.ts
import { useEffect, useState } from 'react';

export function useBatchProgress(jobId: string, batchId: string) {
  const [progress, setProgress] = useState(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/jobs/${jobId}/batches/${batchId}`);
    
    ws.onopen = () => setConnected(true);
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === 'progress') {
        setProgress(data);
      }
    };
    ws.onerror = () => {
      // Fallback to polling
      const interval = setInterval(async () => {
        const res = await fetch(`/api/jobs/${jobId}/batches/${batchId}/progress`);
        const data = await res.json();
        setProgress(data);
      }, 2000);
      return () => clearInterval(interval);
    };
    
    return () => ws.close();
  }, [jobId, batchId]);

  return { progress, connected };
}
```

### Template Selector
```typescript
// In send form
const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
const { data: templates } = useSWR('/api/templates', fetcher);

// When template selected, populate subject and body
useEffect(() => {
  if (selectedTemplate) {
    const template = templates?.find(t => t.id === selectedTemplate);
    if (template) {
      setSubject(template.subject);
      setBody(template.html_body);
    }
  }
}, [selectedTemplate]);
```

## Testing Checklist

- [ ] Login flow works
- [ ] Registration works
- [ ] Protected routes redirect to login
- [ ] Templates can be created/edited/deleted
- [ ] Template selector populates form
- [ ] Scheduling creates scheduled batch
- [ ] WebSocket connects and receives updates
- [ ] Polling fallback works if WS fails
- [ ] Analytics dashboard loads data
- [ ] Batch list shows all batches
- [ ] Retry failed works

## Notes

- All API calls go through Next.js proxy routes
- JWT stored in httpOnly cookies (secure)
- WebSocket uses same origin (no CORS issues)
- Fallback to polling for reliability
- Keep existing animated UI theme
- Maintain dark/light mode support
