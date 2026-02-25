# VIN Recall Tracker - Quick Reference Guide

## Quick Start

### Option 1: Use the Launcher (Easiest)
```bash
# Windows Command Prompt
run.bat

# Windows PowerShell
.\run.ps1
```

### Option 2: Manual Steps
```bash
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Fetch recall data
python vin_recall_checker.py

# 3. Open tracking GUI
python recall_tracker_gui.py
```

## Workflow

1. **Add VINs** → Edit `vin_settings.json`
2. **Fetch Data** → Run `vin_recall_checker.py`
3. **View & Track** → Run `recall_tracker_gui.py`
4. **Check Manufacturer** → Click URL links in GUI
5. **Mark Resolved** → Check boxes and save

## GUI Features

### Left Panel
- Lists all VINs with resolution status
- Shows format: `VIN - Year Make Model (X/Y resolved)`
- Click to view details

### Right Panel - Vehicle Info
- Display VIN, make, model, year
- Clickable link to manufacturer recall lookup page

### Right Panel - Recalls
Each recall shows:
- ✓ Resolved checkbox (click to toggle)
- Campaign number
- Affected component
- Summary of the issue
- Safety consequences
- Remedy/fix information
- Resolution date (if marked resolved)

### Buttons
- **Refresh Data**: Reload from JSON file
- **Save Changes**: Persist resolution status to disk

## Data Files

| File | Purpose | Edit? |
|------|---------|-------|
| `vin_settings.json` | Input VINs | ✓ Yes |
| `recall_check_results.json` | Recall data & tracking | No (GUI updates) |

## Tips

- **Update recalls**: Re-run the checker script, it preserves resolution status
- **Backup data**: Copy `recall_check_results.json` before major changes
- **Multiple vehicles**: Add all VINs to settings file, run checker once
- **Share URLs**: Copy manufacturer URL from GUI to share with others

## Manufacturer Lookup Process

1. GUI shows manufacturer-specific URL (e.g., owners.hyundaiusa.com)
2. Click the link to open in your browser
3. Enter your VIN on the manufacturer's website
4. They'll show if recall was completed for YOUR specific VIN
5. Return to GUI and check "Resolved" if completed
6. Click "Save Changes"

## Supported Data

- **30+ manufacturers** with direct recall lookup links
- **All NHTSA recalls** for any vehicle year/make/model
- **Unlimited VINs** (limited only by NHTSA API rate limits)

## Keyboard Shortcuts

- `Ctrl+R`: Refresh (when implemented)
- `Ctrl+S`: Save (when implemented)
- Mouse wheel: Scroll through recalls

## Common Issues

**"No recall data found"**
→ Run `python vin_recall_checker.py` first

**GUI window too small**
→ Resize or maximize the window

**Changes not saving**
→ Click "Save Changes" button before closing

**VIN not in list**
→ Add to `vin_settings.json` and re-run checker

## Files Location

```
VINRecallCheck/
├── vin_settings.json          ← Your VINs go here
├── recall_check_results.json  ← Data storage (auto-updated)
├── vin_recall_checker.py      ← Fetch recalls
├── recall_tracker_gui.py      ← View & track
├── manufacturer_urls.py       ← URL mappings
├── run.bat / run.ps1          ← Easy launchers
└── README.md                  ← Full documentation
```
