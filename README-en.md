# DFTB+ Automated Calculation Service (DFTB-Opt-Service)

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![DFTB+](https://img.shields.io/badge/DFTB+-24.1-orange.svg)](https://dftbplus.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)

<a href="README.md">中文</a>
·
<a href="https://github.com/lichman0405/dftbopt/issues">Report Bug</a>
·
<a href="https://github.com/lichman0405/dftbopt/issues">New Features</a>


A RESTful Web service based on FastAPI designed to encapsulate DFTB+ calculation workflows into simple and easy-to-use API endpoints. Users can upload crystal structure files (CIF format) to automatically perform geometry optimizations on materials like MOFs and obtain structured calculation results.

## ✨ Key Features

* **RESTful API**: Provides modern, standard API endpoints, making it easy to integrate into automated workflows or frontend applications.
* **File Upload**: Supports direct upload of `.cif` structure files.
* **Parametric Calculation**: Allows dynamic adjustment of calculation methods (`GFN1-xTB`, `GFN2-xTB`) and convergence criteria (`fmax`) via API parameters.
* **Automated Workflow**: Internally handles file format conversion (CIF ↔ GEN), generates DFTB+ input files, runs calculations, and parses outputs automatically.
* **Structured Response**: Returns clear, structured calculation results in JSON format, with the optimized structure file embedded inline as a Base64-encoded string for easy downstream processing.
* **Containerized Deployment**: Uses Docker and Conda for full environment isolation and one-click deployment, solving the challenge of compiling `dftb+` and managing dependencies.

## 📁 Project Structure

The project follows a modular design, clearly separating API, service logic, data models, and core functionality for easy maintenance and future extensions.

```
DFTOPT/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── api.py
│   │   └── routes/
│   │       └── optimization.py
│   ├── core/
│   │   ├── dftb_runner.py
│   │   └── output_parser.py
│   ├── schemas/
│   │   └── optimization.py
│   ├── services/
│   │   └── dftb_service.py
│   └── utils/
│       ├── file_convertor.py
│       └── logger.py
│   └── workspace/
│       └── .gitkeep
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## 🚀 Installation & Startup

This project is designed to run inside a Docker container to ensure environment consistency and reproducibility.

### Prerequisites

* [Docker](https://www.docker.com/products/docker-desktop/)
* [Docker Compose](https://docs.docker.com/compose/install/)

### Steps

1. **Clone or download the project**  
   Place all project files on your local filesystem.

2. **Configure computational resources**  
   For large calculations, make sure to allocate enough memory to the Docker engine in Docker Desktop settings (recommend **16GB** or more).

3. **Build and start the service**  
   In the project root directory, open a terminal and run:

   ```bash
   docker-compose up --build
   ```

   To run the service in the background, add the `-d` flag.

4. **Verify the service**  
   Once up, visit [http://localhost:8000/docs](http://localhost:8000/docs) to use the interactive API docs.

## 🛠️ API Usage

### Endpoint: `POST /api/v1/optimize/`

This endpoint submits a geometry optimization job.

#### Request Body (`multipart/form-data`)

| Key          | Type   | Required | Description                                    |
| ------------ | ------ | -------- | ---------------------------------------------- |
| `input_file` | File   | **Yes**  | `.cif` format only                             |
| `fmax`       | float  | No       | Force convergence threshold (default 0.1 eV/Å) |
| `method`     | string | No       | "GFN1-xTB" or "GFN2-xTB" (default: "GFN1-xTB") |

#### Successful Response (`200 OK`)

Includes full calculation results and Base64-encoded optimized structure.

#### Failure Responses

* `400 Bad Request`: Invalid parameters or file
* `422 Unprocessable Entity`: Calculation failed
* `500 Internal Server Error`: Server error

### Example Client (Python)

```python
import requests
import base64
import os

API_URL = "http://127.0.0.1:8000/api/v1/optimize/"
cif_file_path = "/path/to/your/structure.cif"
payload = {'fmax': '0.05', 'method': 'GFN1-xTB'}

with open(cif_file_path, 'rb') as f:
    files = {'input_file': (os.path.basename(cif_file_path), f, 'chemical/x-cif')}
    response = requests.post(API_URL, data=payload, files=files, timeout=600)
    response.raise_for_status()
    data = response.json()
    b64_string = data['optimized_structure_cif_b64']
    decoded = base64.b64decode(b64_string).decode('utf-8')
    with open("optimized_" + os.path.basename(cif_file_path), "w") as out_f:
        out_f.write(decoded)
```

## ⚠️ Known Issues

* Large systems (>600-700 atoms) may cause segmentation faults due to high memory or deep numerical bugs.
* Ensure ample Docker memory (e.g., 32GB+) and keep `ulimits` settings.
* Report persistent issues to DFTB+ community.