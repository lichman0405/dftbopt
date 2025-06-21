FROM continuumio/miniconda3:latest

# Set the working directory inside the container
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN conda update -n base -c defaults conda && \
    conda install -c conda-forge --yes python=3.12 dftbplus=24.1=nompi_h5d91ca9_100 && \
    conda clean -afy

# Install Python dependencies using pip into the conda environment
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the working directory
COPY ./app /app

# Expose the port the app runs on
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]