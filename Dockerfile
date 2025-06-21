FROM continuumio/miniconda3:latest

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN conda update -n base -c defaults conda && \
    conda install -c conda-forge --yes python=3.12 dftbplus=24.1=nompi_h5d91ca9_100 && \
    conda clean -afy

RUN pip install --no-cache-dir -r /code/requirements.txt

COPY ./app /code/app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]