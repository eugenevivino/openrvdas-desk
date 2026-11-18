# PR draft: DeepSignal vector wind averaging

- From: `eugenevivino/openrvdas` branch `claude/project-thread-un3kq6`
- To: `OceanDataTools/openrvdas_contrib` `master`
- Preview: https://github.com/OceanDataTools/openrvdas_contrib/compare/master...eugenevivino:openrvdas:claude/project-thread-un3kq6
- Status: NOT SENT. Eugene sends it.

## Title

Add DeepSignal: vector wind averaging transform

## Body

<!-- claude-projects-attribution: {"github_login":"eugenevivino"} -->
_Requested by **Eugene** · [project thread](https://claude.ai/code/project/chan_01MydaUAct1B7TBxJNsNW39Q?thread=cmsg_01MydaUAct1B7TBxJNsNW39Q2YAM89XB3tUbsvtKGpWkHG)_

This adds a new contrib project, `contrib/deepsignal/`, and its first module.

**What it does.** `VectorWindAverageTransform` averages wind as vectors over a
time window. A plain average of wind direction is wrong near north: 359 and 1
degrees average to 180. Here they average to 0. Each sample is weighted by its
speed, which is the usual vector-mean wind. Besides mean speed and direction it
can report the plain mean speed, the gust (highest speed in the window),
steadiness, direction spread, and how many samples went into each average.

**How it fits with core.** It is meant to run after core `TrueWindsTransform`,
so it averages true wind. It does not replace `InterpolationTransform`'s
`polar_average`, which averages a single angle with equal weights and is still
the right tool for heading or course.

**Missing data.** It never fills gaps. A sample is used only when speed and
direction arrive in the same record as real numbers. A window with too few good
samples (`min_count`) produces no value, and a calm window reports speed but no
direction, because the direction is undefined.

**Timing.** Averages are stamped on whole multiples of the interval (for a
60 second interval, on each minute) using the data's own timestamps, and cover
the window up to that time.

**Files**
- `contrib/deepsignal/logger/transforms/vector_wind_average_transform.py`
- `contrib/deepsignal/test/logger/transforms/test_vector_wind_average_transform.py` (23 tests)
- `contrib/deepsignal/configs/vector_wind_average_logger.yaml` (runnable sample on the NBP1406 test data)
- `contrib/deepsignal/README.md`

**Testing**
- `pytest contrib/deepsignal/test/`: 23 passed, on this repo's `master` and
  on a current OpenRVDAS core (v2.7.2).
- `flake8 contrib/deepsignal/`: clean.
- Ran the sample config with `listen.py` on core v2.7.2; it printed one
  averaged record per minute.

**Dependencies.** None beyond what core OpenRVDAS already needs.

Questions for the maintainer: is `contrib/deepsignal/` the layout you want,
and is `master` the right target?

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01S8FDBe92VvncFh58DEY89Q
