# The module is to convert file types between cif and gen formats.
# Author: Shibo Li
# Date: 2025-06-21
# Version: 0.1.0


import os
from ase.io import read, write
from app.utils.logger import console

def convert_structure_file(input_file):
    
    # Check if the input file exists
    console.info(f"Starting conversion for {input_file}...")
    ext = os.path.splitext(input_file)[1].lower()

    if ext == ".cif":
        console.info(f"Converting {input_file} to GEN format...")
        output_file = os.path.splitext(input_file)[0] + ".gen"
        atoms = read(input_file)
        write(output_file, atoms, format='gen')
        console.success(f"{input_file} transformed to {output_file} successfully!")

    elif ext == ".gen":
        console.info(f"Converting {input_file} to CIF format...")
        output_file = os.path.splitext(input_file)[0] + ".cif"
        atoms = read(input_file)
        write(output_file, atoms, format='cif')
        console.success(f"{input_file} transformed to {output_file} successfully!")
        

    else:
        console.error(f"Unsupported file format: {ext}. Please provide a .cif or .gen file.")


def cif_to_gen(input_file):
    """
    Convert a CIF file to GEN format.
    """
    convert_structure_file(input_file)

def gen_to_cif(input_file):
    """
    Convert a GEN file to CIF format.
    """
    convert_structure_file(input_file)