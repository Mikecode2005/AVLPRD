import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import pandas as pd
from datetime import datetime
import os
import re
import csv

# --- CONFIGURATION ---
LOG_FILE = "live_log.csv"  # Use CSV instead of Excel to avoid openpyxl dependency

# --- SIMULATED LOGIC (No OpenCV) ---
def simulate_plate_detection():
    """Simulate plate detection without OpenCV"""
    import random
    import string
    
    # Generate fake plate numbers for demonstration
    states = ["Lagos", "Abuja", "Kano", "Rivers", "Oyo", "Kaduna"]
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    numbers = ''.join(random.choices(string.digits, k=3))
    plate = f"{letters}{numbers}"
    state = random.choice(states)
    
    return plate, state, round(random.uniform(0.7, 0.95), 2)

# --- INITIALIZATION ---
print("1. Starting Live Monitoring (Simulated Mode)...")
print("Note: OpenCV not available, running in simulation mode")

# Create log file if it doesn't exist (CSV format)
headers = ["Time_Stamp", "Model", "Origin_Capital", "Plate_Number", "Confidence"]
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

seen_plates = set()
detection_count = 0

print("2. Simulating live detection... (Press Ctrl+C to stop)")
print("Generating simulated plate detections...")

try:
    while detection_count < 10:  # Simulate 10 detections
        import time
        time.sleep(1)  # Simulate processing time
        
        plate, state, confidence = simulate_plate_detection()
        
        if plate not in seen_plates:
            seen_plates.add(plate)
            detection_count += 1
            
            # Log the detection (append to CSV)
            with open(LOG_FILE, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Simulated Detection",
                    state,
                    plate,
                    confidence
                ])
            
            print(f"   -> Detected: {plate} ({state}) - Confidence: {confidence}")
            
except KeyboardInterrupt:
    print("\n3. Live monitoring stopped by user")

print(f"\n4. Simulation completed! {detection_count} plates detected.")
print(f"Log saved to: {LOG_FILE}")
