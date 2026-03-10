import warnings
warnings.filterwarnings("ignore", category=UserWarning)
import pandas as pd
from datetime import datetime
import os
import re

# --- CONFIGURATION ---
LOG_FILE = "live_log.xlsx"

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

# Create log file if it doesn't exist
headers = ["Time_Stamp", "Model", "Origin_Capital", "Plate_Number", "Confidence"]
if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=headers).to_excel(LOG_FILE, index=False)

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
            
            # Log the detection
            new_log = pd.DataFrame([{
                "Time_Stamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Model": "Simulated Detection",
                "Origin_Capital": state,
                "Plate_Number": plate,
                "Confidence": confidence
            }])
            
            with pd.ExcelWriter(LOG_FILE, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
                new_log.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)
            
            print(f"   -> Detected: {plate} ({state}) - Confidence: {confidence}")
            
except KeyboardInterrupt:
    print("\n3. Live monitoring stopped by user")

print(f"\n4. Simulation completed! {detection_count} plates detected.")
print(f"Log saved to: {LOG_FILE}")