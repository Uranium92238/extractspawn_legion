#!/usr/bin/env python3
"""
Extract spawning geometries from trajectory data.
The 5th geometry from each subtrajectory is extracted and categorized
by the state it spawned into.
"""

import os
import re
import argparse
from pathlib import Path
from collections import defaultdict


def read_fifth_geometry(geom_file):
    """Read the 5th geometry from a geometries.xyz file."""
    with open(geom_file, 'r') as f:
        lines = f.readlines()
    
    if len(lines) < 1:
        return None, None, None
    
    # Read number of atoms from the first line
    try:
        natoms = int(lines[0].strip())
    except (ValueError, IndexError):
        return None, None, None
    
    # Each geometry block has: 1 line (natoms) + 1 line (comment) + natoms lines (coordinates)
    block_size = natoms + 2
    
    # Geometry 5 is at index 4 (0-indexed), so it starts at line 4 * block_size
    geom_5_start = 4 * block_size
    geom_5_end = geom_5_start + block_size
    
    # Check if file is long enough
    if len(lines) < geom_5_end:
        return None, None, None
    
    # Extract lines for 5th geometry
    geom_lines = lines[geom_5_start:geom_5_end]
    
    # Get number of atoms and timestep info
    natoms_line = geom_lines[0].strip()
    timestep_line = geom_lines[1].strip()
    
    # Extract the step number from timestep line
    # Format: "      11.000                110"
    parts = timestep_line.split()
    if len(parts) >= 2:
        step = int(parts[1])
    else:
        step = None
    
    return geom_lines, timestep_line, step


def get_spawn_state(energies_file, timestep=25):
    """
    Determine which state the trajectory spawned into.
    Looks at the energies.dat file at the given timestep (5th geometry is timestep 25).
    Matches Epot(nstatdyn) with one of the Epoti columns.
    """
    with open(energies_file, 'r') as f:
        lines = f.readlines()
    
    # Find the line corresponding to timestep 25 (5th geometry at 2.5 fs)
    target_line = None
    for line in lines:
        if line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        
        time = float(parts[0])
        step = int(parts[1])
        
        # The 5th geometry corresponds to step 25 (timestep 2.5 fs)
        if step == timestep:
            target_line = line
            break
    
    if not target_line:
        return None
    
    # Parse the energy line
    parts = target_line.split()
    # Columns: Time, Step, State, Etot, Ekin, Epot1, Epot2, ..., Epot6, Epot(nstatdyn)
    # Indices: 0     1     2      3     4     5      6           10     11
    
    if len(parts) < 12:
        return None
    
    epot_nstatdyn = float(parts[-1])  # Last column
    
    # Check which Epoti matches (columns 5-10 are Epot1-Epot6)
    tolerance = 1e-6
    for i in range(5, 11):  # Epot1 to Epot6
        epot_i = float(parts[i])
        if abs(epot_i - epot_nstatdyn) < tolerance:
            state = i - 4  # Epot1 -> state 1, Epot2 -> state 2, etc.
            return state
    
    return None


def main(input_dir=None, output_dir=None):
    # Base directory containing all TRAJ folders
    if input_dir is None:
        base_dir = Path.cwd()
    else:
        base_dir = Path(input_dir).resolve()
    
    # Output directory (defaults to same as input)
    if output_dir is None:
        out_dir = base_dir
    else:
        out_dir = Path(output_dir).resolve()
    
    print(f"Input directory: {base_dir}")
    print(f"Output directory: {out_dir}")
    
    # Create output directory if it doesn't exist
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Find all top-level TRAJ directories (TRAJ1, TRAJ2, ...)
    top_traj_dirs = sorted([d for d in base_dir.iterdir() 
                           if d.is_dir() and d.name.startswith('TRAJ')])
    
    print(f"\nFound {len(top_traj_dirs)} top-level TRAJ directories: {[d.name for d in top_traj_dirs]}")
    
    # Dictionary to store geometries by state
    geometries_by_state = defaultdict(list)
    
    # Process each top-level TRAJ directory
    for top_traj_dir in top_traj_dirs:
        top_traj_name = top_traj_dir.name
        
        # Find all TRAJn subdirectories (excluding TRAJ1 which is the original trajectory)
        traj_dirs = sorted([d for d in top_traj_dir.iterdir() 
                           if d.is_dir() and d.name.startswith('TRAJ') and d.name != 'TRAJ1'])
        
        print(f"\n{top_traj_name}: Found {len(traj_dirs)} subtrajectories")
        
        # Process each subtrajectory
        for traj_dir in traj_dirs:
            traj_name = traj_dir.name
            geom_file = traj_dir / "geometries.xyz"
            energies_file = traj_dir / "energies.dat"
            
            if not geom_file.exists() or not energies_file.exists():
                print(f"Warning: Missing files in {top_traj_name}/{traj_name}, skipping")
                continue
            
            # Read 5th geometry
            geom_lines, timestep_info, step = read_fifth_geometry(geom_file)
            if geom_lines is None or step is None:
                print(f"Warning: Could not read 5th geometry from {top_traj_name}/{traj_name}, skipping")
                continue
            
            # Determine spawn state
            state = get_spawn_state(energies_file, timestep=step)
            if state is None:
                print(f"Warning: Could not determine spawn state for {top_traj_name}/{traj_name}, skipping")
                continue
            
            # Modify comment line to include trajectory info
            natoms = geom_lines[0]
            comment_line = f"SPAWNGEOM = {top_traj_name}/{traj_name} | {timestep_info.strip()}\n"
            atom_lines = geom_lines[2:]
            
            # Store the geometry
            geometries_by_state[state].append((natoms, comment_line, atom_lines))
            
            print(f"{top_traj_name}/{traj_name}: spawned into state {state}")
    
    # Write output files
    for state, geoms in sorted(geometries_by_state.items()):
        output_file = out_dir / f"{state}.spawn.xyz"
        
        with open(output_file, 'w') as f:
            for natoms, comment, atoms in geoms:
                f.write(natoms)
                f.write(comment)
                for atom_line in atoms:
                    f.write(atom_line)
        
        print(f"\nWrote {len(geoms)} geometries to {output_file.name}")
    
    # Summary
    print("\n" + "="*60)
    print("Summary:")
    print("="*60)
    for state in sorted(geometries_by_state.keys()):
        print(f"State {state}: {len(geometries_by_state[state])} spawning geometries")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Extract spawning geometries from trajectory data and categorize by spawned state.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run in current directory (default)
  python3 extract_spawning_geometries.py
  
  # Specify input directory
  python3 extract_spawning_geometries.py -i /path/to/trajdata
  
  # Specify both input and output directories
  python3 extract_spawning_geometries.py -i /path/to/trajdata -o /path/to/output
        """
    )
    
    parser.add_argument(
        '-i', '--input',
        type=str,
        default=None,
        help='Input directory containing TRAJ folders (default: current directory)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output directory for spawn.xyz files (default: same as input directory)'
    )
    
    args = parser.parse_args()
    main(input_dir=args.input, output_dir=args.output)
