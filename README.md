# Spawning Geometries Extraction

## Overview
This directory contains extracted spawning geometries from all top-level TRAJ directories.

## Script
**File:** `extract_spawning_geometries.py`

A Python script that automatically detects all top-level TRAJ directories (TRAJ1, TRAJ2, ...) 
and extracts the 5th geometry from each subtrajectory, categorizing them by the electronic 
state they spawned into.

## Methodology

### Geometry Extraction
- **Spawning Geometry:** The 5th geometry from each `TRAJn/geometries.xyz` file
- **Source:** Automatically scans all top-level TRAJ directories in the base folder
- **Current Processing:** TRAJ1 (72 subtrajectories) + TRAJ2 (72 subtrajectories) = 144 total
- Note: Subdirectories with the same name as their parent are excluded (e.g., TRAJ1/TRAJ1)

### State Determination
For each spawning geometry:
1. Extract the timestep from the geometry's comment line
2. Find the corresponding line in `energies.dat` at that timestep
3. Compare the last column `Epot(nstatdyn)` with columns `Epot1` through `Epot6`
4. The matching Epoti column determines the spawning state (i=1,2,3,4,5,6)

### Output Format
Files are named `{state}.spawn.xyz` where state ∈ {1,2,3,4,5,6}

Each geometry includes:
- Number of atoms (38)
- Comment line: `SPAWNGEOM = TRAJx/TRAJn | {time} {step}`
- 38 lines of atomic coordinates (element, x, y, z)

## Results

| File | State | Number of Geometries |
|------|-------|---------------------|
| 2.spawn.xyz | 2 | 28 |
| 3.spawn.xyz | 3 | 26 |
| 4.spawn.xyz | 4 | 41 |
| 5.spawn.xyz | 5 | 30 |
| 6.spawn.xyz | 6 | 19 |
| **Total** | | **144** |

**Note:** No trajectories spawned into state 1 (no 1.spawn.xyz file was created).

### Distribution by Top-Level TRAJ:
- **TRAJ1:** 72 spawning geometries (from TRAJ2-TRAJ73 subdirectories)
- **TRAJ2:** 72 spawning geometries (from TRAJ1, TRAJ3-TRAJ73 subdirectories)

## Usage

To re-run the extraction:
```bash
python3 extract_spawning_geometries.py
```

The script will:
1. Automatically detect all top-level TRAJ directories (TRAJ1, TRAJ2, TRAJ3, ...)
2. Scan all TRAJn subdirectories within each top-level TRAJ
3. Extract the 5th geometry from each subtrajectory
4. Determine the spawning state for each geometry
5. Aggregate all geometries and create/overwrite the {state}.spawn.xyz files

**Scalability:** The script will automatically process any number of top-level TRAJ directories 
present in the base folder, making it suitable for expanding datasets.

## Files Generated
- `2.spawn.xyz` - Geometries that spawned into state 2
- `3.spawn.xyz` - Geometries that spawned into state 3  
- `4.spawn.xyz` - Geometries that spawned into state 4
- `5.spawn.xyz` - Geometries that spawned into state 5
- `6.spawn.xyz` - Geometries that spawned into state 6

All files follow the standard XYZ format compatible with visualization tools.
