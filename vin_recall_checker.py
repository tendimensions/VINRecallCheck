import json
import requests
from typing import List, Dict
import time


def load_vins_from_json(filepath: str) -> List[str]:
    """Load VINs from a JSON settings file."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
            return data.get('vins', [])
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{filepath}'.")
        return []


def check_vin_recalls(vin: str) -> Dict:
    """
    Check for recalls for a specific VIN using the NHTSA official vPIC API.
    
    Args:
        vin: The Vehicle Identification Number to check
        
    Returns:
        Dict containing the VIN, recall count, and recall details
    """
    # Use the official NHTSA vPIC API endpoint
    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"
    
    # Still use browser-like headers for good measure
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        result = {
            'vin': vin,
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'url': url,
        }
        
        if response.status_code == 200:
            try:
                data = response.json()
                results_data = data.get('Results', [{}])[0]
                
                # Extract vehicle info
                result['make'] = results_data.get('Make', 'Unknown')
                result['model'] = results_data.get('Model', 'Unknown')
                result['year'] = results_data.get('ModelYear', 'Unknown')
                result['error_code'] = results_data.get('ErrorCode', '0')
                
                # Note: This API doesn't directly provide recalls
                # To get recalls, we need to query a separate endpoint
                if result['error_code'] == '0':
                    # Valid VIN - now check for recalls
                    recalls_url = f"https://api.nhtsa.gov/recalls/recallsByVehicle?make={result['make']}&model={result['model']}&modelYear={result['year']}"
                    recalls_response = requests.get(recalls_url, headers=headers, timeout=10)
                    
                    if recalls_response.status_code == 200:
                        recalls_data = recalls_response.json()
                        recalls = recalls_data.get('results', [])
                        result['recall_count'] = len(recalls)
                        
                        if recalls:
                            result['recalls'] = [
                                {
                                    'component': r.get('Component', 'N/A'),
                                    'summary': r.get('Summary', 'N/A'),
                                    'consequence': r.get('Consequence', 'N/A'),
                                    'remedy': r.get('Remedy', 'N/A'),
                                    'nhtsa_campaign_number': r.get('NHTSACampaignNumber', 'N/A'),
                                    'resolved': False  # Default to unresolved
                                }
                                for r in recalls
                            ]
                    else:
                        result['recall_count'] = 0
                        result['recall_error'] = f"Recall lookup failed: HTTP {recalls_response.status_code}"
                else:
                    result['recall_count'] = 0
                    result['error'] = 'Invalid VIN'
                    
            except json.JSONDecodeError:
                result['recall_count'] = 0
                result['error'] = 'Failed to parse JSON response'
        
        return result
        
    except requests.exceptions.RequestException as e:
        return {
            'vin': vin,
            'status_code': None,
            'success': False,
            'url': url,
            'error': str(e)
        }


def main():
    """Main function to check VIN recalls."""
    settings_file = 'vin_settings.json'
    
    print("VIN Recall Checker")
    print("=" * 50)
    
    # Load VINs from JSON file
    vins = load_vins_from_json(settings_file)
    
    if not vins:
        print(f"No VINs found in '{settings_file}'.")
        return
    
    print(f"Found {len(vins)} VIN(s) to check.\n")
    
    # Check each VIN
    results = []
    for i, vin in enumerate(vins, 1):
        print(f"[{i}/{len(vins)}] Checking VIN: {vin}...")
        
        result = check_vin_recalls(vin)
        results.append(result)
        
        if result['success']:
            # Show vehicle info
            vehicle_info = f"{result.get('year', '?')} {result.get('make', '?')} {result.get('model', '?')}"
            print(f"  Vehicle: {vehicle_info}")
            
            recall_count = result.get('recall_count', 0)
            if recall_count > 0:
                print(f"  ⚠ Found {recall_count} recall(s)")
                for recall in result.get('recalls', []):
                    print(f"    - {recall['component']}: {recall['nhtsa_campaign_number']}")
            else:
                print(f"  ✓ No recalls found")
        else:
            error_msg = result.get('error', f"HTTP {result['status_code']}")
            print(f"  ✗ Failed: {error_msg}")
        
        # Be polite - add a small delay between requests
        if i < len(vins):
            time.sleep(1)
    
    # Summary
    print("\n" + "=" * 50)
    print("Summary:")
    successful = sum(1 for r in results if r['success'])
    print(f"  Total VINs checked: {len(results)}")
    print(f"  Successful: {successful}")
    print(f"  Failed: {len(results) - successful}")
    
    # Save results to file
    output_file = 'recall_check_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to '{output_file}'")


if __name__ == "__main__":
    main()
