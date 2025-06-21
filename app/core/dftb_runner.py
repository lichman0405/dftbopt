# app/core/dftb_runner.py
# The module for running DFTB+ calculations with dynamic input generation.
# Author: Shibo Li
# Date: 2025-06-21
# Version: 0.1.0


import os
import subprocess
from app.utils.logger import console

def generate_hsd_content(method: str, fmax: float, input_gen_file: str) -> str:
    """Dynamically generate the content of the dftb_in.hsd file."""
    
    # Check if the method is valid
    if method not in ["GFN1-xTB", "GFN2-xTB"]:
        raise ValueError("Method must be 'GFN1-xTB' or 'GFN2-xTB'")

    # Use f-string to template the HSD input
    hsd_template = f"""
Geometry = GenFormat {{
  <<< "{input_gen_file}"
}}

Hamiltonian = xTB {{
  Method = "{method}"
  KPointsAndWeights = {{
    0.0 0.0 0.0 1.0
  }}
}}

Driver = GeometryOptimisation {{
  Optimiser = LBFGS {{}}
  LatticeOpt = Yes
  Convergence = {{
    GradElem [eV/Angstrom] = {fmax}
  }}
  MaxSteps = 200
  AppendGeometries = Yes
}}

Options {{
  WriteDetailedOut = Yes
}}

ParserOptions {{
  ParserVersion = 14
}}
"""
    return hsd_template

def run_dftb(workspace_dir: str, input_gen_file: str, fmax: float, method: str) -> bool:
    """
    Prepare and run DFTB+ calculations in the given working directory.
    
    Args:
        workspace_dir (str): The working directory for the calculation.
        input_gen_file (str): The name of the input .gen file (without path).
        fmax (float): Force convergence threshold.
        method (str): The calculation method to use (GFN1-xTB or GFN2-xTB).
        
    Returns:
        bool: Returns True if the calculation completes successfully, otherwise False.
    """
    console.info(f"Preparing DFTB+ calculation in {workspace_dir}...")
    hsd_content = generate_hsd_content(method, fmax, input_gen_file)
    hsd_path = os.path.join(workspace_dir, "dftb_in.hsd")

    try:
        with open(hsd_path, 'w') as f:
            f.write(hsd_content)
        console.success(f"Generated dftb_in.hsd for {method} with fmax={fmax} eV/Angstrom.")

        # Execute the DFTB+ command
        console.info("Starting DFTB+ process...")
        # Use subprocess.run, setting the working directory to workspace_dir
        # This ensures that DFTB+ looks for input files and generates output files in the correct directory
        result = subprocess.run(
            ['dftb+'],
            cwd=workspace_dir,
            capture_output=True,
            text=True,
            check=False  # Set to False, manually check the return code
        )

        # Check if the process executed successfully
        if result.returncode != 0:
            console.error("DFTB+ process failed!")
            console.error(f"Return Code: {result.returncode}")
            console.display_text_in_panel(result.stderr, "DFTB+ Stderr")
            return False

        console.success("DFTB+ process completed successfully.")
        console.info(f"DFTB+ stdout:\n{result.stdout[-500:]}") # Print the last 500 lines of output
        return True

    except Exception as e:
        console.exception(f"An error occurred while running DFTB+: {e}")
        return False
