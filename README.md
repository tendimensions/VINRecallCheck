# VIN Recall Tracker

A Python application to check Vehicle Identification Numbers (VINs) against the NHTSA recall database and track recall resolution status with a graphical user interface.

## Features

- **Automated VIN Checking**: Query NHTSA's official API to retrieve recall information directly from the GUI
- **Graphical Interface**: All-in-one application - no command line needed!
- **Recall Tracking**: Mark recalls as resolved and track resolution dates
- **Manufacturer Links**: Quick access to manufacturer-specific recall lookup pages
- **Persistent Storage**: Track recall status across multiple sessions
- **Smart Updates**: Preserves your resolution tracking when refreshing recall data

## Why Use the NHTSA API?

When you use `curl` or web scraping, manufacturer websites often block automated requests (HTTP 403 Forbidden). This tool uses the **official NHTSA vPIC API** which is designed for programmatic access.

**Important Limitation**: The NHTSA API shows which recalls exist for a vehicle type, but does NOT track whether a specific VIN has had the recall work completed. Only manufacturers track completion status. This tool helps you:

1. Get recall information from NHTSA
2. Check manufacturer websites for VIN-specific completion status
3. Track which recalls you've verified as resolved

## Setup

1. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1  # Windows PowerShell
   # or
   .\.venv\Scripts\activate.bat   # Windows Command Prompt
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `vin_settings.json`** with your VINs:

   Copy the example file and add your VINs:
   
   ```bash
   cp vin_settings.json.example vin_settings.json
   ```
   
   Then edit `vin_settings.json`:
   
   ```json
   {
     "vins": [
       "YOUR_VIN_HERE",
       "ANOTHER_VIN_HERE"
     ]
   }
   ```
   
   **Note**: This file is ignored by git to keep your VIN data private.

4. **Launch the GUI**:

   ```bash
   python recall_tracker_gui.py
   ```

That's it! The GUI will guide you through the rest.

## Usage

### Quick Start

Simply run the GUI application:

```bash
python recall_tracker_gui.py
```

The application will automatically:
- Check if `vin_settings.json` exists (shows setup instructions if missing)
- Check if recall data exists (offers to fetch from NHTSA if missing)
- Display all your vehicles and their recall status

### Working with the GUI

#### First Time Setup

1. **Launch the application**
2. If `vin_settings.json` doesn't exist, the GUI will show you the format to create it
3. Create the file, then restart the GUI (or click **"NHTSA Check VINs"**)
4. Wait for the progress window to complete

#### Checking for New Recalls

Click the **"NHTSA Check VINs"** button at any time to:
- Add new VINs from your settings file
- Refresh recall information for existing VINs
- Your resolution tracking is preserved automatically

#### Tracking Recall Resolution

1. **Select a VIN** from the left panel
2. **View recall details** in the right panel
3. **Click the manufacturer link** to verify completion on their website
4. **Check the "Resolved" box** if the recall has been completed
5. **Click "Save Changes"** to persist your tracking

The GUI displays:
- Vehicle information (year, make, model)
- Clickable manufacturer recall lookup URLs
- Detailed recall information including:
  - NHTSA campaign numbers
  - Affected components
  - Safety consequences
  - Remedy information
- Resolution status and dates

### Step 3: Verify with Manufacturer

1. Select a VIN in the GUI
2. Click the manufacturer recall lookup link
3. Enter the VIN on the manufacturer's website
4. Check if the recall has been completed for your specific VIN
5. If completed, check the "Resolved" box in the GUI
6. Click "Save Changes" to persist your tracking data

## How It WorksYour VINs)
        ↓
recall_tracker_gui.py (Click "NHTSA Check VINs")
        ↓
NHTSA API (Fetch recalls)
        ↓
recall_check_results.json (Stored locally)
        ↓
GUI Display (View & mark resolved)
        ↓
Save Changes → recall_check_results.json (Updated
recall_check_results.json (Recall data + tracking)
        ↓
recall_tracker_gui.py (View & Mark Resolved)
        ↓
recall_check_results.json (Updated with resolution status)
```

### API Endpoints Used

1. **VIN Decoder**: `https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{VIN}`
   - Decodes VIN to get year, make, model
   
2. **Recalls Lookup**: `https://api.nhtsa.gov/recalls/recallsByVehicle`
   - Retrieves recalls by make/model/year

### Supported Manufacturers

The tool includes direct links to recall lookup pages for 30+ manufacturers including:
- Hyundai, Kia, Genesis
- Jeep, Dodge, Chrysler, RAM, Fiat, Alfa Romeo (Stellantis)
- Ford, Lincoln
- Chevrolet, GMC, Buick, Cadillac (GM)
- Honda, Acura
- Toyota, Lexus
- Nissan, Infiniti
- Mazda, Subaru, Volkswagen, Audi, Porsche, BMW, Mercedes-Benz, Volvo
- Tesla, Rivian, Lucid
Your VINs (you create this)
├── recall_tracker_gui.py           # Main GUI application (START HERE)
├── manufacturer_urls.py            # Manufacturer recall lookup URLs
├── recall_check_results.json       # Output: Recall data with tracking
├── vin_recall_checker.py           # Command-line version (optional)
├── .venv/                          # Virtual environment (created during setup)
├── .gitignore                      # Git ignore file
├── vin_settings.json               # Input: List of VINs to check
├── vin_recall_checker.py           # Command-line checker (fetches from NHTSA)
├── recall_tracker_gui.py           # GUI application (track resolution)
├── manufacturer_urls.py            # Manufacturer recall lookup URLs
├── recall_check_results.json       # Output: Recall data with tracking status
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## JSON Data Structure

### Input (vin_settings.json)
```json
{
  "vins": [
    "KM8KRDAF9PU227503",
    "1J4FA54167L116295"
  ]
}
```

### Output (recall_check_results.json)
```json
[
  {
    "vin": "KM8KRDAF9PU227503",
    "status_code": 200,
    "success": true,
    "make": "HYUNDAI",
    "model": "Ioniq 5",
    "year": "2023",
    "recall_count": 3,
    "recalls": [
      {
        "component": "POWER TRAIN:DRIVELINE:DRIVESHAFT",
        "summary": "...",
        "consequence": "...",
        "remedy": "...",
        "nhtsa_campaign_number": "24V065000",
        "resolved": true,
        "resolved_date": "2026-02-24"
      }
    ]
  }
]
```

## Notes

- The script includes a 1-second delay between VIN requests to be respectful to the NHTSA server
- All data is stored locally in JSON format
- The GUI uses tkinter (included with Python)
- Resolution tracking is local only - not synced with manufacturers
- Re-running the checker will preserve existing resolution status if the recall still exists

## TroVIN Settings File"**: Create `vin_settings.json` with your VINs (see Setup section)

**No data showing**: Click the "NHTSA Check VINs" button to fetch recall data

**VIN not found**: Verify the VIN is correct (17 characters, no I, O, or Q)

**No recalls showing**: Good news! NHTSA has no open recalls for that vehicle

**Want to add more VINs**: Edit `vin_settings.json`, then click "NHTSA Check VINs"

**Changes not saving**: Click "Save Changes" button before closing

**Connection errors**: Check your internet connection; NHTSA API may be temporarily unavailable

**Want to refresh data**: Run `vin_recall_checker.py` again - it will update the recall list while preserving your resolution tracking

## Privacy & Security

- All data is stored locally on your computer
- No data is sent to third parties
- NHTSA API queries are read-only public information
- Manufacturer websites are accessed via your browser when you click links
