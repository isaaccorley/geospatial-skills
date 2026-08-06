---
name: planet-bulk-download
description: Download PlanetScope imagery at scale (hundreds to 100k+ AOIs) via the Planet Python SDK v2. Covers search/activate/extract phases, COG /vsicurl/ vs Orders API, GDAL config for signed URLs, retry logic, concurrency budgets, and Planet-side gotchas (broken activations, cold-storage thaw tails, dead assets). Use when downloading at scale, hitting 429s or stuck activations, choosing Orders API vs COG reads, or designing a resumable batch Planet pipeline.
---

# Planet Bulk Download

Hard-won reference for pulling PlanetScope imagery at scale with the Planet SDK v2. The SDK is thin: no retries, no batching, no awareness of cold-storage thaw, no scene grouping. You build all of that. This document is the part you will otherwise rediscover by burning a 17-hour batch job.

## Architecture: three-phase pipeline

Split the job into **search → activate → extract**, each with its own JSONL cache, its own concurrency knob, and its own resume logic. The phases have completely different bottlenecks:

- **search**: cheap metadata calls, rate-limited client-side.
- **activate**: Planet-side cold-storage thaw queue, capped at ~10 cold scenes/min/account regardless of how many you request.
- **extract**: HTTP range reads via GDAL, network-bound at ~0.5s/patch on a 1.5km AOI.

Suggested layout:

```
_global/
  manifest.jsonl                 # input AOIs, one per line
  search/shard_NNN.jsonl         # per-AOI search results
  activations.jsonl              # item_id -> signed URL, append-only
  extract/shard_NNN.jsonl        # per-patch extract status
```

Phase a re-activation pass after the first extract pass (see Reliability Gotchas below).

### Scene grouping is the activation budget killer

Many patches share scenes (mean ~23 patches/scene in practice). **Group all patches needing scene `S`, activate `S` once, then read every patch's window from the warm URL.** Cuts activations 10-20x.

```python
from collections import defaultdict
scene_to_patches = defaultdict(list)
for patch in patches:
    scene_to_patches[patch.item_id].append(patch)
# Activate keys once; extract reads many windows per key.
```

### Sharded array jobs

For search and extract, shard by patch index. Aim **1-5k entries per shard** so a single shard finishes in 10-30 min (good for walltime budgeting and partial-progress visibility).

```python
shard_id = hash(item_id) % num_shards   # for extract: keeps same scene in same task
```

Hash by `item_id` for extract so the same scene is always processed by the same task — GDAL's `/vsicurl/` cache stays warm across patches.

## COG range-reads beat the Orders API by ~100x

PSScene `ortho_analytic_4b_sr` has been a Cloud-Optimized GeoTIFF since ~2022. After `:activate`, the signed `location` URL supports HTTP range reads via `GDAL /vsicurl/`. For **windowed access** (anything less than a full strip), the Orders API queue + clip-tool path is dramatically slower and adds another queue to fail through.

Use the Orders API only when you need full-strip downloads or server-side reprojection you cannot do locally.

```python
import rasterio
from rasterio.windows import from_bounds

url = activation_row["location"]            # signed Planet URL with ?token=
vsicurl_url = f"/vsicurl/{url}"
with rasterio.Env(**GDAL_OPTS):
    with rasterio.open(vsicurl_url) as src:
        window = from_bounds(*patch_bounds, transform=src.transform)
        data = src.read(window=window)
```

## GDAL config for /vsicurl/ COG reads

Apply via `rasterio.Env(**opts)`. **Pass numeric values as Python ints, not strings** — `GDAL_CACHEMAX` and a few others go through C funcs that require int. Strings silently break with cryptic errors.

```python
GDAL_OPTS = dict(
    GDAL_HTTP_VERSION="2",
    GDAL_HTTP_MULTIPLEX="YES",
    GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
    CPL_VSIL_CURL_USE_HEAD="NO",
    GDAL_INGESTED_BYTES_AT_OPEN=32768,           # int
    GDAL_HTTP_MERGE_CONSECUTIVE_RANGES="YES",
    GDAL_CACHEMAX=1024,                          # int, MB
    VSI_CACHE="TRUE",
    VSI_CACHE_SIZE=67108864,                     # int
)
```

**Critical: do NOT set `CPL_VSIL_CURL_ALLOWED_EXTENSIONS`.** Planet's signed URLs end with `?token=...`, not `.tif`. The extension allowlist will reject them. Half a day was lost to this.

## Retry logic (the SDK has none)

Wrap every Data API call — `search`, `list_item_assets`, `activate_asset`, `wait_asset` — in a retry that handles all of:

- `planet.exceptions.TooManyRequests` (429). Exponential backoff starting 0.5s, cap 30s, ~8 attempts. Planet does not send `Retry-After`; pace yourself.
- `planet.exceptions.APIError` whose message contains `"503"`, `"502"`, `"504"`, or `"Server Error"`. Same backoff. The SDK does not expose a clean status code on all error paths — heuristic match on the message string is required.
- `httpx.ConnectTimeout`, `httpx.ReadTimeout`, `httpx.ConnectError`, `httpx.RemoteProtocolError`, `httpx.ReadError`. All happen on multi-hour runs.

```python
import asyncio, random
import httpx
from planet.exceptions import TooManyRequests, APIError
from typing import Any, cast

TRANSIENT_HTTPX = (
    httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError,
    httpx.RemoteProtocolError, httpx.ReadError,
)

async def with_retry(fn, *args, max_attempts=8, base=0.5, cap=30.0, **kw):
    for attempt in range(max_attempts):
        try:
            return await fn(*args, **kw)
        except TooManyRequests:
            pass
        except APIError as e:
            msg = str(e)
            if not any(s in msg for s in ("503", "502", "504", "Server Error")):
                raise
        except TRANSIENT_HTTPX:
            pass
        delay = min(cap, base * (2 ** attempt)) * (0.5 + random.random())
        await asyncio.sleep(delay)
    raise RuntimeError(f"retry exhausted: {fn.__name__}")
```

`sess.client("data")` returns an `Any`-typed object that breaks static checkers. Cast to `Any` to silence:

```python
data_client = cast(Any, sess.client("data"))
```

## Concurrency tuning (measured, paid account)

| Phase | Per-node concurrency | Notes |
|-------|----------------------|-------|
| Search | 16/shard × 8 shards (~128 inflight) | 512 inflight gets 429-throttled. Aim 64-128. |
| Activate | 32-96 | Planet's queue caps total throughput ~10 cold scenes/min/account. Past ~64 is diminishing returns. |
| Extract | 32-64 | Network-bound ~0.5s read + 0.08s write per 1.5km patch. Disk is not the bottleneck. |

The per-account activation cap is **undocumented**. Ask Planet support directly if you need it lifted.

**Activate SR and UDM2 in parallel via `asyncio.gather`.** UDM2 is ~3x slower than SR for unknown reasons (worth reporting to Planet). Doing them serially halves throughput.

```python
sr_task   = asyncio.create_task(activate(item_id, "ortho_analytic_4b_sr"))
udm2_task = asyncio.create_task(activate(item_id, "ortho_udm2"))
sr_url, udm2_url = await asyncio.gather(sr_task, udm2_task)
```

## Planet reliability gotchas (plan around these)

- **~24% of `:activate` responses return `status=active` with a broken URL.** First range-read fails HTTP 400: `"Failure writing output to destination, passed 107 returned 0"`. Solution: a second `:activate` returns a different, working URL — asset is still active, the URL itself was corrupted. **Build a re-activation pass:** scan extract logs for `open_failed`, call `:activate` again, append a fresh row to `activations.jsonl`. Use last-write-wins on `item_id` when loading.
- **Some activations return success with `location=null`.** Same pattern; re-activate.
- **Pre-2018 archive and certain regions (India, Finland observed) have permanently dead assets.** Multiple reactivations do not help. Budget **3-5% unrecoverable**.
- **Cold-storage thaw p99 ≥ 45 minutes** for never-touched scenes. Mean ~3 min once warm. If Planet support enables it, pre-warming a list of scene IDs ahead of time collapses the long tail.

## Efficient patterns

### Resumable JSONL caches everywhere

Append-only, flushed every line. On rerun, build the set of done keys and skip them. Cheap and crash-safe.

```python
def append_row(path, row):
    with open(path, "a") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()

def load_done(path, key):
    done = set()
    if not os.path.exists(path):
        return done
    with open(path) as f:
        for line in f:
            try:
                done.add(json.loads(line)[key])
            except Exception:
                continue   # NFS append-races produce torn lines
    return done
```

**Always wrap `json.loads` in try/except.** NFS append-races produce torn lines that crash a naive loader.

### Don't wipe output files before re-extract

If you wipe `<patch>.tif` for resample then the resample fails, you have lost the original too. Either:

- Don't wipe — let `rasterio.open(path, "w")` overwrite naturally on success.
- Write to `<patch>.tif.tmp` and `os.replace` on success.

### UDM2 (or any small companion asset) gets its own 3-phase pass

Run a separate plan → activate → extract pass for UDM2 after the SR pipeline lands. Ships SR-first results while UDM2 is still thawing on Planet's side.

### Patch-level cloud cover ≠ scene-level cloud cover

A scene with 10% scene-level cloud can have a specific 1.5km patch at 100% cover. **Always probe UDM2 at the actual patch AOI post-hoc.** Re-sample cloudy patches against alternative scenes from the search results.

## Anti-patterns

- Do not use the Orders API for windowed access at scale.
- Do not trust the SDK to auto-retry — there are no built-in retries.
- Do not activate UDM2 inside per-patch loops — batch by unique `item_id` first.
- Do not set `CPL_VSIL_CURL_ALLOWED_EXTENSIONS` with Planet signed URLs.
- Do not pass GDAL config numeric values as strings.
- Do not run `wait_asset` polling without a max-attempts cap — stuck scenes will pin a worker forever.
- Do not wipe existing outputs before a re-extract attempt.
- Do not assume `status=active` means the URL works — verify with the first read, retry-by-reactivate on failure.

## Quick pre-flight checklist

1. AOIs deduped and grouped by `item_id` before any activation call.
2. JSONL caches for search/activations/extract wired up and resumable.
3. Retry wrapper installed around every Data API call (`429` + `5xx` strings + `httpx` transients).
4. GDAL config dict in place, numeric values as ints, `CPL_VSIL_CURL_ALLOWED_EXTENSIONS` unset.
5. SR and UDM2 activations launched in parallel via `asyncio.gather`.
6. Concurrency capped (search ≤128, activate ≤96, extract ≤64).
7. Re-activation pass planned for `open_failed` extract rows.
8. Budget 3-5% permanently unrecoverable assets.
9. Shard size 1-5k entries; extract sharded by `hash(item_id)`.
10. Post-hoc UDM2 cloud probe at patch AOI, not scene level.
