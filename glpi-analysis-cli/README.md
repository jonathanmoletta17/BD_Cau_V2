# GLPI Data Analyst CLI

A minimal, high-performance CLI tool to process and analyze GLPI data using PandasAI.

## Features
- **Data Export**: Extracts data from Postgres and creates `dados_2023.csv`, `dados_2024.csv`, `dados_2025.csv`.
- **Analysis**: Uses LLM (OpenAI) to answer natural language questions about the data.
- **Reporting**: Generates text logs and charts.

## Setup

### Option 1: Docker (Recommended)
Avoids dependency issues on Windows.

1.  Build the image:
    ```bash
    docker build -t glpi-analyst .
    ```
2.  Run Export (Requires access to DB):
    ```bash
    # Assuming DB is on host machine at localhost:5432
    # You might need --network="host" or special DNS
    docker run --env-file .env --network="host" -v $(pwd):/app glpi-analyst --export
    ```
3.  Run Analysis:
    ```bash
    docker run --env-file .env -v $(pwd):/app glpi-analyst "Compare ticket volume between 2023 and 2024"
    ```

### Option 2: Local Python
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: On Windows, you might need C++ Build Tools for some packages.*
2.  Run:
    ```bash
    python main.py --export
    python main.py "Your question here"
    ```

## Configuration
Create a `.env` file:
```env
POSTGRES_USER=glpi_user
POSTGRES_PASSWORD=glpi_dev_password
POSTGRES_HOST=localhost
POSTGRES_DB=glpi_data
OPENAI_API_KEY=sk-your-key
```
