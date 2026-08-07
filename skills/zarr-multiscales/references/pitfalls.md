# Multiscale pyramid failure catalogue

Symptoms first — most of these produce *plausible* output, which is what makes them
expensive. Ordered roughly by how much damage they do before you notice.

______________________________________________________________________

## 1. Work silently lost by striping + resume in the wrong order

**Symptom.** Every worker exits 0. Logs say `wrote N, skipped 0`. The scheduler
reports the whole array `COMPLETED`. But the level has fewer objects than tasks, and
the next level builds nodata holes on top of it.

**Cause.** Resume-filtering applied to the global task list *before* partitioning.
Concurrent workers list "already done" at different moments, so each filters to a
different-*length* list, and `tasks[i::N]` over different-length lists is not a
partition. Some tasks are claimed twice, others by nobody.

**Real numbers.** A level reported `wrote 22353, skipped 0` across six `COMPLETED`
array tasks while only **14,974 of 22,482** objects existed. Two of six stripes had
been starved to 77 and 54 tasks out of 3,747.

**Fix.** Stripe the stable manifest first, then filter within the stripe. Print
per-stripe resume counts (`N of this stripe already written, M remaining`) so the
arithmetic is auditable — the sums should reconcile exactly to the known gap.

**Detection.** Compare object count to manifest target per level. Also verify
first/middle/last of *every stripe* rather than random shards: random sampling can
miss an entire starved stripe, which is precisely what this bug produces.

**Why a contiguous test fixture hides it.** If your test's "already done" set is a
contiguous prefix, the tasks the bug drops coincide with the ones already written, and
the test passes vacuously. Model the done-set as *scattered* (each worker having
written a prefix of its own interleaved stripe).

______________________________________________________________________

## 2. Job success mistaken for data completeness

**Symptom.** A dependency chain (`afterok`-style job dependencies, resolved futures)
advances to the next level even though the parent is incomplete.

**Cause.** A job-dependency chain proves the parent's *processes* exited 0. It says
nothing about whether they wrote every shard.

**Fix.** A completeness gate in the builder: refuse to start unless the parent's real
object count equals its manifest target. Since each object maps to exactly one
required task, `count == target` is a total proof of no gaps and costs one listing.
Make it a gate, not just a report, so a misconfigured resume cannot bypass it.

______________________________________________________________________

## 3. Resampling that violates the data's semantics

**Symptom.** Coarse zooms look subtly wrong: class probabilities that no longer sum
to 1, label maps with classes that never existed, counts whose totals shrink.

**Cause.** `average` on categorical labels (class 1 and 3 do not average to 2);
`mode`/`max` on a probability simplex; `average` on counts.

**Fix.** Pick the operator from the invariant (see SKILL.md table). Record it in the
`multiscales` metadata as `resampling_method` so downstream readers know.

**Note.** Average pooling on a softmax needs **no renormalization** — the mean of
vectors each summing to 1 also sums to 1 by linearity. If you find yourself
renormalizing, you probably have a masking bug (#4), not a math problem.

______________________________________________________________________

## 4. Per-band nodata masks breaking a cross-band invariant

**Symptom.** Probabilities sum to 1 at full resolution but drift (0.97, 1.03) at
coarse levels, usually near coastlines or data edges.

**Cause.** Each band averaged over its own valid mask, so bands averaged over
*different* pixel sets within the same block.

**Fix.** A joint validity mask: a pixel contributes only if valid across every band.
Verify by asserting the nodata mask is identical across bands (all-or-nothing per
pixel) at every level.

______________________________________________________________________

## 5. Nodata bleeding into real data

**Symptom.** Coastlines creep outward at coarse zoom; the valid-data fraction grows
level over level.

**Cause.** Treating fill as a real value (averaging `0.0` or `-9999` in), or a
non-nodata-aware reduction.

**Fix.** Masked reduction; an all-nodata block stays nodata.

**Detection.** The coarsest level's valid fraction should match the source's
occupancy. If the source is 45.1% land, the top of the pyramid should be too.
Growth means bleeding; shrinkage means loss.

______________________________________________________________________

## 6. `np.nanmean` in a thread pool

**Symptom.** `RuntimeWarning: Mean of empty slice` sprayed through logs, or
intermittent warning-suppression failures.

**Cause.** All-nodata blocks legitimately produce NaN, and suppressing that requires
`warnings.catch_warnings()`, which mutates **global** interpreter state and is not
thread-safe. Pyramid builds are network-bound and usually threaded.

**Fix.** Explicit `sum/count` with `np.divide(..., where=counts > 0)`. Faster, no
warning, and the all-nodata result is intentional rather than silenced.

______________________________________________________________________

## 7. Half-pixel drift between levels

**Symptom.** Levels are offset from each other by half a pixel, growing with depth.

**Cause.** Mixing cell-center coordinates with pixel-edge transforms, or recomputing
the origin per level instead of keeping it fixed.

**Fix.** Pixel size scales by the factor; the **origin never changes**. Coordinates
are cell centers (`x0 + (i + 0.5) * dx`); `GeoTransform` is pixel-edge. Assert on
both per level.

______________________________________________________________________

## 8. Odd dimensions handled inconsistently

**Symptom.** Off-by-one shapes; a thin nodata seam on the right/bottom edge that
migrates between levels.

**Cause.** Mixing floor- and ceil-halving, or padding at a different corner than the
origin.

**Fix.** Ceil-halve (`(n + 1) // 2`) and pad at the *trailing* edge so the coarse grid
keeps the top-left origin. Compute each level's shape from the level-0 shape by
repeated ceil-halving, not from the previous level's padded array.

______________________________________________________________________

## 9. Credentials expiring mid-build

**Symptom.** A long job dies partway through with 403 / `ExpiredToken`, often hours in.

**Cause.** Temporary STS credentials fetched once at startup, with a lifetime much
shorter than the job (as low as ~40 minutes).

**Fix.** Request the maximum lifetime, and re-open the store every N tasks so a fresh
token is picked up. If the platform supports headless re-login, wire it in so batch
workers renew without a TTY.

______________________________________________________________________

## 10. Write races on partially-covered shards

**Symptom.** Rare corrupted or truncated shards under high concurrency.

**Cause.** Two workers writing regions of the *same* shard object, forcing
read-modify-write.

**Fix.** Align output shards to input shards so one task owns exactly one output
object. Work unit = one output shard.

______________________________________________________________________

## 11. Swallowing task exceptions

**Symptom.** A permanent hole in one region, with no error anywhere.

**Cause.** `try/except` around a shard task that logs and continues, so the scheduler
never retries and nothing marks the shard as missing.

**Fix.** Let exceptions propagate — fail the worker so the stripe is requeued. The
completeness gate then catches anything that slipped through.

______________________________________________________________________

## 12. Monitoring that cries wolf

**Symptom.** Alerts get ignored, so the real failure is missed.

**Cause.** Over-broad failure patterns. A bare `403` in a log grep matches the
throughput line `~403 MB/s`. Match HTTP statuses in context
(`status code: 4xx`, `<Code>...</Code>`).

**Also.** Do not discard stderr in a status poller — a credential failure then looks
identical to a slow listing. Capture it and emit an explicit failure line.

**Coverage.** A monitor that greps only for progress markers stays silent through a
crash. Ask: *if this died right now, would my filter emit anything?*
