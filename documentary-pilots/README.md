# Five Series, Five Pilots: Democracy Documentary Slate

Five investigative documentary series for YouTube, each with a 60-second pilot. They share one visual language: black frame, a single accent color, 3D data visualizations built in Blender, and AI-generated b-roll that is always labeled on screen.

The five series also fit together. Each one covers a different piece of the machinery democracy runs on:

| Layer | Series | One-line pitch |
|---|---|---|
| Information | **PINK SLIME** | Fake local news sites now outnumber real daily newspapers. Each episode follows the money behind one fake front page. |
| Administration | **THE COUNT** | The people who count your vote, and what it costs them. |
| Participation | **SERVER NATION** | Gen Z toppled governments from group chats. Then it had to run them. |
| Dissent and exile | **THE LONG ARM** | Governments hunting their critics across borders. |
| Privacy and assembly | **BROKERED** | Your location is for sale, including the fact that you showed up to a protest. |

---

## Greenlight recommendation

Scores run 1 to 5, and higher is better for every column. "Low cost" and "Low risk" are inverted, so 5 means cheap or safe.

| Series | Audience pull | Evergreen | Low cost | Low legal/safety risk | Ad-friendliness | Differentiation | **Total** |
|---|---|---|---|---|---|---|---|
| BROKERED | 5 | 5 | 4 | 3 | 4 | 3 | **24** |
| PINK SLIME | 3 | 4 | 5 | 3 | 4 | 4 | **23** |
| SERVER NATION | 4 | 3 | 2 | 3 | 3 | 4 | **19** |
| THE LONG ARM | 4 | 4 | 1 | 1 | 3 | 5 | **18** |
| THE COUNT | 3 | 2 | 2 | 3 | 4 | 3 | **17** |

These scores are my judgment, not measured data. The strongest evidence behind them is the cost and risk profile of each format. Audience pull is the least certain column: test it with the pilots before committing a budget (see "How to test" below).

**1. Flagship: BROKERED.** It has the best ratio of reach to cost. The hook is personal ("your phone"), it never goes stale, and the Blender city system built for the pilot can be reused in every episode. The risk is legal: buying location data as a reporting stunt needs a lawyer before you spend a dollar. Watch the sponsorship trap too. VPN and privacy-app sponsors will want this series, and taking their money conflicts with an investigation into the data economy.

**2. Fast follow: PINK SLIME, as a 3-episode limited run before the Nov 3, 2026 midterms.** It is the cheapest to make, because the reporting is desk work: domain records, FEC filings and ad libraries. It is also time-sensitive right now. The risk is defamation. Attribute every site to its funder only on documentary evidence, and cover left-leaning and right-leaning networks with equal rigor. The series' credibility depends on that.

**3. Develop with grant money: THE LONG ARM.** It is the most original and the most dangerous. Sources can be harmed by being identified. One production idea: use AI face-veils, as *Welcome to Chechnya* did, to anonymize sources with their consent and with on-screen disclosure. That turns this slate's AI toolset into a source-protection tool. It needs security protocols and a budget that ad revenue won't cover. Pitch it to journalism grant funders such as the Pulitzer Center.

**Hold: THE COUNT and SERVER NATION.** *The Count* needs embedded access inside an election office. With the midterms a month away, that access probably can't be negotiated in time. Plan it for 2028, or reshape it as a post-election certification story. *Server Nation* is strong, but it needs international field production or licensed protester footage, both slow and expensive. It could also launch as a cheaper explainer series built on public footage.

### Where this slate is weak

- **Trust in AI visuals.** Journalism channels lose credibility quickly when viewers spot unlabeled AI footage. The pilots label every AI shot. In the real series, use AI only for illustration, reconstruction and anonymization, never as stand-in "footage" of real events.
- **Synthetic narration.** The pilots use a free open-source voice (Piper TTS) as a placeholder. A human narrator, ideally the host, is a large step up in credibility for investigative work.
- **Advertiser-sensitive topics.** Protests, violence and elections can trigger limited ads on YouTube. Plan for memberships, grants and sponsorships that don't conflict with the reporting.

### How to test before committing

1. Upload all five pilots as Shorts and unlisted videos, and run a $50 to $100 ad test per pilot to a cold audience.
2. Compare 3-second hold rate, average view duration, and comment sentiment.
3. Greenlight the winner. If the data disagrees with my ranking, trust the data on audience pull, but not on legal risk.

---

## The pilots

Each pilot is 60.0 seconds long and follows the same structure:

1. A 3-second hook question.
2. Two AI-generated shots.
3. A Blender data visualization of the central statistic.
4. One more AI-generated shot.
5. The series title card over AI key art.
6. A sourced end card.

| Pilot | Hook | Blender visualization |
|---|---|---|
| PINK SLIME, Ep. 1: *The Front Page Nobody Wrote* | "Who wrote the last local story you read?" | Two towers of stacked newspapers, one slab per 10 outlets: 1,213 daily papers vs 1,265 pink-slime sites. Both grow at the same rate until pink overtakes. |
| THE COUNT, Ep. 1: *Night Shift* | "Who counts your vote?" | A hall of 100 empty chairs. 38 of them ignite red. |
| SERVER NATION, Ep. 1: *The Discord Prime Minister* | "Can a group chat choose a prime minister?" | A 275-seat parliament (the real size of Nepal's House) built of chat pixels, which light up as poll votes arrive. |
| THE LONG ARM, Ep. 1: *Nowhere Far Enough* | "How far is far enough?" | A globe with real coastlines (Natural Earth). Red arcs reach from the top three perpetrator states to host countries. Routes are labeled illustrative. |
| BROKERED, Ep. 1: *The Dot* | "Where were you last Tuesday?" | A city of moving phones. One hypothetical person is tracked home → place of worship → clinic → protest. Then every protester is traced back to where they live. |

Full narration scripts are in [`pipeline/pilots.py`](pipeline/pilots.py).

### Fact base (every on-screen number)

| Claim | Source |
|---|---|
| 1,265 partisan-funded "pink slime" sites vs 1,213 daily newspapers (June 2024) | [NewsGuard](https://www.newsguardtech.com/press/sad-milestone-fake-local-news-sites-now-outnumber-real-local-newspaper-sites-in-u-s/) |
| More than two local newspapers close per week | Northwestern Medill Local News Initiative, via [NewsGuard](https://www.newsguardtech.com/press/partisan-funded-websites-nearly-outnumber-daily-newspapers-in-us/) |
| 38% of local election officials threatened, harassed or abused; 60% concerned about federal election-security cuts (2025) | [Brennan Center](https://www.brennancenter.org/our-work/analysis-opinion/survey-finds-election-officials-want-more-support-amid-federal-cutbacks) |
| Nepal suspended 26 platforms on Sept 4, 2025; 74 dead by Sept 22 | [Britannica](https://www.britannica.com/event/2025-Nepalese-Gen-Z-Protests), [Al Jazeera](https://www.aljazeera.com/news/2025/9/9/nepal-lifts-social-media-ban-after-19-killed-in-protests-report) |
| Discord server with 130,000+ members; poll of 7,713 votes, Karki 3,833 (50%); sworn in Sept 12, 2025 | [Outlook India](https://www.outlookindia.com/international/how-discord-helped-revolutionise-nepal), [Al Jazeera](https://www.aljazeera.com/news/2025/9/15/more-egalitarian-how-nepals-gen-z-used-gaming-app-discord-to-pick-pm), [Kathmandu Post](https://kathmandupost.com/politics/2025/09/29/how-nepal-s-enraged-gen-z-turned-discord-into-a-political-arena) |
| March 5, 2026 election; 35-year-old former rapper Balendra Shah became prime minister | [Al Jazeera](https://www.aljazeera.com/news/2026/3/5/nepalese-vote-in-general-election-months-after-gen-z-uprising), [CFR](https://www.cfr.org/articles/in-nepal-gen-z-gets-a-victory-and-the-country-may-too) |
| 126 new physical transnational repression incidents in 2025; at least 54 governments; China, Vietnam and Russia top perpetrators | [Freedom House](https://freedomhouse.org/report/special-report/2026/collaboration-and-resistance-tracking-transnational-repression-2025) |
| Gravy Analytics/Venntel: 17B+ signals a day from ~1B phones (FTC allegation); Mobilewalla analyzed George Floyd protesters by race and home (FTC allegation), Dec 2024 | [The Record](https://therecord.media/ftc-location-data-brokers-gravy-venntel-mobilewalla), [CyberScoop](https://cyberscoop.com/ftc-data-broker-action-gravy-analytics-venntel-mobilewalla/) |

FTC claims are presented as allegations, because they come from complaints that ended in settlements, not court findings.

---

## Episode slates (season 1 candidates)

**PINK SLIME**
1. The Front Page Nobody Wrote: anatomy of one fake local site.
2. Both Sides of the Slime: left- and right-funded networks, side by side.
3. The Robot Newsroom: AI-generated local news sites.
4. Foreign Desk: state-backed fake US local outlets.
5. The Last Reporter: a town after its paper dies.
6. How to Read a Front Page: a viewer's verification toolkit.

**THE COUNT**
1. Night Shift
2. The Threat: tracing one threat back to its sender.
3. The Recount
4. Who Wants This Job?: the turnover crisis.
5. Certification
6. The Machines: what election equipment actually does.

**SERVER NATION**
1. The Discord Prime Minister (Nepal, 2025)
2. Aragalaya (Sri Lanka, 2022)
3. July (Bangladesh, 2024)
4. The Finance Bill (Kenya, 2024)
5. GenZ 212 (Morocco, 2025)
6. Three Weeks (Madagascar, 2025)
7. After the Hashtag: governing after the revolution.

**THE LONG ARM**
1. Nowhere Far Enough
2. The Favor: host-state collaboration.
3. Red Notice: abuse of Interpol notices.
4. Call Home: coercion by proxy, through family members.
5. The Station: covert overseas police posts.
6. Fighting Back: the laws and the people resisting.

**BROKERED**
1. The Dot
2. We Bought Ourselves: a lawful purchase of our own team's location data, with consent.
3. The Geofence: campaigns targeting worshippers and patients.
4. Warrantless: police buying what they'd need a warrant to seize.
5. The Breach: when the broker gets hacked.
6. Off Switch: what actually protects you.

---

## How the pilots were made

| Layer | Tool | Notes |
|---|---|---|
| AI b-roll (15 shots) | Higgsfield, Kling 3.0 (std, 5 s, 720p) | 7.5 credits each. No real people, flags or readable text. Every shot labeled on screen. |
| Key art (5) | Higgsfield, Nano Banana | 1 credit each. Used as the title-card background and YouTube thumbnail base. |
| 3D data visualization | Blender 4.2 (bpy), Cycles CPU | `pipeline/blender/b1_towers.py` … `b5_city.py`. Rendered at 960×540, 12 fps, then motion-interpolated to 24 fps. |
| Map data | Natural Earth 1:110m land | Public domain. |
| Narration | Piper TTS (`en_US-ryan-high`) | Free, local placeholder voice. |
| Score | Procedural synthesis (`pipeline/music.py`) | Original, royalty-free drone, heartbeat, riser and impact. |
| Edit, captions, graphics, grade | Python + Pillow + ffmpeg (`pipeline/compose.py`) | Burned-in captions, tracked 3D labels, sourced stats, vignette and grain, ducked mix at −15 LUFS. |
| Fonts | Bebas Neue, IBM Plex Mono, Inter | All under the SIL Open Font License. |

Total Higgsfield spend: 117.5 credits (15 × 7.5 + 5 × 1) of the 130 approved.

To rebuild: install `bpy==4.2.0`, `piper-tts`, `pillow`, `numpy`, `scipy` and ffmpeg. Then run, in order: `tts.py` → `timeline.py` → `music.py` → each `blender/b*.py anim` → `compose.py <pilot_id>`. The Higgsfield clips are not in the repo. Download them from the Higgsfield project "Documentary Pilots — Democracy Series Slate" into `hf/K1.mp4` … `K15.mp4` and `hf/A21.png` … `A25.png`.
