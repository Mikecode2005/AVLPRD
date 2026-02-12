import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch.utils.data.dataloader")
import cv2
import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import threading
import sys
import subprocess
import pandas as pd
import time
import shutil
from datetime import datetime

# --- CONFIGURATION ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# --- 1. CORE LOGIC FUNCTIONS ---
def run_script(script_name):
    """Runs a python script in a separate thread so GUI doesn't freeze"""
    def task():
        status_label.configure(text=f"⏳ Running...", text_color="#F9AA33")
        toggle_buttons("disabled")
        try:
            proc = subprocess.run([sys.executable, script_name], check=False)
            exit_code = proc.returncode
        except Exception as e:
            exit_code = 1
        
        if exit_code == 0:
            status_label.configure(text="✅ Completed!", text_color="#2CC985")
            time.sleep(1)
            # Auto-open logic
            if "batch_test" in script_name: open_file("batch_results_log.xlsx")
            elif "generate_report" in script_name: open_file("ALPR & Data Logging.pdf")
            elif "live_feed" in script_name: open_file("live_log.xlsx")
            messagebox.showinfo("Success", "Operation completed successfully.")
        else:
            status_label.configure(text="❌ Error Occurred", text_color="#FF4C4C")
        toggle_buttons("normal")
    threading.Thread(target=task).start()

def open_file(path):
    if not os.path.exists(path): return
    if hasattr(os, "startfile"): os.startfile(path)
    elif sys.platform == "darwin": subprocess.run(["open", path])
    else: subprocess.run(["xdg-open", path])

# --- LIVE MONITORING MODULE ---
def run_live_monitoring():
    """Launches live feed and resets UI automatically when the camera is closed."""
    def task():
        status_label.configure(text="📹 Activating Live Camera...", text_color="#F9AA33")
        toggle_buttons("disabled")
        
        try:
            proc = subprocess.run([sys.executable, "live_feed.py"], check=False)
            exit_code = proc.returncode
        except Exception as e:
            exit_code = 1
        
        if exit_code == 0:
            status_label.configure(text="✅ Monitoring Session Ended!", text_color="#2CC985")
            time.sleep(1)
            open_file("live_log.xlsx") 
        else:
            status_label.configure(text="❌ Camera Error", text_color="#FF4C4C")

        time.sleep(2)
        toggle_buttons("normal")
        status_label.configure(text="System Ready!", text_color="#AAAAAA")

    threading.Thread(target=task).start()

def update_aggregated_analytics(total_label, state_label):
    log_files = ["batch_results_log.xlsx", "live_log.xlsx", "video_results_log.xlsx"]
    all_data = []

    for file in log_files:
        if os.path.exists(file):
            try:
                df = pd.read_excel(file)
                all_data.append(df)
            except Exception as e:
                print(f"Error reading {file}: {e}")

    if all_data:
        master_df = pd.concat(all_data, ignore_index=True)
        
        if not master_df.empty:
            total_unique = master_df['Plate_Number'].nunique()
            total_label.configure(text=str(total_unique))
            
            # Filter out 'Unknown' to find the real TOP CITY/CAPITAL
            valid_states = master_df[master_df['Origin_Capital'] != 'Unknown']
            
            if not valid_states.empty:
                top_state = valid_states['Origin_Capital'].value_counts().idxmax()
                state_label.configure(text=str(top_state))
            else:
                state_label.configure(text="Unknown")
    else:
        total_label.configure(text="0")
        state_label.configure(text="No Logs Found")

def run_image_dataset_processing():
    selected_dir = filedialog.askdirectory(title="Select Dataset Folder")
    if selected_dir:
        def task():
            status_label.configure(text="📁 Processing Image Dataset...", text_color="#F9AA33")
            toggle_buttons("disabled")
            proc = subprocess.run([sys.executable, "batch_test.py", selected_dir])
            
            if proc.returncode == 0:
                status_label.configure(text="✅ Dataset Processed Successfully!", text_color="#2CC985")
                time.sleep(1)
                open_file("batch_results_log.xlsx")
            else:
                status_label.configure(text="❌ Dataset Failed", text_color="#E74C3C")
            
            time.sleep(2)
            toggle_buttons("normal")
            status_label.configure(text="System Ready!", text_color="#AAAAAA")
        threading.Thread(target=task).start()

def run_export_analysis():
    def task():
        status_label.configure(text="📊 Exporting Analysis Report...", text_color="#E67E22")
        toggle_buttons("disabled")
        proc = subprocess.run([sys.executable, "export_report.py"])
        
        if proc.returncode == 0:
            status_label.configure(text="✅ Report Generated and Saved!", text_color="#2CC985")
        else:
            status_label.configure(text="❌ Export Failed", text_color="#E74C3C")
            
        time.sleep(2)
        toggle_buttons("normal")
        status_label.configure(text="System Ready!", text_color="#AAAAAA")
    threading.Thread(target=task).start()

# --- 2. ADVANCED FEATURE MODULES ---
def browse_and_run_video():
    selected_file = filedialog.askopenfilename(
        title="Select Vehicle Video",
        filetypes=[("Video Files", "*.mp4 *.avi *.mkv *.mov")]
    )
    if selected_file:
        def monitor_video():
            status_label.configure(text="📹 Analyzing Video Stream...", text_color="#F9AA33")
            toggle_buttons("disabled")
            proc = subprocess.run([sys.executable, "video_test.py", selected_file])
            
            status_label.configure(text="✅ Video Analysis Done!", text_color="#2CC985")
            toggle_buttons("normal")
            time.sleep(2)
            status_label.configure(text="System Ready!", text_color="#AAAAAA")
            open_file("video_results_log.xlsx")

        threading.Thread(target=monitor_video).start()

def open_stats_window():
    stats_window = ctk.CTkToplevel(app)
    stats_window.title("System Analytics")
    stats_window.geometry("500x420")
    stats_window.attributes('-topmost', True)

    logs = {"Live": "live_log.xlsx", "Batch": "batch_results_log.xlsx", "Video": "video_results_log.xlsx"}
    total, state_counts = 0, {}

    for log_file in logs.values():
        if os.path.exists(log_file):
            try:
                df = pd.read_excel(log_file)
                total += len(df)
                if 'Origin_Capital' in df.columns:
                    for s, c in df['Origin_Capital'].value_counts().to_dict().items():
                        state_counts[s] = state_counts.get(s, 0) + c
            except: pass

    ctk.CTkLabel(stats_window, text="Traffic Statistics", font=("Arial", 22, "bold")).pack(pady=20)
    top_state = max(state_counts, key=state_counts.get) if state_counts else "None"
    
    for label, val, color in [("TOTAL VEHICLES", total, "#104169"), ("TOP CITY/CAPITAL", top_state, "#0C4D11")]:
        f = ctk.CTkFrame(stats_window, fg_color=color, corner_radius=10)
        f.pack(pady=10, padx=50, fill="x")
        ctk.CTkLabel(f, text=label, font=("Arial", 12)).pack(pady=(10, 0))
        ctk.CTkLabel(f, text=str(val), font=("Arial", 30, "bold")).pack(pady=(0, 10))

def archive_and_clear_logs():
    if not messagebox.askyesno("Confirm Reset", "Archive all logs and start fresh?"): return
    
    archive_dir = "Archived_Logs"
    if not os.path.exists(archive_dir): os.makedirs(archive_dir)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    logs = {
        "live_log.xlsx": ["Time_Stamp", "Model", "Origin_Capital", "Plate_Number", "Confidence"],
        "batch_results_log.xlsx": ["Time_Stamp", "Model", "Origin_Capital", "Plate_Number", "Confidence"],
        "video_results_log.xlsx": ["Timestamp", "Model", "Origin_Capital", "Plate_Number", "Confidence"]
    }

    for f, headers in logs.items():
        if os.path.exists(f):
            shutil.move(f, os.path.join(archive_dir, f"{f.split('.')[0]}_{ts}.xlsx"))
        pd.DataFrame(columns=headers).to_excel(f, index=False)
    
    status_label.configure(text="🧹 Logs Reset!", text_color="#2CC985")
    messagebox.showinfo("Success", "All logs archived successfully.")

def open_about_window():
    about = ctk.CTkToplevel(app)
    about.title("About Project")
    about.geometry("500x270")
    about.attributes('-topmost', True)
    
    ctk.CTkLabel(about, text="STUDENT'S INFORMATION", font=("Arial", 18, "bold")).pack(pady=(20, 10))
    
    line1_text = "Topic: Developing a Solution for Automated Vehicle License Plate"
    line1_label = ctk.CTkLabel(about, text=line1_text, font=("Arial", 15), anchor="w", justify="left")
    line1_label.pack(fill="x", padx=30)

    line2_text = "Recognition (ALPR) & Data Logging\n"
    line2_label = ctk.CTkLabel(about, text=line2_text, font=("Arial", 15), anchor="center", justify="center")
    line2_label.pack(fill="x", pady=(0, 5))

    details = (
         "Developer:         Uwagboi Andrew Chukwuyem\n"
         "Matric No:          2203030127\n"
         "Department:      Computer Science\n"
         "Year:                   2026"
    )
    details_label = ctk.CTkLabel(about, text=details, font=("Arial", 16), justify="left", anchor="w")
    details_label.pack(fill="x", padx=40, pady=5)

# --- 3. GUI SETUP ---
app = ctk.CTk()
app.title("ALPR & Data Logging System")
sw, sh = app.winfo_screenwidth(), app.winfo_screenheight()
app_w = 770
app.geometry(f"{app_w}x{sh}+{sw-app_w}+0")

def toggle_buttons(s):
    for b in [btn_batch, btn_live, btn_video, btn_report, btn_stats, btn_reset]:
        b.configure(state=s)

header_frame = ctk.CTkFrame(app, corner_radius=10, fg_color="#1E1E1E") 
header_frame.pack(pady=20, padx=20, fill="x")
ctk.CTkLabel(header_frame, text="Automated Vehicle License Plate Recognition (ALPR)\n& Data Logging System", font=("Roboto", 22, "bold")).pack(pady=15)

subtitle_label = ctk.CTkLabel(header_frame, text="Real-Time Detection & Intelligent Data Archiving", font=("Segoe UI", 18), text_color="#AAAAAA")
subtitle_label.pack(pady=(15, 25))

status_label = ctk.CTkLabel(app, text="System Ready!", font=("Consolas", 15, "bold"), text_color="#AAAAAA")
status_label.pack()

btn_frame = ctk.CTkFrame(app, corner_radius=20)
btn_frame.pack(pady=10, padx=30, fill="both", expand=True)

params = {"font": ("Arial", 16, "bold"), "height": 48, "corner_radius": 8}

btn_batch = ctk.CTkButton(btn_frame, text="📂   Process Image Dataset", command=run_image_dataset_processing, fg_color="#104169", **params)
btn_batch.pack(pady=(35, 8), padx=100, fill="x")

btn_live = ctk.CTkButton(btn_frame, text="📹 Activate Live Monitoring", command=run_live_monitoring, fg_color="#0C4D11", **params)
btn_live.pack(pady=8, padx=100, fill="x")

btn_video = ctk.CTkButton(btn_frame, text="📺 Analyze Video Stream", command=browse_and_run_video, fg_color="#424242", **params)
btn_video.pack(pady=8, padx=100, fill="x")

btn_stats = ctk.CTkButton(btn_frame, text="📊 System Analytics", command=open_stats_window, fg_color="#2E4053", **params)
btn_stats.pack(pady=8, padx=100, fill="x")

btn_report = ctk.CTkButton(btn_frame, text="📄 Export Analysis Report", command=run_export_analysis, fg_color="#C0392B", **params)
btn_report.pack(pady=8, padx=100, fill="x")

sub_f = ctk.CTkFrame(btn_frame, fg_color="transparent")
sub_f.pack(pady=10)
btn_reset = ctk.CTkButton(sub_f, text="🧹 Reset", width=100, fg_color="#424242", hover_color="#212121", command=archive_and_clear_logs)
btn_reset.pack(side="left", padx=5)
ctk.CTkButton(sub_f, text="ℹ️ About", width=100, command=open_about_window).pack(side="left", padx=5)
ctk.CTkButton(sub_f, text="❌ Exit", width=100, fg_color="#D32F2F", hover_color="#B71C1C", command=app.destroy).pack(side="left", padx=5)

footer = ctk.CTkLabel(app, text="Developed for my Final Year Project (2026)", font=("Arial", 12), text_color="#666666")
footer.pack(side="bottom", pady=20)

app.mainloop()