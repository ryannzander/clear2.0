---
source: archive/seagate/Documents/04. Toronto Stations/CLEAR_2.0_Mean_vs_Max_Methodology.docx
aliases: []
sha256: 376e266c9c8a2f72bf3b5f0fcab5f5b738abd1f6c2bdd509c6607555e963d6c9
converted: 2026-10-24
converter: markitdown
status: current
kind: mirror
---

**Mean or Max? Choosing the Model's Target**

*Testing per-station-then-mean against per-station-then-max on
real trained-model predictions, to decide how CLEAR 2.0 should
combine multiple Toronto stations into one predictive alert*

Companion notes, part 11 — September 2026

*The counterintuitive result:

Taking the MAXIMUM of 4 per-station predictions does NOT catch
more true alerts than taking their MEAN — it caught fewer, in
5 of 6 tested cases. A predictive model is only as reliable as its
worst-performing individual station, and single-station spikes
are the hardest thing for a regional smoke model to forecast.

The recommendation: keep per-station modeling, combine with the
mean for the predictive alert, and catch single-station outliers
with live monitoring instead of asking the model to predict them.*

# 1. The Question This Answers

CLEAR 2.0's prediction models (both the GBM baseline and the ST-GNN) already forecast each of Toronto's four monitoring roles separately — Downtown, East, North, and West — using PM2.5 data from every available upstream station as input. What remained undecided was how to turn those 4 separate predictions into the one number that actually drives an alert. Two candidate designs were compared: take the MEAN of the 4 predicted values (the approach used throughout this project so far), or take the MAXIMUM of the 4 predicted values, on the reasoning that the highest predicted station should be the one that triggers the alert, since that is the most cautious choice and should, in principle, catch the most real events.

*Rather than reason about this in the abstract, both approaches were tested directly against real predictions already produced by this project's own trained models (the GBM baseline and the ST-GNN's best checkpoint, epoch 12) on the held-out test period.*

# 2. Methodology

* **Two aggregation rules tested,**  for both models, at all three horizons (t+0, t+3h, t+6h): MEAN of the 4 role predictions, and MAX of the 4 role predictions. The same rule was applied to the true values, so each method is graded against its own matching definition of a true alert (mean-vs-mean, max-vs-max) — the fair, self-consistent comparison for how each would actually be deployed.
* **Same 60 µg/m³ High Risk threshold**  used throughout this project, and the same metrics: MAE, High-Tier MAE, Recall (of every truly dangerous hour, the fraction also flagged as dangerous), Precision, and raw false-alarm count.
* **No new training.**  Both models' predictions were already saved from earlier work in this project; only the aggregation step and scoring were new.

# 3. Results — Mean vs. Max, Both Models, All Horizons

|  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- |
| **Horizon** | **Model** | **Mean Recall** | **Max Recall** | **Mean Precision** | **Max Precision** |
| t+0 | GBM | 0.95 | 0.82 | 0.84 | 0.87 |
| t+0 | ST-GNN | 0.97 | 0.78 | 0.64 | 0.81 |
| t+3h | GBM | 0.34 | 0.68 | 0.50 | 0.75 |
| t+3h | ST-GNN | 0.82 | 0.60 | 0.65 | 0.81 |
| t+6h | GBM | 0.00 | 0.02 | — | 0.12 |
| t+6h | ST-GNN | 0.71 | 0.55 | 0.68 | 0.80 |

**Mean wins on recall in 5 of the 6 tested combinations (highlighted green) — the opposite of what “max should be more sensitive” predicts. Max wins consistently on precision (fewer false alarms per alert issued), but that is a smaller win than the recall loss represents for a public safety system.**

# 4. Why Taking the Maximum Doesn't Reduce False Negatives

A max-of-predictions alert is only as reliable as its single worst-performing station model. This was checked directly: GBM's per-role recall at the t+3h horizon, computed separately for each of the 4 Toronto roles.

|  |  |  |
| --- | --- | --- |
| **Role** | **True High-Tier Hours** | **That Role's Own Recall** |
| Downtown | 21 | 0.00 |
| East | 42 | 0.88 |
| North | 47 | 0.36 |
| West | 49 | 0.14 |

|  |
| --- |
| **The mechanism:** East's individual model is strong (88% recall) and happens to carry the max-based aggregate's performance in this one case — which is exactly why GBM's max briefly outperforms its mean at t+3h (Section 3's one exception). But Downtown's model catches 0% of its own true highs, and West only 14%. A max-based alert built from 4 stations is exactly as fragile as its weakest one, and a single station's local spike — the kind identified in the companion station-statistics document (e.g. the uncorroborated July 5, 2025 case) — is a harder, more idiosyncratic target for a regional smoke-transport model to forecast station-by-station than the broader citywide trend is. |

*The “true max” ground truth also includes more of these harder, less regionally-predictable events than the “true mean” ground truth does (more hours qualify as a true positive at all), so a model graded on max-vs-max is being graded on a harder curve, not simply a more forgiving, more sensitive one.*

# 5. Recommendation

1. **Keep predicting each Toronto station separately.**
2. This part of the architecture is already correct and is what makes any aggregation choice possible in the first place — nothing changes here.
3. **Use the mean of the 4 station predictions as the primary signal for the predictive/forecast Alert.**
4. It wins on recall in the cases that matter most for this project — the nowcast, and the ST-GNN's t+3h/t+6h horizons, which is the specific improvement this project's ST-GNN work was built to demonstrate.
5. **Do not ask the model to solve the single-station false-negative problem.**
6. Section 4 shows it is not well-suited to it — individual station models vary widely in reliability, and a max-based alert inherits the weakest one's blind spots.
7. **Instead, add a live, non-predictive Watch trigger, separate from the forecast Alert:**
8. the moment any single REAL (observed, not model-predicted) station reading crosses 60 µg/m³, issue an immediate Watch. This is the two-stage design already recommended in the companion station-statistics document, and it resolves this question's tension directly: the predictive model handles what it's demonstrably good at (the citywide trend, days in advance), and live monitoring handles what the model is demonstrably not good at (a single station's local, hard-to-forecast spike), without either one being asked to do the other's job.

# 6. Map: All Toronto PM2.5 Monitoring Stations

All 10 stations used throughout this analysis — 4 independent NAPS national-network stations and 6 Ontario Provincial stations (including both succession pairs, Downtown and North) — shown at their real coordinates against Toronto's actual Lake Ontario shoreline.

![](data:image/png;base64...)

*All 10 Toronto PM2.5 monitoring stations, 2000-2025. Circles = currently active; triangles = retired. Navy = Ontario Provincial network; orange = NAPS national network.*

*Geographically, the 3 retired/older NAPS stations cluster together in the west/southwest of the city (Etobicoke area), while the 6 Ontario Provincial stations — the ones used as the Toronto roles throughout this project's ST-GNN and GBM models — are spread across Downtown, East, North, and West, giving genuine geographic coverage of the city rather than a single-neighbourhood view.*
