                         L
                         │
             ┌───────────┴───────────┐
             │                       │
          🌐 Web                  📱 Telegram
             │                       │
        Clerk Auth                Telegram
             │                       │
        Resume/Profile               │
             │                       │
             └───────────┬───────────┘
                         │
                  👤 Identity
                         │
                  clerk_user_id
                         │
                  🧠 Agent Core
                         │
              ┌──────────┼──────────┐
              │          │          │
             Jobs      Profile    Tools
              │          │          │
              └──────────┼──────────┘
                         │
                    PostgreSQL
---

                    Website
                    ↓
                    Clerk login
                    ↓
                    Dashboard
                    ↓
                    [ Connect Telegram ]
                    ↓
                    Backend creates 8-digit OTP
                    ↓
                    Website shows OTP
                    ↓
                    User opens Telegram
                    ↓
                    Sends OTP
                    ↓
                    Backend verifies
                    ↓
                    telegram_chat_id ↔ clerk_user_id
                    ↓
                    ✅ Connected
                    ↓
                    Normal Telegram chat → LLM


                                   🏢 Companies
                                          ↑
                            discovery sources
                                          ↑
                            ┌────────────┼────────────┐
                            │            │            │
                            YC        founder data    manual
                            │
                            ↓
                     Career URL discovery
                            ↓
                     ┌──────┼────────┐
                     ↓      ↓        ↓
                     YC    Greenhouse Lever
                     ↓      ↓        ↓
                     └──────┼────────┘
                            ↓
                     Raw job listing
                            ↓
                     Normalize
                            ↓
                     Canonical Job
                            ↓
                     Job Listings
                            ↓
                     PostgreSQL
                            ↓
                     Rule Filter
                            ↓
                     AI Match
                            ↓
                     Recommendations
                            ↓
                     Telegram