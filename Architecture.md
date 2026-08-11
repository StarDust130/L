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