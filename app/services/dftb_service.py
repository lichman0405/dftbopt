# app/services/dftb_service.py
# This file contains the core business logic for the DFTB+ optimization task.
# Author: Shibo Li
# Date: 2025-06-21
# Version: 0.1.0


import os
import shutil
from fastapi import UploadFile
from typing import Tuple

from app.utils.file_convertor import cif_to_gen, gen_to_cif
from app.utils.logger import console
from app.core.dftb_runner import run_dftb
from app.core.output_parser import parse_detailed_out

async def perform_optimization(
    input_file: UploadFile, fmax: float, method: str, workspace_dir: str
) -> Tuple[dict, str]:
    """
    Orchestrates the optimization workflow within a given directory.
    It no longer creates or cleans up the workspace.

    Args:
        input_file: The uploaded file object.
        fmax: Force convergence threshold.
        method: GFN-xTB method.
        workspace_dir: The pre-existing directory to perform calculations in.

    Returns:
        A tuple containing: (parsed_results_dict, output_cif_path)
    """
    # Save uploaded file
    input_cif_path = os.path.join(workspace_dir, str(input_file.filename))
    with open(input_cif_path, "wb") as buffer:
        shutil.copyfileobj(input_file.file, buffer)
    console.info(f"Saved input file to {input_cif_path}")

    # Convert CIF to GEN
    cif_to_gen(input_cif_path)
    input_gen_name = os.path.basename(os.path.splitext(input_cif_path)[0] + ".gen")
    
    # Run DFTB+ calculation
    success = run_dftb(workspace_dir, input_gen_name, fmax, method)
    if not success:
        raise RuntimeError("DFTB+ calculation process failed.")

    # Process output files
    detailed_out_path = os.path.join(workspace_dir, "detailed.out")
    geo_end_gen_path = os.path.join(workspace_dir, "geo_end.gen")
    if not os.path.exists(detailed_out_path) or not os.path.exists(geo_end_gen_path):
        raise FileNotFoundError("Required output files (detailed.out, geo_end.gen) are missing.")
        
    # Parse results
    parsed_data = parse_detailed_out(detailed_out_path)
    
    # Convert final structure
    gen_to_cif(geo_end_gen_path)
    output_cif_path = os.path.join(workspace_dir, "geo_end.cif")
    
    # Return data and the path to the final CIF file
    return parsed_data, output_cif_path