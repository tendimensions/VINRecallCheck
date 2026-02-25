import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import webbrowser
import requests
import time
from typing import List, Dict
from datetime import datetime
from manufacturer_urls import get_recall_url


class RecallTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("VIN Recall Tracker")
        self.root.geometry("1200x800")
        
        self.data_file = 'recall_check_results.json'
        self.settings_file = 'vin_settings.json'
        self.recall_data = []
        self.is_checking = False
        
        self.setup_ui()
        self.check_startup_conditions()
        
    def check_startup_conditions(self):
        """Check for required files on startup."""
        import os
        
        # Check for vin_settings.json
        if not os.path.exists(self.settings_file):
            messagebox.showwarning(
                "No VIN Settings File",
                f"The file '{self.settings_file}' was not found.\n\n"
                "Please create this file with the following format:\n\n"
                '{\n'
                '  "vins": [\n'
                '    "YOUR_VIN_HERE",\n'
                '    "ANOTHER_VIN_HERE"\n'
                '  ]\n'
                '}\n\n'
                "Add your Vehicle Identification Numbers (VINs) to check for recalls."
            )
            return
        
        # Load existing data if available
        self.load_data()
        
        # Check if we have data
        if not self.recall_data:
            result = messagebox.askyesno(
                "No Recall Data",
                f"No recall data found in '{self.data_file}'.\n\n"
                "Would you like to fetch recall information from NHTSA now?"
            )
            if result:
                self.check_vins_from_nhtsa()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="VIN Recall Tracker", 
                               font=('Helvetica', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=0, pady=(0, 10), sticky=tk.E)
        
        check_vins_btn = ttk.Button(button_frame, text="NHTSA Check VINs", 
                                    command=self.check_vins_from_nhtsa,
                                    style='Accent.TButton')
        check_vins_btn.grid(row=0, column=0, padx=5)
        
        refresh_btn = ttk.Button(button_frame, text="Refresh Data", 
                                 command=self.load_data)
        refresh_btn.grid(row=0, column=1, padx=5)
        
        save_btn = ttk.Button(button_frame, text="Save Changes", 
                             command=self.save_data)
        save_btn.grid(row=0, column=2, padx=5)
        
        # Paned window for VIN list and details
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Left panel - VIN list
        left_frame = ttk.Frame(paned, padding="5")
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="VINs", font=('Helvetica', 12, 'bold')).pack(anchor=tk.W)
        
        # VIN Listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.vin_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                      font=('Courier', 10))
        self.vin_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.vin_listbox.yview)
        
        self.vin_listbox.bind('<<ListboxSelect>>', self.on_vin_select)
        
        # Right panel - Details
        right_frame = ttk.Frame(paned, padding="5")
        paned.add(right_frame, weight=3)
        
        self.details_frame = right_frame
        self.setup_details_panel()
        
    def setup_details_panel(self):
        """Setup the details panel."""
        # Vehicle info frame
        info_frame = ttk.LabelFrame(self.details_frame, text="Vehicle Information", 
                                    padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.vin_label = ttk.Label(info_frame, text="VIN: -", 
                                   font=('Courier', 11, 'bold'))
        self.vin_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.vehicle_label = ttk.Label(info_frame, text="Vehicle: -")
        self.vehicle_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.url_frame = ttk.Frame(info_frame)
        self.url_frame.grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Recalls frame
        recalls_frame = ttk.LabelFrame(self.details_frame, text="Recalls", 
                                       padding="10")
        recalls_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas with scrollbar for recalls
        canvas = tk.Canvas(recalls_frame)
        scrollbar = ttk.Scrollbar(recalls_frame, orient="vertical", 
                                  command=canvas.yview)
        self.scrollable_recalls = ttk.Frame(canvas)
        
        self.scrollable_recalls.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_recalls, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def load_data(self):
        """Load recall data from JSON file."""
        import os
        
        if not os.path.exists(self.data_file):
            self.recall_data = []
            self.populate_vin_list()
            return
            
        try:
            with open(self.data_file, 'r') as f:
                self.recall_data = json.load(f)
            self.populate_vin_list()
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON file format.")
            self.recall_data = []
    
    def populate_vin_list(self):
        """Populate the VIN listbox."""
        self.vin_listbox.delete(0, tk.END)
        
        for item in self.recall_data:
            vin = item.get('vin', 'Unknown')
            make = item.get('make', '?')
            model = item.get('model', '?')
            year = item.get('year', '?')
            recall_count = item.get('recall_count', 0)
            
            # Count resolved recalls
            resolved_count = 0
            if 'recalls' in item and item['recalls']:
                resolved_count = sum(1 for r in item['recalls'] 
                                   if r.get('resolved', False))
            
            display_text = f"{vin} - {year} {make} {model} ({resolved_count}/{recall_count} resolved)"
            self.vin_listbox.insert(tk.END, display_text)
    
    def on_vin_select(self, event):
        """Handle VIN selection."""
        selection = self.vin_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index >= len(self.recall_data):
            return
        
        self.display_vin_details(index)
    
    def display_vin_details(self, index):
        """Display details for selected VIN."""
        data = self.recall_data[index]
        
        # Update vehicle info
        vin = data.get('vin', 'Unknown')
        make = data.get('make', 'Unknown')
        model = data.get('model', 'Unknown')
        year = data.get('year', 'Unknown')
        
        self.vin_label.config(text=f"VIN: {vin}")
        self.vehicle_label.config(text=f"Vehicle: {year} {make} {model}")
        
        # Clear and update manufacturer URL
        for widget in self.url_frame.winfo_children():
            widget.destroy()
        
        recall_url = get_recall_url(make)
        url_label = ttk.Label(self.url_frame, 
                             text="Manufacturer Recall Lookup:", 
                             font=('Helvetica', 9, 'bold'))
        url_label.pack(side=tk.LEFT, padx=(0, 5))
        
        url_link = ttk.Label(self.url_frame, text=recall_url, 
                            foreground="blue", cursor="hand2",
                            font=('Helvetica', 9, 'underline'))
        url_link.pack(side=tk.LEFT)
        url_link.bind("<Button-1>", lambda e: webbrowser.open(recall_url))
        
        # Display recalls
        for widget in self.scrollable_recalls.winfo_children():
            widget.destroy()
        
        recalls = data.get('recalls', [])
        if not recalls:
            no_recalls_label = ttk.Label(self.scrollable_recalls, 
                                        text="✓ No recalls found for this vehicle",
                                        foreground="green",
                                        font=('Helvetica', 11, 'bold'))
            no_recalls_label.pack(pady=20)
        else:
            for i, recall in enumerate(recalls):
                self.create_recall_widget(index, i, recall)
    
    def create_recall_widget(self, vin_index, recall_index, recall):
        """Create a widget for a single recall."""
        # Frame for this recall
        recall_frame = ttk.Frame(self.scrollable_recalls, relief=tk.RIDGE, 
                                 borderwidth=2)
        recall_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Header with checkbox
        header_frame = ttk.Frame(recall_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        resolved = recall.get('resolved', False)
        resolved_var = tk.BooleanVar(value=resolved)
        
        check_btn = ttk.Checkbutton(
            header_frame, 
            text="Resolved",
            variable=resolved_var,
            command=lambda: self.toggle_resolved(vin_index, recall_index, 
                                                resolved_var.get())
        )
        check_btn.pack(side=tk.LEFT)
        
        # Campaign number
        campaign = recall.get('nhtsa_campaign_number', 'N/A')
        campaign_label = ttk.Label(header_frame, 
                                  text=f"Campaign: {campaign}",
                                  font=('Helvetica', 10, 'bold'))
        campaign_label.pack(side=tk.LEFT, padx=10)
        
        # Component
        component = recall.get('component', 'N/A')
        component_label = ttk.Label(header_frame, text=f"Component: {component}",
                                   foreground="navy")
        component_label.pack(side=tk.LEFT)
        
        # Details frame
        details_frame = ttk.Frame(recall_frame)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Summary
        summary = recall.get('summary', 'N/A')
        summary_text = tk.Text(details_frame, height=3, wrap=tk.WORD, 
                              font=('Helvetica', 9))
        summary_text.insert('1.0', f"Summary: {summary}")
        summary_text.config(state=tk.DISABLED, background='#f0f0f0')
        summary_text.pack(fill=tk.X, pady=2)
        
        # Consequence
        consequence = recall.get('consequence', 'N/A')
        consequence_text = tk.Text(details_frame, height=2, wrap=tk.WORD,
                                  font=('Helvetica', 9))
        consequence_text.insert('1.0', f"Consequence: {consequence}")
        consequence_text.config(state=tk.DISABLED, background='#fff5f5')
        consequence_text.pack(fill=tk.X, pady=2)
        
        # Remedy
        remedy = recall.get('remedy', 'N/A')
        remedy_text = tk.Text(details_frame, height=2, wrap=tk.WORD,
                             font=('Helvetica', 9))
        remedy_text.insert('1.0', f"Remedy: {remedy}")
        remedy_text.config(state=tk.DISABLED, background='#f5fff5')
        remedy_text.pack(fill=tk.X, pady=2)
        
        # Resolution info if resolved
        if resolved and recall.get('resolved_date'):
            resolved_label = ttk.Label(details_frame, 
                                      text=f"Resolved: {recall['resolved_date']}",
                                      foreground="green",
                                      font=('Helvetica', 9, 'italic'))
            resolved_label.pack(pady=2)
    
    def toggle_resolved(self, vin_index, recall_index, is_resolved):
        """Toggle the resolved status of a recall."""
        if vin_index >= len(self.recall_data):
            return
        
        recalls = self.recall_data[vin_index].get('recalls', [])
        if recall_index >= len(recalls):
            return
        
        recalls[recall_index]['resolved'] = is_resolved
        
        if is_resolved:
            # Add resolution date
            recalls[recall_index]['resolved_date'] = datetime.now().strftime('%Y-%m-%d')
        else:
            # Remove resolution date
            recalls[recall_index].pop('resolved_date', None)
        
        # Refresh the display
        self.populate_vin_list()
        self.display_vin_details(vin_index)
        
        messagebox.showinfo("Updated", 
            "Recall status updated. Click 'Save Changes' to persist.")
    
    def load_vins_from_settings(self):
        """Load VINs from the settings JSON file."""
        import os
        
        if not os.path.exists(self.settings_file):
            messagebox.showerror("Error", 
                f"Settings file '{self.settings_file}' not found.\n\n"
                "Please create it with your VINs.")
            return []
        
        try:
            with open(self.settings_file, 'r') as f:
                data = json.load(f)
                return data.get('vins', [])
        except json.JSONDecodeError:
            messagebox.showerror("Error", 
                f"Invalid JSON in '{self.settings_file}'.")
            return []
        except Exception as e:
            messagebox.showerror("Error", 
                f"Failed to load settings: {str(e)}")
            return []
    
    def check_single_vin(self, vin: str) -> Dict:
        """
        Check for recalls for a specific VIN using the NHTSA official vPIC API.
        
        Args:
            vin: The Vehicle Identification Number to check
            
        Returns:
            Dict containing the VIN, recall count, and recall details
        """
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/{vin}?format=json"
        
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
    
    def merge_recall_data(self, new_data: Dict, existing_data: Dict) -> Dict:
        """
        Merge new recall data with existing data, preserving resolution status.
        
        Args:
            new_data: Newly fetched data from NHTSA
            existing_data: Existing data with possible resolution tracking
            
        Returns:
            Merged data dictionary
        """
        # Start with new data
        merged = new_data.copy()
        
        # If there are recalls in both, merge them
        if 'recalls' in new_data and 'recalls' in existing_data:
            new_recalls = new_data['recalls']
            old_recalls = existing_data['recalls']
            
            # Create a map of old recalls by campaign number
            old_recalls_map = {
                r.get('nhtsa_campaign_number'): r 
                for r in old_recalls
            }
            
            # Merge resolution status
            for new_recall in new_recalls:
                campaign_num = new_recall.get('nhtsa_campaign_number')
                if campaign_num in old_recalls_map:
                    old_recall = old_recalls_map[campaign_num]
                    # Preserve resolution status and date
                    new_recall['resolved'] = old_recall.get('resolved', False)
                    if 'resolved_date' in old_recall:
                        new_recall['resolved_date'] = old_recall['resolved_date']
        
        return merged
    
    def check_vins_from_nhtsa(self):
        """Check all VINs from settings file against NHTSA API."""
        if self.is_checking:
            messagebox.showwarning("Busy", "Already checking VINs. Please wait...")
            return
        
        vins = self.load_vins_from_settings()
        
        if not vins:
            return
        
        self.is_checking = True
        
        # Create progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Checking VINs")
        progress_window.geometry("500x300")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Center the window
        progress_window.update_idletasks()
        x = (progress_window.winfo_screenwidth() // 2) - (500 // 2)
        y = (progress_window.winfo_screenheight() // 2) - (300 // 2)
        progress_window.geometry(f"500x300+{x}+{y}")
        
        frame = ttk.Frame(progress_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        title_label = ttk.Label(frame, text="Fetching Recall Data from NHTSA", 
                               font=('Helvetica', 12, 'bold'))
        title_label.pack(pady=(0, 10))
        
        progress_text = scrolledtext.ScrolledText(frame, height=10, width=60)
        progress_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        progress_bar = ttk.Progressbar(frame, mode='determinate', maximum=len(vins))
        progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        close_btn = ttk.Button(frame, text="Close", state=tk.DISABLED,
                              command=progress_window.destroy)
        close_btn.pack()
        
        def log_message(msg):
            progress_text.insert(tk.END, msg + '\n')
            progress_text.see(tk.END)
            progress_window.update()
        
        log_message(f"Found {len(vins)} VIN(s) to check.\n")
        
        # Create a map of existing data by VIN
        existing_data_map = {item['vin']: item for item in self.recall_data}
        
        new_results = []
        
        for i, vin in enumerate(vins, 1):
            log_message(f"[{i}/{len(vins)}] Checking VIN: {vin}...")
            
            result = self.check_single_vin(vin)
            
            # Merge with existing data if available
            if vin in existing_data_map:
                result = self.merge_recall_data(result, existing_data_map[vin])
            
            new_results.append(result)
            
            if result['success']:
                vehicle_info = f"{result.get('year', '?')} {result.get('make', '?')} {result.get('model', '?')}"
                recall_count = result.get('recall_count', 0)
                log_message(f"  ✓ {vehicle_info} - {recall_count} recall(s)")
            else:
                error_msg = result.get('error', f"HTTP {result['status_code']}")
                log_message(f"  ✗ Failed: {error_msg}")
            
            progress_bar['value'] = i
            progress_window.update()
            
            # Be polite - add a small delay between requests
            if i < len(vins):
                time.sleep(1)
        
        # Update recall data
        self.recall_data = new_results
        
        # Save automatically
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.recall_data, f, indent=2)
            log_message(f"\n✓ Results saved to '{self.data_file}'")
        except Exception as e:
            log_message(f"\n✗ Error saving: {str(e)}")
        
        log_message("\nDone!")
        
        # Enable close button and refresh display
        close_btn.config(state=tk.NORMAL)
        self.populate_vin_list()
        
        self.is_checking = False
    
    def save_data(self):
        """Save the recall data back to JSON file."""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.recall_data, f, indent=2)
            messagebox.showinfo("Saved", "Changes saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")


def main():
    root = tk.Tk()
    app = RecallTrackerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
