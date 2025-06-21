# app/api/routes/optimization.py
# This file defines the API endpoints related to structure optimization.
# Author: Shibo Li
# Date: 2025-06-21
# Version: 0.1.0


import os
import shutil
import uuid
import base64
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import JSONResponse

from app.schemas.optimization import OptimizationResponseSchema
from app.services import dftb_service
from app.utils.logger import console

router = APIRouter()

WORKSPACE_BASE = os.path.join("app", "workspace")

@router.post(
    "/",
    responses={
        200: {
            "description": "Optimization was successful.",
            "model": OptimizationResponseSchema,
        },
        422: {
            "description": "Calculation failed due to input structure or resource issues.",
            "content": {
                "application/json": {
                    "example": {"detail": "DFTB+ calculation failed for the provided structure..."}
                }
            },
        },
        500: {
            "description": "An unexpected internal server error occurred.",
        }
    },
    summary="Run DFTB+ Geometry Optimization and Get All Results",
    description="Submits a CIF file for optimization. On success, returns a single JSON "
                "response containing analysis results and the Base64-encoded "
                "optimized structure file."
)
async def run_dftb_optimization_and_get_results(
    input_file: UploadFile = File(..., description="Input structure file in CIF format."),
    fmax: float = Form(0.1, description="Force convergence threshold in eV/Angstrom."),
    method: str = Form("GFN1-xTB", description="GFN-xTB method (GFN1-xTB or GFN2-xTB).")
):
    """
    Receives a CIF file and parameters, performs a DFTB+ geometry optimization,
    and returns a single, self-contained JSON response.
    """
    if method not in ["GFN1-xTB", "GFN2-xTB"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid method '{method}'. Please choose 'GFN1-xTB' or 'GFN2-xTB'."
        )

    if not input_file.filename or not input_file.filename.lower().endswith('.cif'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload a .cif file."
        )

    request_id = str(uuid.uuid4())
    workspace_dir = os.path.join(WORKSPACE_BASE, request_id)
    os.makedirs(workspace_dir)

    try:
        parsed_data, output_cif_path = await dftb_service.perform_optimization(
            input_file=input_file, fmax=fmax, method=method, workspace_dir=workspace_dir
        )
        with open(output_cif_path, 'rb') as f:
            cif_content_bytes = f.read()

        cif_b64_string = base64.b64encode(cif_content_bytes).decode('utf-8')

        # Construct the successful response object.
        response_data = {
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
        return JSONResponse(status_code=status.HTTP_200_OK, content=response_data)

    except RuntimeError as e:
        console.error(f"DFTB+ runtime error for request {request_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"DFTB+ calculation failed for the provided structure. This is likely due to "
                   f"insufficient resources (memory) for a large structure, or an unstable initial geometry. "
                   f"Internal error: {str(e)}"
        )
    except Exception as e:
        console.exception(f"An unexpected error occurred for request {request_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected server error occurred: {str(e)}"
        )
    finally:
        if os.path.exists(workspace_dir):
            shutil.rmtree(workspace_dir)
            console.info(f"Cleaned up workspace directory: {workspace_dir}")