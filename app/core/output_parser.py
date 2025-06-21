# app/core/output_parser.py
# The module for parsing DFTB+ detailed.out files.
# Author: Shibo Li
# Date: 2025-06-21
# Version: 0.1.0

import re
from typing import Dict, Any

def parse_detailed_out(file_path: str) -> Dict[str, Any]:
    """
    Parses a DFTB+ detailed.out file for key summary information.
    This version is optimized to locate the final results block first
    and then extract the required data, improving efficiency.

    Args:
        file_path (str): The path to the detailed.out file.

    Returns:
        Dict[str, Any]: A structured dictionary with the parsed data.
    """
    results: Dict[str, Any] = {
        'summary': {},
        'convergence_info': {},
        'electronic_properties': {},
        'energies_eV': {},
        'energies_hartree': {}
    }

    try:
        with open(file_path, 'r') as f:
            content = f.read()

        results['summary']['warnings'] = re.findall(r"Warning: (.*)", content)
        results['summary']['convergence_status'] = "Geometry converged" if "Geometry converged" in content else "Not converged"
        results['summary']['calculation_status'] = 'Success'


        final_block_marker = "Total Mermin free energy"
        blocks = content.split(final_block_marker)
        
        if len(blocks) > 1:
            final_block = blocks[-1]
        else:
            final_block = content


        scc_converged = re.search(r"SCC converged", final_block)
        results['convergence_info']['scc_converged'] = bool(scc_converged)

        fermi_match = re.search(r"Fermi level:\s*([-\d\.E\+]+)\s*H\s*([-\d\.E\+]+)\s*eV", final_block)
        if fermi_match:
            results['electronic_properties']['fermi_level_eV'] = float(fermi_match.group(2))

        charge_match = re.search(r"Total charge:\s*([-\d\.]+)", final_block)
        if charge_match:
            results['electronic_properties']['total_charge'] = float(charge_match.group(1))
            
        dipole_match = re.search(r"Dipole moment:\s*([-\d\.E\+]+)\s*([-\d\.E\+]+)\s*([-\d\.E\+]+)\s*Debye", content)
        if dipole_match:
            results['electronic_properties']['dipole_moment_debye'] = {
                "x": float(dipole_match.group(1)),
                "y": float(dipole_match.group(2)),
                "z": float(dipole_match.group(3)),
            }


        energy_pattern = re.compile(r"^\s*(.+?):\s*([-\d\.E\+]+)\s*H\s*([-\d\.E\+]+)\s*eV", re.MULTILINE)
        energy_key_map = {
            "Band energy": "band_energy", "Band free energy (E-TS)": "band_free_energy",
            "Energy H0": "energy_h0", "Energy SCC": "energy_scc",
            "Total Electronic energy": "total_electronic_energy",
            "Repulsive energy": "repulsive_energy", "Total energy": "total_energy",
            "Total Mermin free energy": "total_mermin_free_energy",
            "Force related energy": "force_related_energy"
        }

        for match in energy_pattern.finditer(final_block):
            key = match.group(1).strip()
            if key in energy_key_map:
                json_key = energy_key_map[key]
                results['energies_hartree'][json_key] = float(match.group(2))
                results['energies_eV'][json_key] = float(match.group(3))

    except FileNotFoundError:
        results['summary']['calculation_status'] = 'Failed'
        results['summary']['error'] = f"File not found: {file_path}"
    except Exception as e:
        results['summary']['calculation_status'] = 'Failed'
        results['summary']['error'] = f"An error occurred during parsing: {str(e)}"

    return results
