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
- **Molecule-agnostic:** The script dynamically reads the number of atoms from each geometry file, so it works with molecules of any size
- Note: Subdirectories named TRAJ1 are excluded (TRAJ1 is the original trajectory, not a spawned one)

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
| 4.spawn.xyz | 4 | 40 |
| 5.spawn.xyz | 5 | 30 |
| 6.spawn.xyz | 6 | 20 |
| **Total** | | **144** |

**Note:** No trajectories spawned into state 1 (no 1.spawn.xyz file was created).

### Distribution by Top-Level TRAJ:
- **TRAJ1:** 72 spawning geometries (from TRAJ2-TRAJ73 subdirectories; TRAJ1 excluded as original trajectory)
- **TRAJ2:** 72 spawning geometries (from TRAJ2-TRAJ73 subdirectories; TRAJ1 excluded as original trajectory)

## Usage

### Basic Usage
Run in the current directory (will look for TRAJ folders and output files here):
```bash
python3 extract_spawning_geometries.py
```

### Advanced Usage
Specify custom input and/or output directories:
```bash
# Specify input directory
python3 extract_spawning_geometries.py -i /path/to/trajdata

# Specify both input and output directories
python3 extract_spawning_geometries.py -i /path/to/trajdata -o /path/to/output

# View help
python3 extract_spawning_geometries.py --help
```

### Command-Line Options
- `-i, --input`: Input directory containing TRAJ folders (default: current directory)
- `-o, --output`: Output directory for spawn.xyz files (default: same as input directory)

The script will:
1. Automatically detect all top-level TRAJ directories (TRAJ1, TRAJ2, TRAJ3, ...)
2. Scan all TRAJn subdirectories within each top-level TRAJ
3. Extract the 5th geometry from each subtrajectory
4. Determine the spawning state for each geometry
5. Aggregate all geometries and create/overwrite the {state}.spawn.xyz files
6. Create the output directory if it doesn't exist

**Scalability:** The script will automatically process any number of top-level TRAJ directories 
present in the base folder, making it suitable for expanding datasets.

## Files Generated
- `2.spawn.xyz` - Geometries that spawned into state 2
- `3.spawn.xyz` - Geometries that spawned into state 3  
- `4.spawn.xyz` - Geometries that spawned into state 4
- `5.spawn.xyz` - Geometries that spawned into state 5
- `6.spawn.xyz` - Geometries that spawned into state 6

All files follow the standard XYZ format compatible with visualization tools.
