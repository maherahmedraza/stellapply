---
description: How to open Chrome browser for testing in WSL
---
// turbo-all

1. Run the Chrome debug script to open the browser:
```bash
bash /home/maher/projects/stellapply/start-chrome-debug.sh
```

2. The browser will open with remote debugging enabled on port 9222. You can then navigate to:
   - Frontend: http://localhost:3000
   - Backend API docs: http://localhost:8000/docs
   - Keycloak admin: http://localhost:8081
   - MinIO console: http://localhost:9001
