# app/schemas/optimization.py
# This file defines the data structures (schemas) for API requests and responses.
# Author: Shibo Li
# Date: 2025-06-21
# Version: 0.1.0

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class DipoleMomentSchema(BaseModel):
    x: float
    y: float
    z: float

class ElectronicPropertiesSchema(BaseModel):
    fermi_level_eV: Optional[float] = None
    total_charge: Optional[float] = None
    dipole_moment_debye: Optional[DipoleMomentSchema] = None

class ConvergenceInfoSchema(BaseModel):
    scc_converged: bool = False

class SummarySchema(BaseModel):
    calculation_status: str
    convergence_status: str
    warnings: List[str] = []
    error: Optional[str] = None

class DetailedResultsSchema(BaseModel):
    summary: SummarySchema
    convergence_info: ConvergenceInfoSchema
    electronic_properties: ElectronicPropertiesSchema
    energies_eV: Dict[str, float]
    energies_hartree: Dict[str, float]

class OptimizationResponseSchema(BaseModel):
    status: str
    request_id: str
    input_parameters: Dict[str, Any]
    detailed_results: DetailedResultsSchema
    # This field will hold the Base64 encoded string of the final CIF file.
    optimized_structure_cif_b64: str = Field(
        ..., 
        description="The optimized structure in CIF format, encoded as a Base64 string."
    )