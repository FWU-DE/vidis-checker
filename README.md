## Installation

### Prerequisites

- Python 3.12 or higher
- OpenAI API key (set as environment variable `OPENAI_API_KEY`)

### Setup

1. **Install uv** (Python package manager):

   ```sh
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Clone the repository and navigate to the project directory**

3. **Create virtual environment** (optional - uv sync will usually create one automatically):

   ```sh
   uv venv
   ```

4. **Install dependencies**:
   ```sh
   uv sync
   ```

## Running the Agent

Run tasks with:

```sh
uv run python run_agent.py [OPTIONS]
```

### Options

- `--url`: URL to crawl
- `--tasks`: Type of tasks to perform (default: all)
  - Available tasks:
    - `login`: Login to the website
    - `legal`: Find and save privacy policy, terms of service, etc.
    - `student`: Explore the website as a student
    - `teacher`: Explore the website as a teacher
    - `register`: Find the registration page
    - `logout`: Find the logout functionality

### Examples

```sh
# Run the legal task
uv run python run_agent.py --url https://schooltogo.de --task legal --output schooltogo_legal.zip
```

### Task Descriptions

- **Login**: Logs in to the page
- **Legal**: Locates and saves privacy policy, legal notices, and terms of service
- **Student**: Navigates through the website as a student would
- **Teacher**: Navigates through the website as a teacher would
- **Register**: Finds the registration page and saves it
- **Logout**: Logs in and then finds the logout functionality

### Output

All results are saved to the `./tmp` directory, organized by task name. Each task folder contains:

## Run Classification

Run classification with:

```sh
uv run python run_classification.py --input_name [INPUT_NAME] --output_name [OUTPUT_NAME]
```

### Options

- `--input_name`: Name of the task to check
- `--output_name`: Path to save the PDF report to

### Examples

```sh
# Check the legal task and save the report to report.pdf
uv run python run_classification.py --input_name schooltogo_legal --output_name schooltogo_legal_classification
```

## Generate Report

Generate report with:

```sh
uv run python generate_report.py --input_name [INPUT_NAME] --output_name [OUTPUT_NAME]
```

### Options

- `--input_name`: Name of the task to check
- `--output_name`: Path to save the PDF report to

### Examples

```sh
uv run python generate_report.py --input_name schooltogo_legal --output_name schooltogo_legal_report
```

## Criteria

You can find the full criteria here:

https://www.vidis.schule/wp-content/uploads/sites/10/2024/12/Pruefkriterien-VIDIS-V0.2.pdf

We check the following:

- RDS-CDN-379 (no)
- RDS-CUC-371 (yes)
- RDS-CUC-372 (yes)
- RDS-CUC-373 (yes)
- RDS-CUC-374 (yes)
- RDS-CUC-375 (currently no - which information should we additionally check?)
- RDS-CUC-376 (currently no as discussed - theoretically some possibilities, but would be very complicated)
- RDS-CUC-377 (currently no - already covered in other criteria, not checked separately)
- RDS-CUC-453
- RDS-DEV-380 (no, technically not possible)
- RDS-DEV-381 (no, technically not possible)
- RDS-DEV-466 (no, technically not possible)
- RDS-DSO-383 (yes)
- RDS-DIL-356 (could be done if we ask for AVV)
- RDS-DIL-357 (no, technically not possible)
- RDS-DIL-358 (no, technically not possible)
- RDS-IPF-364 (yes)
- RDS-IPF-365 (yes)
- RDS-IPF-366 (yes)
- RDS-IPF-367 (yes)
- RDS-AGB-368 (yes)
- RDS-AGB-369 (yes)
- RDS-SPE-370 (yes)
- RDS-UBR-387 (no, technically not possible)
- RDS-UBR-388 (no, technically not possible)
- ITS-ENC-359 (yes)
- ITS-ENC-360 (yes)
- ITS-ENC-361 (yes)
