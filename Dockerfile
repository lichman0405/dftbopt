# Dockerfile (Corrected Final Version)

# Use the official miniconda3 image as a base
FROM continuumio/miniconda3:latest

# Set the working directory to a new project root inside the container
WORKDIR /code

# Copy the Python requirements file first to leverage Docker's layer caching
COPY ./requirements.txt /code/requirements.txt

# Create a conda environment that includes python and dftbplus
RUN conda update -n base -c defaults conda && \
    conda install -c conda-forge --yes python=3.12 dftbplus=24.1=nompi_h5d91ca9_100 && \
    conda clean -afy

# Install Python dependencies using pip into the conda environment
RUN pip install --no-cache-dir -r /code/requirements.txt

# Copy the entire 'app' directory into the working directory.
# This creates the correct /code/app/... structure.
COPY ./app /code/app

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application FROM THE PROJECT ROOT (/code).
# Now, Python can correctly find the 'app' module.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]