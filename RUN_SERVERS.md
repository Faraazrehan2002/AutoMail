# How to Run Servers

## Recommended: Separate Terminals

Since your disk is full, run the servers in separate terminals (no need for `concurrently`):

### Terminal 1 - Backend
```bash
cd backend
uvicorn app.main:app --reload
```

### Terminal 2 - Frontend
```bash
cd web
npm run dev
```

## Verify

- Backend: http://localhost:8000/health
- Frontend: http://localhost:3000

## If You Want Concurrently Later

Once you free up disk space, you can:

```bash
# Install concurrently (optional)
npm install concurrently

# Then use from root
npm run dev
```

But running separately works perfectly fine and is actually easier to debug!
