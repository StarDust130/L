

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
                         ↓
                      👤 User
                           ↓
                      🎯 Goal / Profile
                           ↓
                        L Agent
                           ↓
                   ┌───────┴────────┐
                   ↓                ↓
              Research          Matching
                Agent              Agent
                   ↓                ↓
               Tools              Tools
                   ↓                ↓
             Web / APIs         PostgreSQL
                   ↓                ↓
                  └───────┬────────┘
                          ↓
                    Recommendations
                          ↓
                       Telegram

---

               (L Bhiaya Agent Loop 🕺)

                     🎯 USER GOAL
                         ↓
                    🧠 L AGENT
                         ↓
                "What should I do?"
                         ↓
              ┌──────────┴──────────┐
              ↓                     ↓
          🔎 Research             💾 Data
             Tools                 Tools
              ↓                     ↓
       search / fetch /       save / update /
       extract / discover     dedupe / query
              └──────────┬──────────┘
                         ↓
                     🔍 OBSERVE
                         ↓
              "Do I have enough?"
                 ↙             ↘
               NO               YES
                ↓                 ↓
           use another tool    finish
                ↓                 ↓
                └────── loop ─────┘

---
               1. Need candidate profile
               → get_my_profile()

               2. Need companies/jobs
               → search_web()

               3. Found a company
               → inspect_company()

               4. Need career page
               → find_career_page()

               5. Found jobs
               → extract_jobs()

               6. Need more candidates?
               → search again

               7. Have enough good jobs?
               → deduplicate()

               8. Save useful results
               → save_job()

               9. Rank for user
               → match_jobs()

               10. Return best 5–10 

----

                              🧠 L
                                   │
                    ┌───────────────┴───────────────┐
                    ↓                               ↓
          🔎 Source Discovery              🔄 Source Monitor
          "Find NEW sources"              "Check KNOWN sources"
                    │                               │
                    ↓                               ↓
               Sources                         Sources
                    └───────────────┬───────────────┘
                                   ↓
                              💼 Job Discovery
                                   ↓
                              🧹 Validate
                                   ↓
                              ♻️ Deduplicate
                                   ↓
                              Jobs DB
                                   ↓
                              🎯 Match
                                   ↓
                         Recommendations
                                   ↓
                         📱 Telegram               