# app/services/dftb_service.py
# This file contains the core business logic for the DFTB+ optimization task.

import os
import shutil
import uuid
from fastapi import UploadFile

from app.utils.file_convertor import cif_to_gen, gen_to_cif
from app.utils.logger import console
from app.core.dftb_runner import run_dftb
from app.core.output_parser import parse_detailed_out
from app.schemas.optimization import OptimizationResponseSchema, DetailedResultsSchema

WORKSPACE_BASE = os.path.join("app", "workspace")

async def perform_optimization(
    input_file: UploadFile, fmax: float, method: str
) -> OptimizationResponseSchema:
    """
    Orchestrates the entire DFTB+ optimization workflow.
    """
    request_id = str(uuid.uuid4())
    workspace_dir = os.path.join(WORKSPACE_BASE, request_id)
    os.makedirs(workspace_dir)

    try:
        # Save uploaded file
        input_cif_path = os.path.join(workspace_dir, str(input_file.filename))
        with open(input_cif_path, "wb") as buffer:
            shutil.copyfileobj(input_file.file, buffer)
        console.info(f"[{request_id}] Saved input file to {input_cif_path}")

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
            
        # Parse detailed.out and convert to Pydantic model
        parsed_data = parse_detailed_out(detailed_out_path)
        detailed_results = DetailedResultsSchema(**parsed_data)
        
        # Convert optimized GEN back to CIF
        gen_to_cif(geo_end_gen_path)
        output_cif_path = os.path.join(workspace_dir, "geo_end.cif")
        
        with open(output_cif_path, "r") as f:
            output_cif_content = f.read()

        # Construct the final response object using the Pydantic schema
        return OptimizationResponseSchema(
            status="success",
            request_id=request_id,
            input_parameters={
                "original_filename": input_file.filename,
                "method": method,
                "fmax_eV_A": fmax
            },
            detailed_results=detailed_results,
            optimized_structure_cif=output_cif_content,
        )

    finally:
        # Clean up the temporary workspace
        if os.path.exists(workspace_dir):
            shutil.rmtree(workspace_dir)
            console.info(f"[{request_id}] Cleaned up workspace directory.")