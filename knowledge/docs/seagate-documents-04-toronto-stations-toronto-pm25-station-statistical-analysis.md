---
source: archive/seagate/Documents/04. Toronto Stations/Toronto_PM25_Station_Statistical_Analysis.docx
aliases: []
sha256: 77f42f803433d7d1bb4c8430cb3af316b35ad37238baf769a072d60d9ed97fd7
converted: 2026-10-24
converter: markitdown
status: current
kind: mirror
---

**Toronto's PM2.5 Monitoring Network**

*A statistical analysis of all 10 NAPS and Ontario Provincial
stations, 2000–2025: data completeness, cross-station agreement,
and how CLEAR 2.0 should calculate one representative value for the city*

Companion notes, part 10 — September 2026

*The headline results:

All 10 Toronto stations, national and provincial alike, agree
strongly (r = 0.75–0.94) — there is no systematic disagreement
between the two networks.

But on real wildfire days, stations can differ by over 100 µg/m³
at the same hour, and real single-station local-pollution spikes
do occur in the historical record. Neither a simple average nor a
single robust statistic fully resolves this — the data points to
a two-stage Watch/Alert design instead of picking one formula.*

# 1. What This Document Covers

This analysis covers all 10 PM2.5 monitoring stations ever operated in Toronto by the two networks named in this project's raw data: the National Air Pollution Surveillance program (NAPS, 4 stations) and the Ontario Provincial air-quality network (6 stations, including two succession pairs where an old station was replaced by a new one at a nearby site). Source data: "Canada NAPS Hourly PM2.5 2000-2024 (whole year)" and "ON Provincial - Hourly PM2.5 - 2000-2025 (whole year)" in this project's RAW Data folder, read through this project's own verified cleaning pipeline (scripts/clean\_pipeline.py, scripts/build\_master.py) rather than re-parsed from scratch, since that pipeline's output (Cleaned Data/master/pm25\_hourly\_master.parquet) is the exact, already-validated product of those two raw folders.

Four questions are answered: how complete is each station's historical record, how closely do stations agree with each other (and does the national network agree with the provincial one), how large is the typical and worst-case disagreement between simultaneously reporting stations, and — using real examples from the data — what is the best way to combine multiple stations into one number for CLEAR 2.0's alert system.

# 2. Station Inventory: Years Active and Data Completeness

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| **Station ID** | **Network** | **First Year** | **Last Year** | **Years With Any Data** | **Mean Completeness** |
| NAPS\_60403 | NAPS | 2000 | 2002 | 3 | 36.3% |
| NAPS\_60413 | NAPS | 2002 | 2011 | 10 | 74.9% |
| NAPS\_60429 | NAPS | 2001 | 2013 | 12 | 58.5% |
| NAPS\_60435 | NAPS | 2010 | 2025 | 16 | 89.8% |
| ON\_31103 | ON Provincial (Downtown, retired 2020) | 2000 | 2020 | 21 | 90.0% |
| ON\_31129 | ON Provincial (Downtown, current) | 2019 | 2025 | 7 | 91.5% |
| ON\_33003 | ON Provincial (East) | 2002 | 2025 | 24 | 98.8% |
| ON\_34020 | ON Provincial (North, retired 2017) | 2000 | 2017 | 18 | 92.1% |
| ON\_34021 | ON Provincial (North, current) | 2017 | 2025 | 9 | 98.8% |
| ON\_35125 | ON Provincial (West) | 2000 | 2025 | 25 | 94.4% |

![](data:image/png;base64...)

*Years of activity and per-year data completeness for all 10 Toronto stations, both networks. Gaps in a bar mean the station had zero readings that year.*

* **Completeness is generally strong,**  especially for the currently-active stations: ON\_33003 and ON\_34021 both average 98.8% across their operating years, among the best in the network.
* **The 3 oldest NAPS stations (60403, 60413, 60429) have real gaps and much lower average completeness**  (36–75%), and all three stopped reporting entirely by 2013 — they no longer contribute to current Toronto air-quality monitoring.
* **Every ON Provincial station shows a real succession**: Downtown moved from ON\_31103 to ON\_31129 (2019–2020 handover), and North moved from ON\_34020 to ON\_34021 (2017 handover), each pair sited close enough together to be treated as one continuous role by this project's existing methodology.

# 3. How Closely Do the Stations Agree?

Pairwise Pearson correlation was computed for every station pair using only their simultaneously reporting hours (minimum 500 overlapping hours required).

|  |  |  |  |
| --- | --- | --- | --- |
| **Comparison** | **Number of Station Pairs** | **Mean Correlation (r)** | **Range** |
| NAPS ↔ NAPS (within national network) | 2 | 0.875 | 0.847 – 0.902 |
| ON Provincial ↔ ON Provincial (within provincial network) | 12 | 0.841 | 0.753 – 0.896 |
| NAPS ↔ ON Provincial (cross-network) | 17 | 0.865 | 0.796 – 0.939 |

|  |
| --- |
| **The key finding:** Cross-network correlation (NAPS vs. Ontario Provincial, mean r = 0.865) is just as strong as — in fact slightly stronger than — correlation within the provincial network alone (mean r = 0.841). There is no evidence the two networks systematically disagree or measure different things; a reading from a NAPS station and a reading from an Ontario Provincial station are about as comparable to each other as two Ontario Provincial stations are to each other. |

The single lowest correlation in the entire dataset is ON\_31129 ↔ ON\_35125 (Downtown vs. West, r = 0.753) — still a strong positive relationship, but a reminder that even within one network, the most geographically separated station pairs (roughly 13–15 km apart) track each other less tightly than closer pairs do.

# 4. How Large Is the Range of PM2.5 Differences Between Stations?

Using every hour where at least 3 of the 5 currently-active-era stations (ON\_31129, ON\_33003, ON\_34021, ON\_35125, NAPS\_60435) reported simultaneously (136,893 hours), the spread (highest minus lowest simultaneous reading) was computed for every hour:

|  |  |
| --- | --- |
| **Statistic** | **Spread (µg/m³)** |
| Median (typical hour) | 3.0 |
| 75th percentile | 6.0 |
| 90th percentile | 9.0 |
| 95th percentile | 11.0 |
| 99th percentile | 19.0 |
| Maximum observed | 180.0 (June 28, 2023, 21:00) |

|  |
| --- |
| **The critical finding for alert design:** On a typical hour, stations agree closely (median spread only 3 µg/m³). But on the 9 documented wildfire-event days, median spread jumps to 17.5 µg/m³ — nearly 6 times higher than normal — and the single worst hour (June 28, 2023, 21:00) saw readings of 48, 82, 95, 106, and 228 µg/m³ across 5 simultaneously reporting stations. Real wildfire smoke does not blanket every corner of Toronto identically; different neighbourhoods can experience genuinely different exposure at the same hour, even during a real, citywide event. |

# 5. Local Pollution vs. Wildfire Smoke — What the Data Actually Shows

The question posed for this analysis was specific: could a single high-reading station reflect local pollution rather than a real regional event? The data was searched directly for hours where exactly one station crossed the 60 µg/m³ High Risk threshold while the other simultaneously-reporting stations stayed well below it (median of the others under 30 µg/m³). 18 such hours were found across the full record — a real, if rare, pattern.

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **Date/Time** | **Elevated Station** | **Value** | **Other Stations** | **Likely Interpretation** |
| 2012-09-03 03:00 | ON\_33003 | 70 | 6–16 | Isolated single-hour spike, outside fire season — likely local |
| 2013-11-04 03:00–04:00 | ON\_35125 | 66–67 | 12–20 | Isolated 2-hour spike, November — likely local |
| 2021-06-16 05:00–06:00 | NAPS\_60435 | 60–79 | 2–5 | Extreme magnitude gap, 1-hour duration — likely instrument/local |
| 2023-01-03 03:00 | ON\_34021 | 62 | 19–22 | Isolated single-hour spike, January — likely local |
| 2025-07-05 16:00–20:00 | ON\_31129 | 61–106 | 16–23 | Sustained 5-hour rise, peaks at Very High, July — genuinely ambiguous |

*Most of these cases are easy to call: a single hour or two, far outside wildfire season, with no other station moving at all, is a strong local-pollution or instrument-noise signature. But the July 5, 2025 case is genuinely hard — a full 5-hour sustained rise reaching Very High (106 µg/m³), during wildfire season, that no other station corroborated. This is precisely the ambiguous case the CLEAR 2.0 alert system needs a defensible rule for, not just a judgment call.*

# 6. Testing Three Candidate Methods Against Real Data

Three ways of turning multiple simultaneous station readings into one Toronto value were tested against the same 136,893-hour dataset, all using CLEAR's 60 µg/m³ High Risk threshold:

|  |  |  |  |
| --- | --- | --- | --- |
| **Method** | **Total Hours Alerting** | **Hours Caught on Known Event Days (of 384)** | **False Alerts on the 18 Local-Outlier Hours** |
| A. Mean of all reporting stations (CLEAR's current method) | 125 | 125 | 0 |
| B. Median of all reporting stations | 139 | 135 | 0 |
| C. Hybrid: mean ≥60, OR at least 2 stations independently ≥60 | 166 | 157 | 0 |

* **None of the three methods produced a single false alert**  on the 18 identified local-outlier hours — at the actual 60 µg/m³ alert threshold, isolated single-station spikes in this dataset were not large enough on their own to trip any of the three rules except by also being caught correctly. This is a reassuring result, not a coincidence to rely on blindly — a future, larger isolated spike could still cross 60 on a single station.
* **The hybrid method catches the most real event hours**  (157 of 384, vs. 125 for the mean-only method) without adding any false alerts in this test, because requiring “2 stations independently high” is satisfied a little earlier in a real event's progression than waiting for the citywide mean to climb.
* **The median performed better than expected,**  catching more event hours than the mean (135 vs. 125) — not because it ignores outliers, but because with 5 stations, the median only needs 3 of them to be elevated, which happens before all 5 pull the mean up.

# 7. Recommendation: A Two-Stage Design, Not a Single Formula

**No single statistic perfectly resolves the tension in this data. A robust statistic (median, or requiring multiple stations to agree) protects against local-pollution false alarms, but the July 5, 2025 example shows it can also delay recognizing a real, sustained, dangerous reading if it happens to start at just one station. Given this project's own governing principle — if PM2.5 is high, an alert needs to be issued to protect people — under-alerting is the costlier mistake, and the recommendation below is built around not delaying a real warning.**

1. **Keep the mean as Toronto's primary reported value.**
2. It already matches CLEAR's documented methodology, and Section 3 confirms both networks agree closely enough (r = 0.75–0.94 throughout) that averaging active stations is statistically sound, not an arbitrary choice.
3. **Add an immediate single-station Watch trigger, separate from the public Alert.**
4. The moment ANY one station crosses 60 µg/m³, issue an internal/preliminary Watch — this guarantees the July 5, 2025 scenario is never silently missed, satisfying “if PM2.5 is high, alert.”
5. **Escalate to a full public Alert once corroborated:**
6. when either the multi-station mean also reaches 60, or a second station independently crosses 60 within a short window (the hybrid rule tested in Section 6, which caught 25% more real event-hours than the mean alone with zero false alerts in this dataset). This mirrors CLEAR's own already-documented alert algorithm, which calls for confirming wildfire attribution with independent evidence before a full public alert — this extends the same logic to station-to-station confirmation.
7. **Do not silently drop the outlier station's reading even at the Watch stage.**
8. Report which specific station is elevated and by how much — useful both for public transparency and for distinguishing a fast-moving localized event from later corroboration.

|  |
| --- |
| **Why not just switch to the median outright:** The median performed well in this backtest, but Section 6 also shows it depends on how many stations happen to be reporting at a given hour (it needs a majority elevated, not just one) — a property that is harder to explain on a public-facing alert system than “the average, confirmed by a second station.” The two-stage design keeps the well-understood, already-documented mean as the headline number while still closing the single-station blind spot the median was being considered to fix. |

# Appendix A: Verifying the Station Count — Are There Really Only 10 Toronto Stations?

This appendix was added after a direct check of the raw NAPS source file's own "Station Index" sheet, which lists 13 station IDs with City = "Toronto," not the 4 independent NAPS stations used in this analysis. This section documents exactly what those extra 9 IDs are and why the original 10-station count (4 NAPS + 6 Ontario Provincial) is correct.

## A.1 The 13 raw NAPS "Toronto" IDs, matched to their physical location

Every one of the 13 IDs was matched to its nearest Ontario Provincial station by exact coordinate distance:

|  |  |  |  |
| --- | --- | --- | --- |
| **NAPS ID** | **Nearest Provincial Station** | **Distance** | **Interpretation** |
| 60403 | — (9 km to nearest, in Mississauga) | n/a | Independent NAPS station (kept as NAPS\_60403) |
| 60410 | ON\_33003 (Toronto East) | 0 m | Same physical site — merged |
| 60413 | — (6 km to nearest, in Mississauga) | n/a | Independent NAPS station (kept as NAPS\_60413) |
| 60421 | ON\_34020 (Toronto North, old) | 4 m | Same physical site — merged |
| 60424 | ON\_31103 (Toronto Downtown, old) | 0 m | Same physical site — merged |
| 60429 | — (9 km to nearest, in Mississauga) | n/a | Independent NAPS station (kept as NAPS\_60429) |
| 60430 | ON\_35125 (Toronto West) | 0 m | Same physical site — merged |
| 60433 | ON\_31103 (Toronto Downtown, old) | 151 m | Same physical site — merged |
| 60435 | — (8 km to nearest, in Mississauga) | n/a | Independent NAPS station (kept as NAPS\_60435) |
| 60438 | ON\_35125 (Toronto West) | 185 m | Same physical site — merged |
| 60439 | ON\_31103 (Toronto Downtown, old) | 732 m | Same physical site — merged |
| 60440 | ON\_34021 (Toronto North, new) | 13 m | Same physical site — merged |
| 60445 | ON\_31129 (Toronto Downtown, new) | 3 m | Same physical site — merged |

|  |
| --- |
| **The explanation:** 9 of the 13 raw NAPS "Toronto" IDs sit within 1 km of an Ontario Provincial station already in this analysis — four of them match to within 13 metres, which is not "nearby," it is the same physical instrument. This is standard practice: a single monitoring station commonly reports simultaneously to both Environment Canada's national NAPS network and the Ontario provincial network. This project's own cleaning pipeline (scripts/build\_master.py) already has a documented rule for exactly this situation ("<1 km = same physical site") and merges these correctly, keeping the Provincial station identity and folding the NAPS readings in as a gap-filling source rather than double-counting one physical monitor as two separate stations. The remaining 4 IDs (60403, 60413, 60429, 60435) have no Provincial match within even 6 km and are the genuinely independent NAPS-only stations — exactly the 4 used throughout the rest of this document. |

**Conclusion: the original count of 10 distinct physical monitoring locations (4 independent NAPS + 6 Ontario Provincial, counting each succession pair once) is correct. Treating all 13 raw IDs as separate stations would double-count 9 physical locations.**

## A.2 Does Combining Both Streams Recover Additional Completeness?

Since the merged NAPS and Provincial streams for a shared site are separately submitted data, one could plausibly have valid readings for hours the other is missing. The existing pipeline already fills hours where the Provincial source has no row at all, but does not fall back to NAPS when a Provincial row exists with a null reading. This gap was tested directly against the raw pre-merge NAPS data.

|  |  |
| --- | --- |
| **Metric** | **Result** |
| Total additional hours recoverable (all 6 Provincial stations, 2003–2024) | 1,052 |
| As a share of existing valid data | ~0.12% |
| Station benefiting most | ON\_35125 (Toronto West) — 759 of 1,052 hours, from two co-located NAPS matches |
| Overlap with any of the 9 documented High Risk wildfire events | 0 hours |
| Recovered readings reaching Moderate tier (≥30 µg/m³) | 16 of 1,052 |
| Recovered readings reaching High Risk tier (≥60 µg/m³) | 0 |
| Mean / maximum recovered value | 8.4 / 53 µg/m³ |

|  |
| --- |
| **What this means for the rest of this document:** The gap is real but narrow — about 0.12% of data — and every recovered hour is a routine, background-level reading on an ordinary day. None fall on a documented wildfire event, and none reach the High Risk alert threshold. Combining the streams more completely would be a legitimate, small data-quality improvement, but it changes none of the correlation, spread, or alert-method conclusions reported in Sections 3–7 of this document — those results stand as reported. |
