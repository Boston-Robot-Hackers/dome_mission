# The mission for Dome

The mission has three phases. Each phase is a **behavior that dome_mission
runs**: plain sequential code that calls motion actions and reads the semantic
map (F05). dome_mission decides when a phase starts and when it is done. The
other packages do the moving, mapping and seeing.

## Mapping phase

The robot drives around the arena autonomously and builds a map with
slam_toolbox.

- **Behavior**: dome_mission sends dome_nav an `ExploreArea` goal and waits for
  the terminal outcome (no frontiers left, or stopped).
- **Who does what**: dome_nav picks frontiers and drives. With no map yet it
  relies on the short-range obstacle map to stay out of trouble, and keeps
  pushing into uncharted areas. Per-goal aborts are dome_nav's.
- **Done when**: `ExploreArea` returns. Exploring within a bounded extent
  (e.g. one room) is F06.

## Discovery Phase

The robot finds and records objects of interest.

- **Decided**: dome_semantic builds the object map from vision and publishes it
  on `/semantic/targets`. dome_mission keeps a local copy and builds no world
  model of its own.
- **Decided**: small looks around use Nav2's `Spin` action, not a new
  primitive.
- **Not decided**: whether discovery runs during mapping or as a separate pass,
  and what makes it "done".

## Command Phase

The robot carries out requests against the built maps.

- **Decided**: requests arrive on `/intent`, already structured, from the CLI,
  voice or pad. dome_mission is the only consumer once F08 lands.
- **Decided**: go to target resolves a label against the local semantic map and
  drives there with Nav2 `NavigateToPose`.
- **Decided**: `stop` cancels whatever behavior is running.
- **Planned**: check-targets patrol (F04).
- **Not decided**: whether the map keeps updating during this phase
  (localization vs lifelong SLAM). That is dome_nav's mode (I02).
