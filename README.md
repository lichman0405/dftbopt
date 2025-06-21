# DFTB+ 自动化计算服务 (DFTB-Opt-Service)

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![DFTB+](https://img.shields.io/badge/DFTB+-24.1-orange.svg)](https://dftbplus.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)

<a href="README-en.md">English</a>
·
<a href="https://github.com/lichman0405/dftbopt/issues">报告 Bug</a>
·
<a href="https://github.com/lichman0405/dftbopt/issues">请求新功能</a>

一个基于 FastAPI 的 RESTful Web 服务，旨在将 DFTB+ 的计算流程封装为简单易用的 API 接口。用户可以通过上传晶体结构文件（CIF 格式）来对 MOF 等材料进行自动化的几何优化，并获取结构化的计算结果。

## ✨ 主要特性

* **RESTful API**: 提供现代、标准的 API 接口，便于集成到自动化工作流或前端应用中。
* **文件上传**: 支持直接上传 `.cif` 格式的结构文件。
* **参数化计算**: 支持通过 API 参数动态调整计算方法（`GFN1-xTB`, `GFN2-xTB`）和收敛标准（`fmax`）。
* **自动流程**: 服务内部自动处理文件格式转换 (CIF ↔ GEN)、生成 DFTB+ 输入文件、执行计算、解析输出。
* **结构化响应**: 以 JSON 格式返回清晰、结构化的计算结果，并将优化后的结构文件以 Base64 编码形式内联在响应中，便于下游程序处理。
* **容器化部署**: 基于 Docker 和 Conda，实现了环境的完全隔离和一键式部署，解决了 `dftb+` 编译和依赖管理的难题。

## 📁 项目结构

项目采用了模块化的设计，将 API、服务逻辑、数据模型和核心功能清晰分离，便于维护和未来扩展。

```
DFTOPT/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用启动入口
│   ├── api/                    # API 接口层
│   │   ├── api.py              # -> 汇集所有路由
│   │   └── routes/
│   │       └── optimization.py   # -> 优化功能的路由
│   ├── core/                   # 核心功能层
│   │   ├── dftb_runner.py      # -> 封装 dftb+ 进程调用
│   │   └── output_parser.py    # -> 封装输出文件解析
│   ├── schemas/                # 数据模型层 (Pydantic)
│   │   └── optimization.py
│   ├── services/               # 业务逻辑层
│   │   └── dftb_service.py
│   └── utils/                  # 通用工具
│       ├── file_convertor.py   # (用户提供)
│       └── logger.py           # (用户提供)
│   └── workspace/              # 临时文件工作区
│       └── .gitkeep
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## 🚀 安装与启动

本项目被设计为在 Docker 容器中运行，以确保环境的一致性和可复现性。

### 先决条件

* [Docker](https://www.docker.com/products/docker-desktop/)
* [Docker Compose](https://docs.docker.com/compose/install/)

### 步骤

1.  **克隆或下载项目**
    将本项目所有文件放置在您的本地文件系统。

2.  **配置计算资源**
    对于大型计算，请务必在 Docker Desktop 的设置中为 Docker 引擎分配足够的内存（建议 **16GB** 或更多）。

3.  **构建并启动服务**
    在项目的根目录下（即包含 `docker-compose.yml` 文件的目录），打开终端并运行：
    ```bash
    docker-compose up --build
    ```
    * `--build` 参数会在首次启动时强制构建镜像。
    * 如果希望服务在后台运行，请添加 `-d` 标志：`docker-compose up --build -d`。

4.  **验证服务**
    服务成功启动后，您可以在浏览器中访问 [http://localhost:8000/docs](http://localhost:8000/docs) 来查看并使用自动生成的交互式 API 文档。

## 🛠️ API 使用说明

### 端点: `POST /api/v1/optimize/`

该端点用于提交一个几何优化任务。

#### 请求体 (`multipart/form-data`)

| 参数名 (`key`) | 类型 (`Type`) | 是否必需 | 描述/约束 |
| :--- | :--- | :--- | :--- |
| `input_file` | File | **是** | 待计算的晶体结构文件，必须是 `.cif` 格式。 |
| `fmax` | float | 否 | 几何优化的力的收敛阈值 (eV/Å)。**默认值: 0.1**。 |
| `method` | string | 否 | 使用的半经验方法。必须是 `"GFN1-xTB"` 或 `"GFN2-xTB"`。**默认值: "GFN1-xTB"**。 |

#### 成功响应 (`200 OK`)

返回一个包含所有结果的 JSON 对象。
<details>
<summary>点击查看完整的成功响应示例</summary>

```json
{
  "status": "success",
  "request_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
  "input_parameters": {
    "original_filename": "my_mof.cif",
    "method": "GFN1-xTB",
    "fmax_eV_A": 0.1
  },
  "detailed_results": {
    "summary": {
      "warnings": ["dipole moment is not defined absolutely!"],
      "convergence_status": "Geometry converged",
      "calculation_status": "Success"
    },
    "convergence_info": { "scc_converged": true },
    "electronic_properties": {
      "fermi_level_eV": -10.49,
      "total_charge": 0.0,
      "dipole_moment_debye": {"x": -3.01, "y": -0.02, "z": 4.59}
    },
    "energies_eV": {
        "total_mermin_free_energy": -7629.55,
        "total_energy": -7629.54
        // ... 其他能量项
    },
    "energies_hartree": {
        "total_mermin_free_energy": -280.380,
        "total_energy": -280.380
        // ... 其他能量项
    }
  },
  "optimized_structure_cif_b64": "ZGF0YV9......(很长的 Base64 字符串)......Cg=="
}
```
</details>

#### 失败响应

* `400 Bad Request`: 输入参数或文件类型无效。
* `422 Unprocessable Entity`: 计算过程失败（例如，对于特定结构不稳定）。
* `500 Internal Server Error`: 服务器内部发生意外错误。

### 客户端调用示例 (Python)

下面的 Python 脚本演示了如何调用此 API，并处理返回的结果。

```python
import requests
import base64
import json

# API 端点 URL
API_URL = "[http://127.0.0.1:8000/api/v1/optimize/](http://127.0.0.1:8000/api/v1/optimize/)"

# 输入文件路径
cif_file_path = "/path/to/your/structure.cif"

# 请求参数
payload = {
    'fmax': '0.05',
    'method': 'GFN1-xTB'
}

# 准备上传的文件
with open(cif_file_path, 'rb') as f:
    files_to_upload = {
        'input_file': (os.path.basename(cif_file_path), f, 'chemical/x-cif')
    }

    try:
        print("🚀 Submitting optimization job...")
        response = requests.post(API_URL, data=payload, files=files_to_upload, timeout=600)
        response.raise_for_status() # 如果状态码不是 2xx，则抛出异常

        # 解析成功的响应
        data = response.json()
        print("✅ Job successful!")

        # 打印部分计算结果
        print("\n--- Calculation Summary ---")
        print(f"Convergence Status: {data['detailed_results']['summary']['convergence_status']}")
        print(f"Total Energy (eV): {data['detailed_results']['energies_eV']['total_energy']}")

        # 解码 Base64 并保存优化后的结构文件
        b64_string = data['optimized_structure_cif_b64']
        decoded_cif_content = base64.b64decode(b64_string).decode('utf-8')

        output_filename = f"optimized_{os.path.basename(cif_file_path)}"
        with open(output_filename, "w") as out_f:
            out_f.write(decoded_cif_content)

        print(f"\n✅ Optimized structure saved to: {output_filename}")

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Error: {e.response.status_code}")
        print(f"   Detail: {e.response.json().get('detail', 'No details provided.')}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")

```

## ⚠️ 已知问题与限制

* **大型体系的稳定性**: 对于非常大的体系（例如 >600-700 原子），`conda-forge` 渠道安装的 `dftb+ 24.1` 版本在处理某些结构时可能会因为**段错误 (Segmentation Fault)** 而崩溃。
* **根本原因**: 这很可能是由于计算任务对内存和堆栈空间的巨大需求，或 `dftb+`/`tblite` 库中与特定体系相关的深层次数值不稳定性/Bug。
* **建议**: 在处理大型结构时，请确保为 Docker 分配了充足的物理内存（例如 32GB+），并在 `docker-compose.yml` 中保留 `ulimits` 设置。如果问题依然存在，建议向 DFTB+ 官方社区报告此问题。
