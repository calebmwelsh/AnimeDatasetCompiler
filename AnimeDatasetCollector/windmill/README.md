# Windmill port of the AniList -> Kaggle collector

This folder holds the Windmill version of the job that used to run as the Docker
`anilist-data-collector` container triggered by the Ofelia `scheduler`. The
Docker setup in `../docker/` is intentionally left in place so you can fall
back.

- `anilist_to_kaggle.py` - a single, self-contained Windmill Python script that
  replaces `main.py` + `fetch_data.py` + `upload_data.py`.

## What changed vs. the Docker version

- One script instead of three. The fetch and upload share one in-memory
  DataFrame, so splitting them into a flow would force the whole ~21k-row
  dataset through Windmill's result store between steps - wasteful on this Pi.
- No `kaggle.json` file. Credentials come from two Windmill secret variables and
  are exported as `KAGGLE_USERNAME` / `KAGGLE_KEY`, which the kaggle library
  reads natively.
- All file I/O goes to a per-run temp dir (`tempfile.mkdtemp`) and is deleted at
  the end. Nothing assumes a persistent mount (the old container had none either
  - its `anime_data` dir was empty).
- `tqdm` progress bars are replaced with periodic `logging` (no TTY in Windmill).
- `fetch_data.py` and `kaggle_dataset_description.md` are embedded as base64 so
  the published dataset keeps the exact same file list. The metadata JSON is
  inlined as a Python dict.
- The year-based pagination that works around AniList's 5,000-record cap is
  unchanged. XLSX output is still best-effort (wrapped in try/except, same as the
  original), so a memory or Excel cell-limit error logs a warning and the run
  continues on CSV + pickle.

## Deployment status (done 2026-06-26)

This was deployed and tested in the live Windmill on the Pi (workspace `admins`)
via the `windmill-local` MCP. Already in place:

- **Script**: `f/anime/anilist_to_kaggle` (Python 3.11). Dependencies installed
  and locked by Windmill from the `#requirements:` block (pandas, requests,
  kaggle, openpyxl, **wmill**).
- **Secret variables**: `f/anime/kaggle_username` (`calebmwelsh`) and
  `f/anime/kaggle_key`.
- **Schedule**: `f/anime/anilist_to_kaggle`, cron `0 0 2 * * SUN`, timezone
  `America/Chicago`, args `{no_upload:false, test_mode:false}` plus the two var
  paths. It is **DISABLED** - see Cutover below.

Verified on the worker:
- Dry run (`no_upload=true, test_mode=true`) -> 100 records fetched, all 6 files
  staged, no upload. ~13s.
- Real upload test (`test_mode=true, dataset_id="calebmwelsh/anilist-test"`) ->
  published to the throwaway dataset. ~23s. (Delete `calebmwelsh/anilist-test`
  on Kaggle when you no longer need it.)

The live full run (`no_upload=false, test_mode=false` -> the real
`calebmwelsh/anilist-anime-dataset`) has NOT been run yet - that is the cutover.

Note on `wmill` in the requirements block: when a `#requirements:` block is
present, Windmill builds an isolated venv with exactly those packages and does
NOT auto-add the `wmill` client, so it must be listed explicitly. `openpyxl` is
listed for the same reason (pandas imports it lazily; import detection misses it).

### Rotate the Kaggle key

The key currently in `f/anime/kaggle_key` is the one from the old mounted
`kaggle.json` and was exposed in plaintext during setup. Rotate it on Kaggle
(Settings -> API -> Expire/Create New Token) and update the variable with
`updateVariable` (or the UI). The key is intentionally not written into this
git-tracked file.

## Cutover (you do this when ready)

1. Trigger one real full run to confirm the live dataset publishes and to see the
   Pi's memory behavior: run `f/anime/anilist_to_kaggle` manually with
   `no_upload=false, test_mode=false` (the default args) and watch
   `docker stats windmill-windmill_worker-1` / `free -h` on the Pi.
2. Stop the old Docker job so it does not also fire Sunday 2 AM: the collector +
   Ofelia are Portainer stack #29 (`/data/compose/29`). Delete that stack in
   Portainer, or `docker compose down` the `anilist-data-collector` and
   `scheduler` services. Until this is done, the Windmill schedule must stay
   disabled or the dataset would publish twice each Sunday.
3. Enable the Windmill schedule (`updateSchedule` with `enabled:true`, or the UI
   toggle). The job timeout in Windmill defaults are fine, but a full fetch is
   many minutes across the ~24 year ranges with a 0.5s delay per page.

## Heads-up: memory on this Pi

The Pi has ~1.8 GB RAM total and ~1.1 GB free, shared with the Windmill server,
worker, postgres, two GitHub runners, cloudflared, and Portainer. In a dry run,
100 anime produced a ~5 MB CSV (~50 KB/record) because of the large nested JSON
columns (characters, staff, relations, recommendations, reviews). At ~21,000
records that extrapolates to roughly a 1 GB CSV, plus the in-memory DataFrame and
the openpyxl XLSX write on top.

So the full run is the part most likely to fail under memory pressure - more than
it would have in the standalone Docker container, because the Windmill worker
carries its own footprint. Mitigations if the first full run OOMs:

- The XLSX step is already best-effort and will drop out first (it is also the
  heaviest); the run continues on CSV + pickle.
- Watch the first real run's worker memory (`docker stats windmill-windmill_worker-1`
  on the Pi, or `free -h`).
- If it still OOMs, options are: raise the worker's memory/swap, trim the GraphQL
  query (the per-anime characters/staff/reviews subfields dominate the size), or
  stream batches to disk and concatenate with lower peak memory. Flag me and we
  can do one of these.
