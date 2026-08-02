# F35 — dome_mission: Mission-Sequencing Layer

> Relocated from dome_nav → dome_mission (2026-07-31, TF35 T08) as this package's
> founding record — the extraction (T01–T08) is complete, including the T07
> live sim bring-up (verified 2026-08-01: explore ran end-to-end via
> `mission_node`, `reached: 2, failed: 0`). Go-to-label remains
> live-unverified only because it's blocked upstream on F33/TF33
> (`dome_semantic` uncoded), not a gap in this feature.

**Priority**: High
**Done:** yes
**Tasks File Created:** yes (TF35)
**Tests Written:** yes
**Test Passing:** yes
**Description**: Extract high-level mission sequencing out of dome_nav into a
new neutral package `dome_mission`. dome_nav becomes navigation **primitives
only** (SLAM, plan, drive-to-pose, frontier-explore); dome_mission owns the
mission FSM and the `/intent` contract, orchestrating dome_nav + dome_semantic.
Introduced alongside F33 Phase A: the semantic-target consumer (label→pose
resolution) lands in dome_mission from the start, so dome_nav never gains a
dependency on `dome_semantic_msgs`.

Motivation: the three mission verbs are not peers. `explore` is a dome_nav
primitive, but `locate targets` (explore + semantic ingest, sequenced) and
`go to target` (label→pose from dome_semantic + drive-to-pose in dome_nav) are
cross-package orchestration that today is smeared into dome_nav
(`nav_manager` and `explorer_manager_node` both subscribe `/intent`). A mission
layer gives that logic one home and keeps every package below it a dumb,
reusable primitive.

## Settled decisions (2026-07-31, author)

- **Extract in Phase A**, not deferred to Phase C. The F33 typed-msg consumer
  (F33 T05, label→pose) is built in dome_mission from day one; dome_nav never
  consumes `SemanticTargetArray`. This reassigns F33 T05 — see F33 G9.
- **`dome_mission` owns `/intent`.** dome_control → `/intent` → dome_mission.
  dome_nav's `explorer_manager_node` and `nav_manager_node` **stop** subscribing
  `/intent` and instead expose primitives dome_mission calls. Exactly one
  `/intent` handler in the system (no two-handler race).
- **Neutral package.** dome_mission depends on dome_nav's primitive interface,
  `dome_semantic_msgs`, and TF. dome_nav depends on none of the above.

## Target layering

```
dome_control      dome_mission (NEW)        dome_nav        dome_semantic
  intents    →    behavior FSM        →    primitives   ←   object memory
 (voice/UI)       explore/locate/goto      explore/nav      label→pose source
```

## Scope

- New `dome_mission` package: mission FSM node subscribing `/intent`, driving
  the three behaviors. Pure/ROS split per dome_nav L0/L1 discipline — sequencing
  logic testable without a live graph.
- Three behaviors:
  - **explore** — start/stop dome_nav frontier exploration; done on no-frontiers.
  - **locate targets** — explore (or survey vantage points) while dome_semantic
    ingests; the stateful cross-package sequence (F33 Phase C's real home).
  - **go to target** — resolve label→pose from `SemanticTargetArray`
    (dome_semantic), send `NavigateToPose` to Nav2 via dome_nav.
- dome_nav primitive interface: how dome_mission commands explore start/stop and
  drive-to-pose (candidate: ROS actions `ExploreArea` + Nav2's existing
  `NavigateToPose`; decided in the task file). Removes `/intent` subscription
  and label-lookup from dome_nav.
- Move F33 T05 label→pose consumer here; `tools/nav_intent_check.py` retargeted
  to talk to dome_mission.

## Constraints

- Exactly one `/intent` handler (dome_mission). dome_nav nodes must not also
  subscribe `/intent` after this lands.
- dome_nav must not depend on `dome_semantic_msgs` or `dome_semantic`.
- No YAML patching; launch composition via `better_launch`.
- Resolves F33 open question G3 (where dwell/sequencing lives): in dome_mission,
  not the explorer node FSM, algorithm plugin, or Nav2 BT.

## Open questions

- dome_nav primitive interface shape: ROS actions vs services vs a thin
  command topic — settle in the F35 task file with the explore start/stop and
  drive-to-pose contract.
- Boundary vs the explorer node's existing watchdog/stuck FSM (analysis.md
  Part 1 node-watchdog tension): which stop/abort authority stays in dome_nav
  vs moves up to dome_mission.
- **Orchestrator: FSM vs behavior tree — Phase-B decision.** Phase A/C use a
  plain FSM (3 verbs, mostly sequential; BT is YAGNI). BT becomes a candidate at
  Phase B for reactive vision-aware behaviors (pause/dwell/confirm/resume,
  fallback/retry, viewpoint coverage). If adopted it is `py_trees_ros` (Python),
  a separate higher tree, **not** Nav2's internal C++ BT. The T01 ROS-action
  interface is chosen to keep this FSM→BT swap cheap (see TF35 T01 rationale).

## How to Demo

**Setup**

`dome_nav`'s `main` branch predates this feature — the `ExploreArea` action
server (T07) only exists on `origin/semantic-exploration`, not yet merged.
Check that branch out before building, or the explorer silently falls back to
its pre-T07 `/intent` handler with no action server:

```bash
cd <ws>/src/dome_nav && git checkout semantic-exploration  # or -b + origin/... if not local yet
```

Build and source the workspace:

```bash
colcon build --packages-select dome_nav_msgs dome_semantic_msgs dome_nav dome_mission
source install/setup.bash
```

Bring up the whole stack from the mission-layer top-level launch (slam + Nav2 +
explorer + mission_node) on a sim host with a world loaded:

```bash
bl dome_mission mission_explore.launch.py --map_name demo --world_name simple_room --sim_mode true
```

`--sim_mode` (not `--use_sim_time` — that name collides with a better_launch
framework-reserved global option and is silently dropped, see TF35 T07) picks
dome_nav's Gazebo sim stack over the real-robot one; `--world_name` is
required in sim mode (`simple_room` or `multi_room`, from `dome_nav/worlds/`).

Until F33 lands, the semantic map has no live publisher, so the go-to-label
step (D) uses `tools/nav_intent_check.py` to inject one typed target.

**A. Confirm the layering is wired (no robot motion needed)**

```bash
ros2 action list | grep explore_area          # dome_nav exposes the primitive
ros2 node info /mission | grep -A2 Subscribers # mission_node subscribes /intent
ros2 node info /explore_manager_node | grep -c /intent   # expect 0
```

Pass: `/explore_area` is advertised as `dome_nav_msgs/action/ExploreArea`, the
sole `/intent` subscriber is `/mission`, and the explorer has none — the
single-`/intent`-handler invariant holds and dome_nav carries no
`dome_semantic_msgs` dependency (`grep -r dome_semantic dome_nav/` is empty).

**B. Explore via the mission verb**

In one terminal watch the feedback and status:

```bash
ros2 topic echo /explore/status
```

Start exploration by publishing the intent dome_mission owns:

```bash
ros2 topic pub --once /intent std_msgs/msg/String \
  'data: "{\"name\": \"exploration_start\", \"source\": \"cli\", \"slots\": {}}"'
```

Pass: `mission_node` logs `intent EXPLORE_START -> state EXPLORING` and sends an
`ExploreArea` goal; the explorer starts picking frontier goals; the map grows;
`ExploreArea` feedback reports rising `explored_area_m2` and the live
`current_goal`.

**C. Preempt mid-session**

```bash
ros2 topic pub --once /intent std_msgs/msg/String \
  'data: "{\"name\": \"exploration_stop\", \"source\": \"cli\", \"slots\": {}}"'
```

Pass: the `ExploreArea` goal is canceled (result outcome `STOPPED=1`), the robot
stops, and the FSM returns to `IDLE`. (Letting exploration run to no-frontiers
instead yields `EXPLORED_DONE=0`.)

**D. Go to a labelled target**

Inject one confirmed target and command a drive to it:

```bash
python3 tools/nav_intent_check.py     # publishes a typed SemanticTargetArray + navigation_go
```

Or by hand: publish a `dome_semantic_msgs/SemanticTargetArray` on
`/semantic/targets` (a `can` at a known map pose, `schema_version: 1`), then:

```bash
ros2 topic pub --once /intent std_msgs/msg/String \
  'data: "{\"name\": \"navigation_go\", \"source\": \"cli\", \"slots\": {\"label\": \"can\"}}"'
```

Pass: `mission_node` resolves `can` → the recorded pose (nearest to the robot,
yaw included), sends a Nav2 `NavigateToPose` goal **directly** (no dome_nav hop),
and the robot drives there and arrives. An unknown label logs a clear warning and
the FSM settles back at `IDLE` without motion. A stray target with the wrong
`schema_version` is dropped with a warning.

**Expected output**

All three mission verbs (explore / stop / go-to-label) are orchestrated from one
place — dome_mission. dome_nav is a dumb navigation primitive with no mission or
semantic knowledge: it only serves the `ExploreArea` action and Nav2. The
`/intent` contract has exactly one handler, and go-to-label rides the typed
`SemanticTargetArray` msg, not the retired schemaless JSON.
