# Hoichoi Mobile App — Build Analysis

> Scope: what it takes to build a native iOS + Android app that replicates the content and experience of the Hoichoi platform (`hoichoi.nl` / `hoichoi.tv`).

---

## 0. Important Upfront Caveat — Legal / IP

Hoichoi is an existing commercial product owned by **SVF Entertainment Pvt. Ltd.** (operated via Hoichoi Technologies Pvt. Ltd.). The content catalogue (Bengali films, originals like *Byomkesh*, *Eken Babu*, *Feluda*, *Mandaar*, *Indubala Bhaater Hotel*, etc.) is licensed exclusively to them.

Before any engineering work, clarify which of these you actually mean:

| Scenario | What's allowed |
|---|---|
| **A. You are SVF / Hoichoi, or an authorised partner** rebuilding/refreshing their app | Full clone is fine; you have rights to the catalogue and brand. |
| **B. You are a regional affiliate** (e.g. Holland Hoichoi / hoichoi.nl) building a localised promo/companion app | You can build a **storefront / subscription-funnel / community app**, but must consume Hoichoi's official APIs or deep-link into their player — you cannot host or re-stream their video assets. |
| **C. You want a Hoichoi-*like* app** with your own Bengali content | Build the same architecture, but you must licence or produce your own catalogue. |
| **D. Pirating/mirroring the catalogue** | Not viable — copyright infringement, App Store / Play Store will reject and take down, and SVF will pursue takedowns/lawsuits. |

The rest of this document assumes **A or C** (you have rights to a catalogue). If it's **B**, the scope shrinks to ~30% of what's below — skip the video pipeline and DRM sections.

---

## 1. What Hoichoi Actually Is — Source Analysis

Bengali OTT (Over-The-Top) video-on-demand platform, similar in shape to Netflix / Hotstar but vertical-focused on Bengali-language content.

### Content types
- **Films** — 625+ Bengali movies (catalogue + new releases)
- **Web series / Originals** — 175+ shows, multi-season, episodic
- **Bangla Natok** — short-form Bengali tele-films / plays
- **Shorts & documentaries**
- **Trailers, teasers, behind-the-scenes**
- **Free-tier sampler** — selected films and first episodes of premium series

### Languages
- Bengali (primary)
- English + Bengali subtitles on most content
- **Bilingual UI** — user can switch the entire interface between English and Bengali

### Platforms supported (today)
- iOS, Android phones + tablets
- Web (`hoichoi.tv`)
- Smart TVs: Android TV, Samsung Tizen, LG webOS, Mi TV
- Streaming sticks: Roku, Amazon Fire TV, Apple TV
- Chromecast casting from mobile

### Streaming / playback features
- HD + 4K UHD streaming (adaptive bitrate)
- Dolby Atmos audio, Dolby Vision HDR on select titles
- **Offline downloads** (with licence expiry)
- Resume playback across devices (cross-device watch state)
- Subtitles toggle (EN / BN)
- Multiple audio tracks (where available)

### User-facing features
- Sign-up / sign-in (email, phone OTP, social — Google/Facebook/Apple)
- Profiles (multiple per account is common in OTT; Hoichoi today is mostly single-profile)
- Watchlist / "My List"
- Continue-watching rail
- Search (with filters: genre, year, language, cast)
- Recommendations (personalised + curated)
- Trailers preview
- Share to social
- **Parental control PIN**
- Ratings / age classification

### Commerce
- **Subscription tiers**: Monthly / Quarterly / Annual (prices vary by country/region — Hoichoi regionalises pricing based on licensing + FX + market)
- Promo codes / coupons
- Payment methods: Cards, UPI (India), Wallets (regional), PayPal (international), in-app purchase via App Store / Play Store billing on mobile
- Gift subscriptions / shared accounts
- Free trial flows

### Support / ancillary
- Help centre (`support.hoichoi.tv`)
- Account management, device de-authorisation
- Push notifications (new releases, episodes)
- Email / WhatsApp marketing opt-ins

---

## 2. Mobile App Feature Set — MVP vs. v1 vs. v2

Build in waves; don't try to ship everything at once.

### MVP (3–4 months)
- Auth: email + phone OTP + social login
- Browse: home rails, sections (Movies / Series / Originals / Natok), category pages
- Title detail page (synopsis, cast, episodes, trailer)
- Video player with adaptive bitrate, subtitles, resume
- Search (basic, by title)
- Subscription paywall + in-app purchase (Apple IAP + Google Play Billing)
- Watchlist
- Profile / account settings
- Push notifications
- English + Bengali UI

### v1 (months 5–7)
- **Offline downloads** with DRM-licensed expiry
- Chromecast (Android) + AirPlay (iOS)
- Continue-watching cross-device sync
- Search filters + genre browsing
- Recommendations rail (basic — popular + similar titles)
- Parental control PIN
- Promo codes redemption
- Share to social

### v2 (months 8–12)
- Personalised recommendations (ML-driven)
- Multiple user profiles per account
- 4K + HDR + Dolby Atmos (requires premium-tier device support)
- A/B-tested home page rails
- Live events / premieres
- In-app gifting
- Tablet-optimised layouts
- Smart TV companion (remote control / second screen)

---

## 3. Recommended Tech Stack

Pick **one** of the two paths. They have very different cost/quality trade-offs.

### Option A — Native (recommended for a serious OTT product)
| Layer | iOS | Android |
|---|---|---|
| Language | Swift 5.x | Kotlin |
| UI | SwiftUI + UIKit fallback | Jetpack Compose |
| Player | **AVPlayer** + FairPlay DRM | **ExoPlayer (Media3)** + Widevine DRM |
| Networking | URLSession + async/await | Retrofit + OkHttp + Coroutines |
| Persistence | Core Data / SwiftData | Room |
| DI | Swift built-ins | Hilt |
| Analytics | Firebase + Mixpanel / Amplitude | same |
| Crash | Firebase Crashlytics / Sentry | same |
| Push | APNs via Firebase | FCM |

**Why native**: video playback, DRM (FairPlay on iOS is iOS-only), offline downloads with licence persistence, Chromecast/AirPlay, and battery/CPU efficiency are all dramatically better natively. Every major OTT (Netflix, Disney+, Hotstar) is native for this reason.

### Option B — Cross-platform (faster, cheaper, with caveats)
- **React Native** or **Flutter**
- Player: `react-native-video` (uses AVPlayer/ExoPlayer underneath) or `video_player` + `better_player` in Flutter
- DRM works but requires native bridging on both platforms — you save less time than you'd hope
- Good for the MVP, but expect to drop to native for the player on v1+

**Recommendation**: Native (Option A). The player is the heart of an OTT app — don't compromise here.

---

## 4. Backend / Cloud Architecture

You aren't just building two apps — you're building (or consuming) a multi-tenant streaming backend.

```
                          ┌─────────────────────┐
                          │   Mobile Apps       │
                          │ (iOS + Android)     │
                          └──────────┬──────────┘
                                     │ HTTPS / JWT
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
       ┌────────────┐         ┌────────────┐         ┌────────────┐
       │  API GW    │         │   CDN      │         │  Identity  │
       │ (REST/GQL) │         │ (video +   │         │  / Auth    │
       └─────┬──────┘         │  artwork)  │         │  (OAuth)   │
             │                └──────┬─────┘         └────────────┘
   ┌─────────┼─────────┬──────────┐  │
   ▼         ▼         ▼          ▼  ▼
 Catalog  Playback  Subscription  Recs  DRM
 Service  Service    /Billing    Engine  License
                                         Server
   │         │         │          │      │
   └────┬────┴────┬────┴─────┬────┴──────┘
        ▼         ▼          ▼
     Postgres  Redis      S3 / GCS
     (catalog) (sessions, (mezzanine
                cache)     + HLS/DASH)
```

### Core services you (or your vendor) must run
1. **Identity / Auth** — JWT issuance, OTP via SMS gateway (Twilio / MSG91), social login federation, refresh tokens, device session management.
2. **Catalogue service** — Titles, episodes, seasons, cast, genres, artwork, metadata, search index (Elasticsearch / OpenSearch / Algolia).
3. **Playback service** — Returns signed manifest URLs (HLS `.m3u8` / DASH `.mpd`), validates entitlement, issues short-lived signed cookies for CDN.
4. **DRM licence server** — **Widevine** (Android/Chrome), **FairPlay** (iOS/Safari/Apple TV), **PlayReady** (Edge/Windows/Smart TVs). Almost always outsourced: **AWS Elemental MediaPackage + SPEKE**, **Bitmovin**, **Axinom**, or **Vualto**.
5. **Subscription & billing** — Reconciliation across Apple IAP, Google Play Billing, Stripe (web), regional payment gateways (Razorpay, Paytm). Webhook handling for renewals, refunds, grace periods.
6. **Recommendations** — Start with simple "more like this" + popularity; graduate to a collaborative-filtering model on watch history.
7. **Analytics pipeline** — Player heartbeats, QoS (buffering, bitrate drops, errors), engagement events. Tools: Conviva (industry standard for OTT QoS), Mux Data, or a self-built Kinesis/BigQuery pipeline.
8. **Notifications** — APNs + FCM, scheduled campaigns (OneSignal / Braze / CleverTap).

### Video pipeline (the big one)
You need a workflow that takes a delivered master and produces playable streams:

1. **Ingest** — upload mezzanine (ProRes / high-bitrate H.264) to S3.
2. **Transcode** — AWS MediaConvert / Bitmovin / Mux to ABR ladder (e.g. 240p / 360p / 480p / 720p / 1080p / 4K), separate audio tracks, subtitle WebVTT/IMSC, HDR variants where applicable.
3. **Package** — HLS (CMAF fMP4) for iOS/Apple, DASH for Android/web. Apply DRM encryption (CENC + SAMPLE-AES).
4. **Distribute** — Push to CDN (CloudFront / Akamai / Fastly).
5. **Manifest signing** — Per-session signed URLs / cookies.
6. **Quality control** — automated AQC plus manual spot check.

**Build vs. buy:** for an early-stage product, **buy** — use a managed OVP (Online Video Platform): **JW Player**, **Mux**, **Bitmovin**, **Brightcove**, or **AWS Elemental**. You can graduate to a self-managed pipeline later when the unit economics demand it.

---

## 5. Third-Party Services Checklist

| Need | Common choices |
|---|---|
| Auth / OTP | Firebase Auth, Auth0, Cognito; Twilio / MSG91 for SMS |
| Video encoding + packaging | AWS MediaConvert + MediaPackage, Bitmovin, Mux |
| DRM | AWS SPEKE, Axinom, Vualto, BuyDRM |
| CDN | CloudFront, Akamai, Fastly, Cloudflare Stream |
| Player SDKs | Bitmovin, JW, THEOplayer, ExoPlayer/AVPlayer + custom |
| Search | Algolia, Elasticsearch, Typesense |
| Subscriptions / receipt validation | RevenueCat, Adapty, Qonversion |
| Payments (non-store) | Stripe, Razorpay (India), PayPal |
| Push / engagement | Firebase Cloud Messaging, OneSignal, CleverTap, Braze |
| Analytics | Firebase, Mixpanel, Amplitude |
| Player QoS | Conviva, Mux Data, NPAW |
| Crash | Crashlytics, Sentry, Bugsnag |
| A/B testing | Firebase Remote Config, Optimizely, Statsig |
| Customer support | Freshdesk (Hoichoi uses this), Zendesk, Intercom |

---

## 6. Platform-Specific Gotchas

### iOS
- **FairPlay DRM** is mandatory for premium content on iOS — requires Apple's FPS deployment package (registered Apple developer org, NDA).
- **In-App Purchase is mandatory** for subscription unlock that's consumed inside the app (Apple takes 15–30%). You **cannot** link to your website to pay, except under the new "external link" reader-app entitlement — file an entitlement request, which OTT apps generally qualify for, but the UX is constrained.
- **AirPlay** — must implement properly or Apple will reject the build.
- **App Tracking Transparency** prompt is required if you use any tracking SDK.
- **Background download** for offline content needs `BGTaskScheduler` configuration.

### Android
- **Widevine L1** (hardware-backed) needed for HD+ DRM playback. Some low-end Android devices only have L3 — you'll need to gate quality accordingly.
- **Google Play Billing** required for digital subscriptions; rules similar to Apple's.
- **ExoPlayer (Media3)** is the de facto player — well-maintained, supports HLS + DASH + offline.
- **Foreground service** required for background audio / Chromecast persistence.
- **Different OEM behaviours** (MIUI, OneUI, ColorOS) on push notifications — test on Xiaomi/Realme handsets specifically for the India/Bengal audience.

### Both
- **Screenshot / screen-record protection** on premium content (FLAG_SECURE on Android; iOS UIScreen capture detection — there's no perfect block, but a known minimum to deter casual piracy).
- **Region locking** — content licensing is geo-bound; need IP-geolocation on the playback service and proper handling of VPN evasion.
- **Accessibility** — VoiceOver / TalkBack, dynamic type, captions are mandatory in many markets and good practice everywhere.

---

## 7. Compliance & Legal

- **Apple / Google content policies** — age ratings, parental controls, content warnings.
- **GDPR (EU/Netherlands-relevant)** — explicit consent banners, data export, right to delete, DPA with every processor.
- **Indian IT Rules 2021** — self-regulatory body classification (Hoichoi's primary market). Grievance officer + complaint portal required.
- **DPDP Act 2023 (India)** — data protection compliance.
- **CSAM scanning & moderation** — applies to UGC; less relevant if you have curated catalogue only.
- **Music licensing** — incidental rights for soundtracks already licensed via the film; original score is bundled with the film rights deal.
- **Subtitle accessibility** — required by some EU regulators for VoD services with EU establishment.

---

## 8. Team & Timeline (illustrative for MVP → v1)

| Role | FTE for ~8 months |
|---|---|
| Product Manager | 1 |
| Designer (UX/UI, motion) | 1 |
| iOS engineer | 2 |
| Android engineer | 2 |
| Backend engineer | 2–3 |
| DevOps / SRE | 1 |
| QA engineer (incl. device matrix) | 1–2 |
| Video/streaming engineer | 1 |
| Data / analytics | 0.5–1 |
| Content ops (catalogue mgmt) | 1 (ongoing) |

Total: **~12–15 people**, **8 months** to a polished v1 with offline + DRM + payments.
A leaner MVP (no offline, no DRM, single subscription tier) can ship in **3–4 months with 5–6 people** if you stay on managed services.

---

## 9. Indicative Costs (early-stage estimates)

| Bucket | Monthly (early scale: ~10–50k MAU) |
|---|---|
| Engineering team (loaded) | $80k–$150k |
| Cloud infra (compute, DB, storage) | $1.5k–$5k |
| CDN egress (the big one — scales with watch hours) | $3k–$30k+ |
| Video encoding / packaging | $1k–$5k |
| DRM licensing | $0.5k–$3k |
| Player QoS / analytics | $0.5k–$2k |
| Support tooling | $0.3k–$1k |
| Apple + Google dev accounts, certificates | trivial |
| Apple/Google take on subscriptions | **15–30% of subscription revenue** |

CDN egress is the dominant variable cost. Rule of thumb: **~$0.02–$0.08 per hour streamed at 1080p**, depending on CDN and region.

---

## 10. Key Risks

1. **DRM rejection on App Store / Play Store** — get the FPS deployment certificate early; the Apple paperwork can take weeks.
2. **In-app purchase reconciliation** — Apple/Google receipt validation is fiddly; use RevenueCat unless you have a strong reason not to.
3. **Geo / region pricing** — content licences often dictate per-region availability windows. You need a flexible entitlement model from day one.
4. **Performance on low-end Android** — Bengali audience skews towards budget Android handsets; test on devices with 2GB RAM, Widevine L3.
5. **Offline download licence expiry** — common source of customer-support tickets; bake clear UI for it.
6. **Subtitle quality** — auto-generated subtitles are not acceptable for Bengali; need professionally translated files per title.
7. **Cold-start recommendations** — first-time users get a generic shelf; design the onboarding to capture enough taste data to seed recs (genre picker, "pick 3 you've watched", etc.).

---

## 11. Suggested Next Steps

1. **Confirm legal scope** (the A/B/C/D question in §0). This unlocks or constrains everything else.
2. **Catalogue audit** — how many titles, what masters do you have, what's the encoding state, what subtitle files exist.
3. **Vendor shortlist** for OVP + DRM + IAP (RevenueCat) + analytics (Conviva/Mux). Get pricing.
4. **Design sprint** — 2-week clickable Figma prototype for the 4 hero flows: onboarding → browse → play → subscribe.
5. **Spike** on iOS FairPlay + Android Widevine playback against a sample DRM-encrypted asset. This is the technical heart of the app and should be de-risked first, before any UI is built.
6. **MVP scope lock** and sprint plan.

---

## 12. One-Page Summary

A Hoichoi-style mobile app is a **subscription OTT product**, not a content app. The hard parts are:

- **Video pipeline + DRM** (FairPlay on iOS, Widevine on Android)
- **Subscription handling** across Apple IAP, Google Play Billing, and regional gateways
- **Offline downloads** with licence expiry
- **Geo-restricted entitlement** model
- **QoS / CDN economics** at scale

The UI is the easy bit. Plan **6–9 months and 10–15 people** to a polished v1, or **3–4 months and 5–6 people** for a credible MVP that depends heavily on managed services (Mux/Bitmovin + RevenueCat + Algolia + Conviva). Native development is strongly recommended over cross-platform for any serious OTT product.

The **first decision** is not technical — it's whether you have the rights to the catalogue, or whether you're building a thin companion/affiliate app on top of Hoichoi's official platform. That answer reshapes everything below it.
