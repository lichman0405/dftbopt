FROM continuumio/miniconda3:latest

# Set the working directory inside the container
WORKDIR /app

# Copy the Python requirements file first to leverage Docker's layer caching
COPY ./requirements.txt /app/requirements.txt

# Create a conda environment that includes python and dftbplus
# This uses the user-provided command for dftb+ installation
RUN conda update -n base -c defaults conda && \
    conda install -c conda-forge --yes python=3.12 dftbplus=24.1=nompi_h5d91ca9_100 && \
    conda clean -afy


RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

# Expose the port the app runs on
EXPOSE 8000


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]