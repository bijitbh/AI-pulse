# Hoichoi NL — Community Mobile App: Build Analysis

> Scope: a mobile app (iOS + Android) that mirrors the content and experience of **hoichoi.nl** — the Holland-e Hoi-Choi Bengali community association based in Amstelveen, NL. **Not** a clone of the unrelated Hoichoi OTT streaming product.

---

## 1. What hoichoi.nl Actually Is

A non-profit Bengali cultural association in the Netherlands, founded 2015. The website is a **community portal**, not a commercial product.

### Site sections (from public pages)
- **Home** — intro, upcoming-event banner, what's new
- **About** — history of Hoichoi, mission ("Bangaliana with camaraderie")
- **Our Team** — founding members + current committee
- **Events** — current year's flagship Durga Puja + smaller events through the year (Saraswati Puja, Poila Boishakh, Kali Puja, Christmas/New Year, picnics, etc.)
- **Past Events** archive — e.g. Durga Puja 2023, 2024 pages with photo galleries
- **Media publications** — press coverage / shared media
- **Testimonials** — community feedback
- **Contact** — committee email, social
- Social: Facebook (`HollandHoichoi`), Instagram (`hollandehoichoi`)

### Content / data on the site
- Static-ish copy (mission, history, committee bios)
- Event pages with date / venue / schedule / pricing
- Photo galleries (large image counts per event)
- A few embedded videos
- News / blog-style posts
- Some external links (sponsors, partners, press)

The site is almost certainly a **WordPress** site (the URL structure `/events/durga-puja-2024/`, `/our-team/`, etc., and the way page slugs/archives are organised, is classic WP).

---

## 2. What an App Adds Over the Website (the "Why")

A community website is fine for first-time visitors. An app is worth building when you want **regular, push-driven engagement** with returning community members. Specifically:

| Use case | App advantage over website |
|---|---|
| Event reminders | Native push notifications |
| Ticket / pass on-the-day | Saved digital pass, offline access at the venue |
| Photo galleries | Faster, native-feeling browsing; offline cache |
| Live event updates | Push + in-app banner |
| Two-way community | Comments, RSVPs, member directory |
| Quick contact | Tap-to-call, tap-to-WhatsApp, directions |
| Donations / contributions | Smoother flow than web form |
| Recurring annual return | Icon on home screen is sticky in a way a URL is not |

If you don't need those, a **Progressive Web App (PWA)** wrapping the existing site might be 95% of the value at 10% of the cost. See §10.

---

## 3. Feature Set

### MVP (4–6 weeks if cross-platform + headless CMS)
- **Home** — current/next event hero, quick links
- **About / Mission**
- **Our Team** — list with photos + roles + short bios
- **Events** — list of upcoming events; tap into event detail
- **Event detail** — date, time, venue (with map + directions button), schedule, ticket prices, "Add to calendar" button
- **Photo galleries** — by event / year
- **Contact** — email, WhatsApp group link, social links, venue map
- **Push notifications** — event reminders + new-photos-uploaded
- **Bilingual UI** — English + Bengali (Unicode, not images of text)
- **Share** — share event / photo to WhatsApp, Facebook, Instagram

### v1 (additional, +4–6 weeks)
- **RSVP / ticket purchase** — integrate with whichever payment / ticketing provider you use today (or move to a new one — see §6)
- **Digital ticket / pass** — QR code, saved offline, optional Apple Wallet / Google Wallet pass
- **Member sign-in** — optional; lets members see member-only content (committee announcements, AGM notes)
- **Donations** — one-tap contributions (Stripe / Mollie / iDEAL — relevant for NL)
- **Newsletter sign-up**
- **Testimonials** with submission form
- **Sponsors** page

### v2 (nice-to-have, post-launch)
- **Community feed** — Facebook/Instagram-style timeline curated by committee
- **Live updates** during multi-day events (Durga Puja schedule changes, kitchen menus, parking notes)
- **In-app live-stream** of cultural programmes (or just YouTube/FB embed)
- **Recipe / culture corner** — content marketing
- **Volunteer sign-up** for events
- **Lost-and-found / classifieds** for the local Bengali community
- **Multi-association federation** — same app shell shared with Kallol, Ohm BCA, etc. (each association = a "tenant")

---

## 4. The Single Most Important Build Decision

You have three viable paths. For a **community association**, the trade-off is very different from a commercial OTT product.

| Path | Effort | Cost / yr | UX | When to pick |
|---|---|---|---|---|
| **A. PWA** (mobile-friendly site + "Add to Home Screen") | ~1–2 weeks | ~€0 hosting | Good on Android, weaker on iOS (no push until iOS 16.4+, OK now) | Tiny budget, just want a mobile-feeling experience and push reminders |
| **B. Cross-platform native** (Flutter or React Native) | ~6–10 weeks for MVP+v1 | €50–200 / yr (stores + hosting + push) | Excellent on both | **Recommended.** Right balance for a community app |
| **C. Fully native** (Swift + Kotlin) | 2× option B | Similar runtime cost | Marginally better | Overkill — not justified |

**Strong recommendation: Path B with Flutter.** One codebase, native feel on iOS + Android, mature plugins for everything you need (maps, calendar, push, photo galleries, Stripe, Apple Wallet passes), and you can ship a polished app with 1–2 developers in 2–3 months.

If you're not paying anyone — i.e. this is a volunteer-built community project — seriously consider **Path A (PWA) first**. It's a weekend of work, gets the site on phone home screens, supports push on modern iOS and Android, and you can graduate to a real app later if engagement justifies it.

---

## 5. Architecture (assuming Path B — Flutter app + headless content)

```
┌────────────────────────────────┐
│  iOS / Android App (Flutter)   │
└──────────────┬─────────────────┘
               │ HTTPS (REST/GraphQL)
   ┌───────────┼───────────┬────────────────┐
   ▼           ▼           ▼                ▼
┌────────┐ ┌────────┐ ┌────────────┐ ┌──────────────┐
│ Content│ │ Auth   │ │ Payments / │ │ Push (FCM /  │
│  CMS   │ │(opt.)  │ │ Ticketing  │ │   APNs)      │
└───┬────┘ └────────┘ └────────────┘ └──────────────┘
    │
    ▼
 ┌────────────────────────┐
 │ Existing WordPress     │  ← reuse the site you already maintain
 │ (hoichoi.nl) via       │
 │ WP REST API / WPGraphQL│
 └────────────────────────┘
```

### Why reuse the existing WordPress site as the content backend
The committee already publishes content on hoichoi.nl. If you build a separate backend, **someone now has two places to publish** — that always breaks down in a volunteer-run org. Use WordPress as the **headless CMS**:

- Enable the built-in **WP REST API** (free) or install **WPGraphQL** (free)
- Add **ACF (Advanced Custom Fields)** to model events properly (date, venue, lat/lng, schedule items, ticket tiers)
- Add **Media Library** as-is for photo galleries
- The app reads JSON from `hoichoi.nl/wp-json/...`
- **Content updates instantly reflect in the app** — no app release needed

This is the lowest-friction path for a volunteer org.

### What the app stores locally
- Cached event list + photos (so the app works at the venue with patchy Wi-Fi)
- Saved tickets / passes
- Push notification token
- User language preference (EN / BN)
- (Optional) sign-in token

---

## 6. Tickets, Payments & Donations — Netherlands Specifics

You're in NL, so don't blindly copy India / US patterns.

- **iDEAL** is the dominant NL payment method — must be supported for donations and ticket sales (~70% of NL online payments).
- **Mollie** (Dutch payments company) is the easiest provider — iDEAL + cards + Apple Pay + Google Pay + Bancontact, with strong Flutter/RN SDK and clean API.
- Alternatives: Stripe (good iDEAL support since 2021), Adyen (overkill for community scale).
- **In-App Purchase rules**: Apple/Google require IAP only for **digital goods consumed inside the app**. Event tickets / donations to a registered non-profit can go via direct payment (Mollie/Stripe) — this is explicitly allowed under Apple's "physical goods/services" carve-out and Google's "physical events" carve-out. Big cost saver (no 15–30% store tax).
- **ANBI status?** If Hoichoi is a registered Dutch foundation (Stichting) with ANBI status, donations are tax-deductible — surface this in the donation flow.

### Existing ticketing
If you already sell Durga Puja tickets through a platform (Eventbrite / WeezEvent / custom WP plugin), keep that and just **deep-link** from the app to your existing checkout. Don't rebuild a ticketing system for a once-a-year event.

---

## 7. Push Notifications — the killer feature

The single biggest engagement win from going app-first.

- **FCM (Firebase Cloud Messaging)** handles both Android and iOS via one API
- Use **topics**, not individual tokens, to fan out without a server: e.g. `all-users`, `durga-puja-2026`, `lang-bn`, `volunteers`
- Committee posts via a simple admin panel (Firebase Console works for a few pushes a month, or a tiny custom form)

Typical push moments:
- 7 days before Durga Puja: "Tickets on sale"
- Day before: "See you tomorrow at Diamant Party Centrum — gates open 10:00"
- Live during event: "Cultural programme starts in 30 min in Hall 2"
- After event: "Photos are up — 240 new pictures from Day 3"
- Throughout year: "Saraswati Puja date confirmed — Feb 14"

---

## 8. Content / Data Modelling (WordPress + ACF)

Custom post types and fields to define:

| Post type | Key fields |
|---|---|
| **Event** | title, subtitle, start_datetime, end_datetime, venue_name, address, lat/lng, hero_image, gallery, schedule (repeater: time + activity + location), ticket_url, food_menu, dress_code, status (upcoming/past) |
| **Team member** | name, role, photo, bio, email, linkedin |
| **Testimonial** | author_name, author_photo, quote, year |
| **Media coverage** | publication_name, headline, date, url, excerpt, thumbnail |
| **Sponsor** | name, logo, tier (gold/silver/bronze), url |
| **Announcement** | title, body, posted_at, push_sent (bool) |
| **Photo gallery** | event reference, images (repeater), photographer credit |

The home screen of the app pulls: next `Event` (status=upcoming), 3 latest `Announcement`s, recent `Gallery` thumbnails.

---

## 9. Bilingual Support (EN + BN)

- **UI strings** — Flutter `intl` package with `en` + `bn` ARB files
- **Content** — translate at the CMS level. Two cheap options:
  1. **WPML** or **Polylang** WP plugins — proper multi-lingual content with parallel posts
  2. Cheaper: one field for English copy + one field for Bengali copy on each post, and the app picks based on user setting
- **Fonts** — bundle a proper Bengali font (e.g. **Hind Siliguri** or **Noto Sans Bengali** from Google Fonts) — system Bengali rendering is inconsistent across Android OEMs
- Allow the user to toggle language at any time from Settings, and remember the choice

---

## 10. PWA-First Alternative (recommended starting point)

Before committing to a real app, try this 1–2 weekend project:

1. Confirm hoichoi.nl is responsive (it likely already is)
2. Add a `manifest.json` with app name, icon, splash colours
3. Add a service worker — Workbox can generate one. Caches assets so the site loads instantly + works offline at the venue
4. Add **Web Push** (works on iOS 16.4+ once user adds to home screen, and natively on Android)
5. Optionally wrap with **PWABuilder.com** to publish as a Play Store and App Store listing

What you lose vs a real app: no Apple Wallet pass, no native maps deep-link, no slick gallery transitions, slightly worse offline. What you gain: shipping in days instead of months, no app-store review cycles, no rebuild for each platform.

A pragmatic phasing:
- **Phase 0 (this month):** ship the PWA. Measure: how many people install, how many enable push, how many open it during Durga Puja week.
- **Phase 1 (if metrics justify):** build the Flutter app and reuse the same WordPress backend.

---

## 11. Distribution

- **Google Play** — $25 one-time developer fee, ~3-day review the first time
- **Apple App Store** — $99/yr Apple Developer Program fee (or $0/yr if Hoichoi is a registered non-profit — Apple waives the fee for verified 501(c)(3) and equivalents; in NL this is the **ANBI** route, application form takes 4–6 weeks)
- Use **TestFlight** (iOS) and **internal testing track** (Android) to circulate beta builds to the committee before public launch
- Plan a soft launch ~6 weeks before Durga Puja so committee + active members can shake it down

---

## 12. Team & Timeline

This is a community project, so realistic options:

| Setup | Timeline to MVP | Notes |
|---|---|---|
| 1 volunteer Flutter dev (evenings/weekends) | 3–4 months | Most realistic if someone in the committee codes |
| 1 paid contractor part-time | 6–10 weeks | Budget €5k–€15k for a polished MVP + v1 |
| Off-the-shelf white-label event app (Eventee, Whova, Bizzabo) | 1–2 weeks | Cheaper short-term, but rents your community to a third party and locks you in. Not recommended for a long-running annual event. |

You don't need designers, PMs, QA, ops for a project this size. The committee plays those roles.

---

## 13. Indicative Costs

| Item | Cost |
|---|---|
| Apple Developer Program (waived with ANBI) | €0–€99/yr |
| Google Play Developer | ~€23 one-time |
| WordPress hosting (already paying) | unchanged |
| Firebase (push + analytics) | €0 (free tier covers community-scale) |
| Mollie (payments) | ~€0.29 per iDEAL transaction, ~1.8% + €0.25 per card |
| Domain / SSL | already covered |
| Optional: Mapbox or Google Maps tiles | €0 within free tier |
| Optional: Sentry crash reporting | €0 free tier |
| Build cost | €0 (volunteer) to €5k–€15k (contractor) |

Total recurring: **<€100/yr** if volunteer-built; the only real cost is the build itself.

---

## 14. Risks & Pitfalls

1. **Content goes stale** — if the committee doesn't post in WP, the app shows old content. Mitigation: build the CMS workflow so it's easier to post than to use Facebook (then both stay updated).
2. **Single-maintainer risk** — one volunteer builds it, then leaves; nobody can ship a new release. Mitigation: pick a boring, mainstream stack (Flutter + WordPress) so the next volunteer can pick it up.
3. **Apple/Google policy** — apps that are "just a wrapper around a website" sometimes get rejected. Add at least 3–4 native-feeling features (push, offline gallery, Wallet pass, native maps) to clear the bar.
4. **GDPR** — even a community app processes personal data (push tokens, sign-ins, photos of identifiable people). Publish a short privacy policy; honour delete-account requests.
5. **Photo consent** — galleries with identifiable community members raise consent questions. Add a "request removal" link on every gallery.
6. **Annual usage spike** — most traffic concentrates around the 5 days of Durga Puja. Cache aggressively so the app doesn't fall over.
7. **Bengali rendering on cheap Android phones** — bundle the font; don't rely on system default.

---

## 15. Recommended Path Forward

1. **Decide PWA-first vs. real app** (§10). If unsure, do the PWA first — you'll learn what people actually want before sinking months into a Flutter app.
2. **Audit hoichoi.nl content** — list every page, gallery, event archive. This becomes the data spec for the CMS model in §8.
3. **Add WPGraphQL + ACF** to the existing WP install. No app yet — just make the content app-ready.
4. **Spec the MVP** with the committee — agree on which 6–8 screens ship first.
5. **Build 2-screen prototype** (home + event detail) using Flutter against the live WP API. Demo to the committee. Iterate.
6. **MVP → committee TestFlight / internal track → public launch** at least 4 weeks before the next Durga Puja so it has time to bake.

---

## 16. One-Page Summary

For Hoichoi NL, this is a **community + events app**, not an OTT product — and the right build is small, cheap, and reuses the website you already maintain.

- **Stack:** Flutter app + existing WordPress as headless CMS (WPGraphQL + ACF) + Firebase push + Mollie for any payments
- **Effort:** 2–3 months for a polished MVP + v1, one developer
- **Cost:** under €100/yr to run; €0–€15k to build depending on volunteer vs. contractor
- **The killer feature:** push notifications around the annual Durga Puja and other events
- **Smart first step:** ship a PWA in a weekend before committing to a full app — most of the value, almost none of the cost

The biggest question to answer **before any code** is: do you have someone on the committee (you, or a volunteer) who will commit to building it and shipping a release once or twice a year? An unmaintained community app is worse than no app at all.
