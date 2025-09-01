### Backend (Python, async, real-time, rapid development):
- FastAPI: Modern, async, lightweight, and much faster to develop than Django. Native support for WebSockets, background tasks, and async endpoints.
- Auth: Use JWT (PyJWT) or integrate Clerk via API for authentication.
- Redis: For pub/sub, caching, and real-time notifications.
- PostgreSQL: Scalable, reliable relational database.
- Uvicorn: ASGI server for running FastAPI with async support.
- Celery (optional): For background jobs if you need scheduled or heavy tasks.

### Frontend (Mobile-first, rapid UI, scalable to desktop):
- React Native: For iOS/Android and future desktop expansion (via React Native macOS or React Native Windows).
- Expo: Rapid development, easy builds, OTA updates, and web support.
- TypeScript: For type safety and maintainability.
- React Query or SWR: For fast, cache-friendly data fetching and real-time updates.
- Socket.IO-client or native WebSocket: For real-time features.
- UI Kit: Use lightweight libraries like React Native Paper or NativeBase for rapid UI development.

### Why this stack?
- FastAPI is async by default, perfect for real-time and scalable APIs.
- React Native + Expo enables rapid mobile and desktop UI development.
- PostgreSQL + Redis is proven for scale and real-time features.
- Socket.IO/WebSocket gives you instant updates for games, chat, etc.
- TypeScript and modern UI kits speed up development and reduce bugs.