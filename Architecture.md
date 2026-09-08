
# L - Jobless Bot Architecture 😢
  
                         ┌──────────────────┐
                         │      USER        │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ↓                           ↓
                Next.js                     Telegram
                    │                           │
                    └─────────────┬─────────────┘
                                  ↓
                         ┌────────────────┐
                         │    FastAPI     │
                         └───────┬────────┘
                                 │
                    ┌────────────┴────────────┐
                    ↓                         ↓
             ┌──────────────┐         ┌──────────────┐
             │  L AGENT     │         │ REST APIs    │
             │ Orchestrator │         │              │
             └──────┬───────┘         └──────┬───────┘
                    │                        │
                    └──────────┬─────────────┘
                               ↓
                         ┌────────────┐
                         │  SUPABASE  │
                         │ PostgreSQL │
                         │ pgvector   │
                         │ Storage    │
                         │ Queue      │
                         └─────┬──────┘
                               │
             ┌─────────────────┼─────────────────┐
             ↓                 ↓                 ↓
       WORKER 1           WORKER 2           WORKER 3
       Discovery          Ingestion          Matching
             │                 │                 │
             ↓                 ↓                 ↓
          Web/Search       APIs/Crawlers      User profiles
          New sources      Job extraction     Ranking
          New jobs         Validation         Recommendations
                           Deduplication       Notifications