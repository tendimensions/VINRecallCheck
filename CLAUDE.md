# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VINRecallCheck is a Python desktop application for tracking NHTSA vehicle recall status. Users enter their VINs, fetch recall data from NHTSA's public API, and mark individual recalls as resolved.

## Setup & Run

```bash
# One-time setup
python -m venv .venv
source .venv/Scripts/activate  # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp vin_settings.json.example vin_settings.json  # Add your VINs here

# Run the GUI (primary entry point)
python recall_tracker_gui.py

# Fetch/refresh recall data from NHTSA
python vin_recall_checker.py
```

No test suite exists — this is a single-user utility app.

## Architecture

The app has three layers with a clear data flow:

**`vin_settings.json`** (user-provided VINs) → **`vin_recall_checker.py`** (NHTSA API fetcher) → **`recall_check_results.json`** (local cache) → **`recall_tracker_gui.py`** (Tkinter GUI for tracking resolution)

### Key files

- **`recall_tracker_gui.py`** — Main application. Loads JSON on startup, renders a two-panel Tkinter UI (VIN list left, details right), persists user-marked resolutions back to JSON. Detects unsaved changes via a red status bar.
- **`vin_recall_checker.py`** — CLI fetcher. Decodes VINs via the NHTSA vPIC API, queries recalls by make/model/year, writes results to `recall_check_results.json`. Includes 1-second delays between requests.
- **`manufacturer_urls.py`** — Loads `manufacturer_urls.json` and returns per-manufacturer recall lookup URLs (30+ OEMs). Used by the GUI to show clickable manufacturer links.

### NHTSA API endpoints

```
VIN decode:  https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{VIN}?format=json
Recalls:     https://api.nhtsa.gov/recalls/recallsByVehicle?make={MAKE}&model={MODEL}&modelYear={YEAR}
```

**Important**: NHTSA reports recalls for a vehicle *type*, not whether a specific VIN has been serviced. Users must verify completion on manufacturer websites.

### Data files (git-ignored)

- `vin_settings.json` — Input: `{ "vins": ["VIN1", "VIN2"] }`
- `recall_check_results.json` — Output: array of vehicle objects, each with recalls array and per-recall `resolved` status + date
