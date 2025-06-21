# app/api/routes/optimization.py
# This file defines the API endpoints related to structure optimization.
# Author: Shibo Li
# Date: 2025-06-21
# Version: 0.1.0

import base64
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status

from app.schemas.optimization import OptimizationResponseSchema
from app.services import dftb_service

router = APIRouter()

@router.post(
    "/",
    response_model=OptimizationResponseSchema,
    summary="Run DFTB+ Geometry Optimization and Get All Results"
)
async def run_dftb_optimization_and_get_results(
    input_file: UploadFile = File(..., description="Input structure file in CIF format."),
    fmax: float = Form(0.1, description="Force convergence threshold in eV/Angstrom."),
    method: str = Form("GFN1-xTB", description="GFN-xTB method (GFN1-xTB or GFN2-xTB).")
):
    """
    Receives a CIF file, performs optimization, and returns a single JSON
    response containing both the analysis results and the Base64-encoded 
    optimized structure file.
    """
    if method not in ["GFN1-xTB", "GFN2-xTB"]:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid method.")
    
    if not input_file.filename or not input_file.filename.lower().endswith('.cif'):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid file type, must be .cif.")
    
    try:
        # The service layer now returns the parsed data and the path to the output file
        parsed_data, output_cif_path, request_id = await dftb_service.perform_optimization(
            input_file=input_file, fmax=fmax, method=method
        )
        if isinstance(output_cif_path, tuple):
            output_cif_path = output_cif_path[0] 
        
        # Read the content of the final CIF file
        with open(output_cif_path, 'rb') as f:
            cif_content_bytes = f.read()
            
        # Encode the file content into a Base64 string
        cif_b64_string = base64.b64encode(cif_content_bytes).decode('utf-8')
        
        # Construct the final response object
        response = {
            "status": "success",
            "request_id": request_id,
            "input_parameters": {
                "original_filename": input_file.filename,
                "method": method,
                "fmax_eV_A": fmax
            },
            "detailed_results": parsed_data,
            "optimized_structure_cif_b64": cif_b64_string,
        }
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )