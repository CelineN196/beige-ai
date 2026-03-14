                ┌─────────────────────────┐
                │     User Input Data     │
                │ mood                   │
                │ weather                │
                │ temperature            │
                │ humidity               │
                │ AQI                    │
                │ sweetness_pref         │
                │ health_focus           │
                │ trend_score            │
                │ time_of_day            │
                └─────────────┬──────────┘
                              │
                              ▼
                ┌─────────────────────────┐
                │   Feature Processing    │
                │ encoding + scaling      │
                └─────────────┬──────────┘
                              │
                              ▼
                ┌─────────────────────────┐
                │   K-Means Clustering    │
                │ Identify Customer Type  │
                │                         │
                │ Cluster Examples:       │
                │ • Dessert Lovers        │
                │ • Health Conscious      │
                │ • Trend Followers       │
                │ • Comfort Seekers       │
                └─────────────┬──────────┘
                              │
                              │ Add cluster_id
                              ▼
                ┌─────────────────────────┐
                │ Random Forest Model     │
                │ Classification Model    │
                │                         │
                │ Predict cake category   │
                └─────────────┬──────────┘
                              │
                              ▼
                ┌─────────────────────────┐
                │ Association Rule Mining │
                │ Discover behavior rules │
                │                         │
                │ Example:                │
                │ rainy + stressed →      │
                │ chocolate cake          │
                └─────────────┬──────────┘
                              │
                              ▼
                ┌─────────────────────────┐
                │ Hybrid Recommendation   │
                │ Engine                  │
                │                         │
                │ Combine:                │
                │ • RF prediction         │
                │ • cluster preference    │
                │ • association rules     │
                └─────────────┬──────────┘
                              │
                              ▼
                ┌─────────────────────────┐
                │ Top 3 Cake Suggestions  │
                │                         │
                │ 1. Matcha Zen Cake      │
                │ 2. Citrus Cloud Cake    │
                │ 3. Dark Chocolate Cake  │
                └─────────────┬──────────┘
                              │
                              ▼
                ┌─────────────────────────┐
                │ Gemini API (LLM Layer)  │
                │ Explain Recommendation  │
                │                         │
                │ "Because your mood is   │
                │ tired and weather rainy │
                │ matcha desserts are     │
                │ often preferred."       │
                └─────────────────────────┘

Layer 1 — Prediction AI
(Random Forest)

Layer 2 — Customer Intelligence
(K-Means Clustering)

Layer 3 — Behavior Discovery
(Association Rules)

Imagine these two customers:


mood	sweetness	health	trend
tired	8	2	0.3
tired	8	9	0.3
Without clustering they look similar.

But K-Means might detect:

customer	cluster
customer 1	sweet lovers
customer 2	health conscious