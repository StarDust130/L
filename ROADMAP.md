

# 🗺️ Development Roadmap

0. Backend foundation
   ├── FastAPI setup
   ├── Supabase/Postgres connection
   ├── Clerk auth
   ├── DB models/migrations
   ├── config + logging
   └── basic error handling

1. Worker 1 — Discovery 🔎
   └── Discover new job sources + fresh job URLs

2. Worker 2 — Ingestion 🕷️
   └── Fetch → parse → extract → validate → dedupe → DB

3. L Agent 🤖
   └── Agent loop + tools
       search_jobs
       get_job
       save_job
       preferences
       etc.

4. Worker 3 — Recommendation 🎯
   └── Match → rank → prepare daily recommendations

5. Telegram 📱
   └── webhook → same Agent → Telegram response

6. Frontend 🎨
   └── Jobs + Chat + minimal profile