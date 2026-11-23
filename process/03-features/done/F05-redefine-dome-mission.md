# F05 — Redefine dome_mission as the Single Brain

**Priority**: Medium

**Date Created:** 2026-11-22

**Done:** yes

**Tasks File Created:** yes

**Tests Written:** n/a (docs only)

**Test Passing:** n/a (docs only; full suite 49 passed 2026-11-23)

**Description**: Write down what dome_mission is and how it relates to
dome_control and dome_semantic. **Docs only, no code.** F04, F06 and F07 are
written against this definition.

This replaces the 2026-11-22 draft ("multi-step behavior layer, asks a semantic
query interface"). A 2026-11-23 review found that the draft added interfaces
nothing needed yet. It also left two nodes acting as the brain.

## The problem it fixes

Two nodes subscribe to `/intent` and split the intent names between them
(dome_control F19):

- dome_control's `behavior_manager_node` handles `stop`, the turns,
  `get_status`, `describe_scene` and `count_objects`;
- dome_mission's `mission_node` handles explore and go-to.

Each has its own intent parser. dome_control's `stop` is a motor halt that
doesn't know mission_node exists, and it can't interrupt motion running inside
`behavior_manager`. Both packages' docs say they are the brain.

## The definition

> **dome_mission is the brain.** It is the only node that consumes `/intent`,
> and it alone owns what the robot is doing now. It turns each intent into
> either a query answer or a behavior. It runs a behavior by calling motion
> actions in sequence, and `stop` cancels whatever is running.

## Package roles

### dome_control: operator surface

- **Owns**: the CLI/REPL, turning operator input into `/intent`, showing
  `/mission/state` and other status, process and launch management.
- **Does not own**: any `/intent` subscriber, robot activity state, behaviors.
  It publishes `/cmd_vel` only in an explicit manual/teleop mode.
- **Test**: if the robot would still behave correctly with dome_control deleted
  and intents arriving some other way, the code belongs here.

### dome_mission: the brain

- **Owns**: parsing intents, arbitration (a new intent preempts the old one;
  `stop` cancels everything), `/mission/state`, answering queries (call the
  service, publish an `/announcement`), and running behaviors (explore, go to
  target, turn, patrol, the mission phases).
- **Does not own**: talking to humans, publishing `/cmd_vel`, building the world
  model, English parsing.
- **Test**: if it decides what happens next or when something is finished, it
  belongs here.

### dome_semantic: world model

- **Owns**: building the object map (and rooms, once a behavior needs them),
  persisting it, publishing it on `/semantic/targets`, and the
  `/describe_scene` service.
- **Does not own**: motion, sequencing, deciding what to look at.
- **Test**: if it is a fact about the world, it belongs here.

### Motion primitives: Nav2 and dome_nav

- Each kind of motion the robot does on its own is a cancellable action:
  dome_nav's `ExploreArea`, Nav2's `NavigateToPose`, and Nav2's behavior-server
  `Spin` and `DriveOnHeading`.
- dome_mission calls these actions and doesn't implement any of them.

## Key decisions

- **One brain.** `behavior_manager_node` and its behavior handlers move into
  dome_mission, and dome_control stops subscribing to `/intent`. That change is
  its own feature (see **Follow-on work**).
- **Keep subscribing to the semantic map.** dome_mission keeps
  `label_resolver` and resolves labels against its copy of
  `/semantic/targets`. The array is small, and a local lookup is less code than
  a service and needs no async round trip. **Add a query service only when a
  question can't be answered from the published array.**
- **Use Nav2's behavior server for turns and small spins.** All dome_nav Nav2
  params files already enable `spin` and `drive_on_heading`. That removes the
  need for a new small-spin primitive. It probably also covers `spin_survey`,
  which would let dome_control's spin-survey code be deleted rather than moved.
  *Unverified*: whether the survey's pause-and-capture can be expressed as a
  series of `Spin` goals.
- **Behaviors are plain sequential code.** Each step waits on an action, so a
  patrol is a loop. No behavior-tree framework, and no FSM state per behavior.
  `py_trees_ros` stays a candidate only if reactive interrupts multiply.
  *Hazard*: in rclpy this needs a worker thread per behavior or async callbacks
  on a multi-threaded executor.
- **No English parsing.** Intents arrive already structured.
- **Map maintenance is dome_nav's.** Localization vs lifelong SLAM is a dome_nav
  mode. dome_mission at most requests one.

## What it supersedes

- **F03**: its "dome_mission holds all go-to-label / semantic knowledge" still
  stands, now as a subscription. Its "dome_mission is the sole `/intent`
  handler" becomes true only once the merge lands. Its FSM-for-now choice is
  replaced by plain sequential behaviors.
- **dome_control F19**: the split `/intent` ownership table goes away.
- **dome_control `control-architecture.md`**: its `behavior_manager_node`
  "brain" is now dome_mission. That doc is dome_control's to update.

## Follow-on work

These are not part of F05; each needs its own feature.

- **Merge the brain** into dome_mission (new feature here): bring in
  `behavior_manager_node`, `MotionBehavior` and `PerceptionBehavior`; map turns
  to Nav2 `Spin`/`DriveOnHeading`; keep a single intent parser; make `stop`
  cancel the active goal. dome_control then drops its subscriber (a dome_control
  feature).
- **F07** is largely moot, because `label_resolver` stays. Re-scope or defer it.
- **F04** uses Nav2 `Spin` and no longer waits on a new primitive.
- **F06** still needs extent fields on `ExploreArea.Goal` from dome_nav.

## Out of scope

Any code change.

## How to Demo

**Setup**: none.

**Steps**:
1. Read `process/02-doc/spec.md`, `CLAUDE.md`, `process/02-doc/notes.md` and
   `process/02-doc/mission.md`.
2. Read the headers of F03, F04 and F07.

**Expected output**: all four docs state the definition and package roles
above, consistently. F03 is marked as partly superseded. F04 and F07 are
re-scoped against F05.

## Process Gate

After creating this feature file and the corresponding task file, **stop and present the plan to the user**. Do not write any code or content until the user gives explicit approval to proceed.
