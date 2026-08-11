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

                    Telegram /start
                        ↓
                    Check telegram_accounts
                        ↓
                    Already linked?
                    /       \
                    YES       NO
                    ↓          ↓
                    Agent    Generate one-time token
                                ↓
                            Open L website
                                ↓
                            Clerk
                                ↓
                        Profile exists?
                            /          \
                        YES          NO
                        ↓            ↓
                        Link       Resume/Profile
                        ↓            ↓
                        └──────→ Link
                                    ↓
                                Return Telegram
----
#### User Flow Diagram
                Telegram /start
                    ↓
                🔐 Connect L
                    ↓
                Website /telegram?token=ABC
                    ↓
                Already logged in?
                ┌──────┴──────┐
                YES            NO
                ↓              ↓
                Connect       Clerk Sign up/Login
                ↓              ↓
                └──────┬───────┘
                        ↓
                    Telegram linked
                        ↓
                Profile ready?
                    ┌───┴───┐
                    YES      NO
                    ↓        ↓
                Telegram   Quick profile setup
                    ↓        ↓
                    └───→ Telegram    
----


                    ┌──────────────┐
                    │   Telegram   │
                    └──────┬───────┘
                           │
                         chat_id
                           ↓
                  telegram_accounts
                           │
                      clerk_user_id
                           ↓
            ┌─────────────┐     ┌──────────────┐
            │  Next.js    │────→│   FastAPI    │
            │  + Clerk    │     │              │
            └─────────────┘     └──────┬───────┘
                                    │
                                PostgreSQL
                                    │
                        ┌──────────────┼──────────────┐
                        ↓              ↓              ↓
                Profile       Recommendations    Jobs

---
            POST /telegram/connect

            1. Clerk user is authenticated ✅
            2. Token exists ✅
            3. Token isn't expired ✅
            4. Token isn't already used ✅
            5. Telegram isn't connected to another L account ✅
                ↓
            6. Create connection ✅
            7. Mark token used  ✅                