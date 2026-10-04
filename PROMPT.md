# Master prompt — Shillong Trip (shillongtrip.com)

> Role: a senior team in one — Northeast India travel strategist, UX/CRO lead, visual designer, front-end engineer, technical SEO + AEO specialist, and a destination expert who has driven the Guwahati–Shillong road in the rain, waited at the Kaziranga Central Range gate at 7 am and crossed Sela Pass in snow. Build the best travel website for **Meghalaya (Shillong, Cherrapunji, Dawki), Assam (Kaziranga, Majuli, Guwahati), Arunachal Pradesh (Tawang, Ziro, Mechuka) and the rest of the Northeast** (Nagaland, Manipur, Mizoram, Tripura).

## 1. Goal

1. Rank for "shillong trip", "meghalaya tour package", "shillong tour package", "kaziranga tour package", "tawang tour package", "northeast tour package", "arunachal tour package", and hundreds of long-tail, high-intent queries.
2. Be quoted by AI answer engines: answer-first summaries, fact tables, exactly 9 FAQs per content page, clean JSON-LD, `llms.txt`.
3. Convert: WhatsApp-first enquiries, lead capture with attribution, no dark patterns.

## 2. Brand and design — "Monsoon Modern" (must NOT resemble any other site we run)

- Brand: **Shillong Trip**. Voice: warm, local, practical; first person plural ("we").
- Feel: lush, rain-washed, confident and modern. Not editorial-serif, not maroon, not "Himalayan".
- Type: a characterful grotesk display face (Bricolage Grotesque) + a friendly humanist sans for body (Hanken Grotesk). No serif headlines.
- Palette: deep forest green, rain teal, tangerine accent, turmeric highlight, on a cool cloud-white page. Rounded, generous shapes (24–32 px radii), pill buttons, sticker-style tags.
- Layout language: split-screen hero with a stacked photo collage, bento grids, horizontal "state" tabs, image-left package cards, tabbed package pages, overlapping fact cards, a LIGHT footer with a big green call-to-action panel.
- Signature tools: route stepper on every package, "Rain meter" (monthly rainfall bars) on places, best-month heatmap (places × months), Northeast permit checker (ILP / PAP / RAP by state and passport), Kaziranga safari planner (zones, timings, season), trip budget builder, WhatsApp shortlist.
- URLs: `/packages/`, `/places/`, `/states/<state>/`, `/guides/`, `/trip-tools/`, `/styles/<theme>/`.

## 3. Content scope

| Type | Count | Each has |
|---|---|---|
| Places | 56 | quick answer, key facts, highlights, things to do, how to reach, where to stay, tips, permits, **9 FAQs**, nearby, credited photos |
| Packages | 60 | day-by-day with overnight altitude and drive, route, hotel tiers, inclusions/exclusions, indicative price, **9 FAQs** |
| Guides | ~63 | 1,800–2,400 words, answer-first, tables, internal links, **9 FAQs** |
| State hubs | 4 | Meghalaya, Assam, Arunachal, More Northeast |

## 4. Images

Wikimedia Commons only (CC0, PD, CC BY, CC BY-SA). Correct place, credited on the photo and on `/photo-credits/`. Processed to responsive WebP.

## 5. Writing rules

- Headings: no full stop at the end; short, one line on desktop.
- Plain, specific, numbers over adjectives (km, hours, metres, INR, months).
- Banned: nestled, breathtaking, hidden gem, paradise, tapestry, embark, delve, unleash, vibrant, bustling, mesmerizing, stunning, magical, "Scotland of the East" (at most once site-wide, in quotes), "abode of clouds" (at most once per page), "heaven on earth", "a feast for the eyes", "something for everyone", "whether you're", "look no further", "ultimate guide", "in this blog", "in conclusion".
- Facts that change (permits, Kaziranga season, Bum La, road status, festival dates, fees): state the rule and add "check current status before you travel".
- Prices are indicative "from" prices, INR per person, twin sharing, standard hotels.
- Never invent reviews, awards, statistics, founders or client counts. Byline: "Shillong Trip Travel Desk".
- Do NOT mention "Sikkim Tour Packages" or any sister brand.

## 6. Data schemas

### `content/places/<slug>.json`
```json
{
  "slug": "nongriat-root-bridges", "name": "Nongriat Double Decker Root Bridge",
  "state": "meghalaya",                 // meghalaya | assam | arunachal | northeast
  "state_name": "Meghalaya",            // actual state for northeast entries: Nagaland, Manipur, Mizoram, Tripura
  "district": "East Khasi Hills",
  "types": ["trek", "root-bridge"],
  "tagline": "≤70 chars, no full stop",
  "altitude_m": 700, "coords": [25.2472, 91.6760],
  "best_months": [10,11,12,1,2,3],
  "best_time": "One sentence",
  "permit": { "required": false, "indians": "…", "foreigners": "…" },
  "from_hub": { "hub": "Shillong", "km": 60, "hours": "2.5" },
  "ideal_stay": "1 night in Nongriat or 2 in Sohra",
  "meta_description": "≤158 chars",
  "quick_answer": "40–60 words",
  "intro": ["para", "para"],
  "highlights": [{ "name": "…", "text": "…" }],
  "things_to_do": ["…"],
  "how_to_reach": "60–120 words", "where_to_stay": "60–120 words",
  "tips": ["…"],
  "faqs": [{ "q": "…", "a": "…" }],     // exactly 9
  "nearby": ["slug"],
  "image_query": "Commons search terms"
}
```

### `content/packages/<slug>.json`
```json
{
  "slug": "meghalaya-classic-4n", "title": "…", "nights": 4,
  "themes": ["family"], "states": ["meghalaya"],
  "places": ["shillong", "sohra"], "hero": "nohkalikai-falls",
  "price_from_inr": 15500, "best_months": [10,11,12,1,2,3,4],
  "difficulty": "easy", "max_altitude_m": 1965,
  "start": "Guwahati Airport (GAU)", "end": "Guwahati Airport (GAU)",
  "meta_description": "≤158 chars incl. 'N nights / N+1 days'",
  "quick_answer": "40–60 words", "overview": ["para", "para"], "highlights": ["…"],
  "itinerary": [ { "day": 1, "title": "…", "stay": "Shillong", "altitude_m": 1525, "drive": "100 km · 3 hrs", "text": "80–150 words", "meals": "Dinner" } ],
  "inclusions": ["…"], "exclusions": ["…"],
  "hotels": [{ "tier": "Standard", "options": "…" }, { "tier": "Premium", "options": "…" }, { "tier": "Luxury", "options": "…" }],
  "good_to_know": ["…"], "faqs": [{ "q": "…", "a": "…" }]
}
```
Note: the day-by-day array is called **`itinerary`** (not `days`). Day count = nights + 1.
Themes: `honeymoon, family, luxury, budget, trekking, adventure, culture, offbeat, wildlife, festival, monsoon, snow, photography, short-break, seniors, solo, international, tea`.

### `content/guides/<slug>.md`
YAML front matter: `title` (≤60, no full stop), `slug`, `keyword`, `description` (≤158), `category` (Planning | Itineraries | Places | Stays | Seasons | Wildlife | Culture | Food | Treks), `date`, `updated: "2026-09-30"`, `read_minutes`, `places: [slugs]`, `packages: [slugs]`, `quick_answer`, `key_takeaways`, `faqs` (exactly 9). Body in Markdown, internal links as `/places/<slug>/`, `/packages/<slug>/`, `/guides/<slug>/`.

## 7. Slug registry

`content/_plan.json` is the single source of truth for every slug and internal link.
