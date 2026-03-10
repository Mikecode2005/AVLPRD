import streamlit as st
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch.utils.data.dataloader")

# Handle OpenCV import gracefully for Streamlit deployment
try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    st.warning("OpenCV not available. Some features may be limited.")

import os
import sys
import subprocess
import pandas as pd
import time
import shutil
from datetime import datetime
import glob

# --- STREAMLIT CONFIGURATION ---
st.set_page_config(
    page_title="ALPR & Data Logging System",
    page_icon="📹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS STYLING ---
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
    }
    .success-text {
        color: #10B981;
        font-weight: bold;
    }
    .error-text {
        color: #EF4444;
        font-weight: bold;
    }
    .info-text {
        color: #3B82F6;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. CORE LOGIC FUNCTIONS ---
def run_script(script_name, args=None):
    """Runs a python script and returns the result"""
    try:
        cmd = [sys.executable, script_name]
        if args:
            cmd.extend(args)
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return proc.returncode == 0, proc.stdout, proc.stderr
    except Exception as e:
        return False, "", str(e)

def update_aggregated_analytics():
    log_files = ["batch_results_log.xlsx", "live_log.xlsx", "video_results_log.xlsx"]
    all_data = []
    total_vehicles = 0
    top_state = "No Data"

    for file in log_files:
        if os.path.exists(file):
            try:
                df = pd.read_excel(file)
                all_data.append(df)
            except Exception as e:
                st.warning(f"Error reading {file}: {e}")

    if all_data:
        master_df = pd.concat(all_data, ignore_index=True)
        
        if not master_df.empty:
            total_vehicles = master_df['Plate_Number'].nunique()
            
            # Filter out 'Unknown' to find the real TOP CITY/CAPITAL
            valid_states = master_df[master_df['Origin_Capital'] != 'Unknown']
            
            if not valid_states.empty:
                top_state = valid_states['Origin_Capital'].value_counts().idxmax()
            else:
                top_state = "Unknown"
    
    return total_vehicles, top_state

def archive_and_clear_logs():
    """Archive all logs and start fresh"""
    archive_dir = "Archived_Logs"
    if not os.path.exists(archive_dir): 
        os.makedirs(archive_dir)
    
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
    
    st.success("All logs archived successfully!")

def display_log_data():
    """Display log data in a table format"""
    log_files = ["batch_results_log.xlsx", "live_log.xlsx", "video_results_log.xlsx"]
    all_data = []

    for file in log_files:
        if os.path.exists(file):
            try:
                df = pd.read_excel(file)
                df['Source'] = file
                all_data.append(df)
            except Exception as e:
                st.warning(f"Error reading {file}: {e}")

    if all_data:
        master_df = pd.concat(all_data, ignore_index=True)
        if not master_df.empty:
            st.dataframe(master_df, use_container_width=True)
        else:
            st.info("No log data available yet.")
    else:
        st.info("No log files found.")

# --- 2. STREAMLIT UI ---
def main():
    st.markdown('<h1 class="main-header">📹 ALPR & Data Logging System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-Time Detection & Intelligent Data Archiving</p>', unsafe_allow_html=True)
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page:", 
                               ["Dashboard", "Batch Processing", "Live Monitoring", 
                                "Video Analysis", "Reports", "Settings"])
    
    # Analytics Dashboard
    if page == "Dashboard":
        st.header("📊 System Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            total_vehicles, top_state = update_aggregated_analytics()
            st.metric("Total Unique Vehicles", total_vehicles)
        
        with col2:
            st.metric("Top City/Capital", top_state)
        
        st.divider()
        
        st.subheader("Recent Activity")
        display_log_data()
    
    # Batch Processing
    elif page == "Batch Processing":
        st.header("📂 Process Image Dataset")
        
        uploaded_files = st.file_uploader("Upload images", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
        
        if uploaded_files:
            if st.button("Process Images"):
                with st.spinner("Processing images..."):
                    # Save uploaded files temporarily
                    temp_dir = "temp_upload"
                    if not os.path.exists(temp_dir):
                        os.makedirs(temp_dir)
                    
                    for uploaded_file in uploaded_files:
                        with open(os.path.join(temp_dir, uploaded_file.name), "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    
                    success, stdout, stderr = run_script("batch_test.py", [temp_dir])
                    
                    if success:
                        st.success("✅ Dataset processed successfully!")
                        if os.path.exists("batch_results_log.xlsx"):
                            st.download_button(
                                label="Download Results",
                                data=open("batch_results_log.xlsx", "rb").read(),
                                file_name="batch_results_log.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    else:
                        st.error(f"❌ Processing failed: {stderr}")
        
        st.info("Upload multiple images to process them in batch.")
    
    # Live Monitoring
    elif page == "Live Monitoring":
        st.header("📹 Live Camera Monitoring")
        
        st.info("This feature requires a camera connection. Click start to begin monitoring.")
        
        if st.button("Start Live Monitoring"):
            with st.spinner("Starting live monitoring..."):
                # Use fallback script if OpenCV is not available
                if OPENCV_AVAILABLE:
                    script_to_run = "live_feed.py"
                    st.info("Using real OpenCV-based detection")
                else:
                    script_to_run = "live_feed_no_cv2.py"
                    st.info("OpenCV not available, using simulated detection")
                
                success, stdout, stderr = run_script(script_to_run)
                
                if success:
                    st.success("✅ Live monitoring session completed!")
                    if os.path.exists("live_log.xlsx"):
                        st.download_button(
                            label="Download Live Log",
                            data=open("live_log.xlsx", "rb").read(),
                            file_name="live_log.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.error(f"❌ Live monitoring failed: {stderr}")
    
    # Video Analysis
    elif page == "Video Analysis":
        st.header("📺 Analyze Video Stream")
        
        uploaded_video = st.file_uploader("Upload video file", type=['mp4', 'avi', 'mkv', 'mov'])
        
        if uploaded_video:
            if st.button("Analyze Video"):
                with st.spinner("Analyzing video..."):
                    # Save uploaded video temporarily
                    temp_video = "temp_video.mp4"
                    with open(temp_video, "wb") as f:
                        f.write(uploaded_video.getbuffer())
                    
                    success, stdout, stderr = run_script("video_test.py", [temp_video])
                    
                    if success:
                        st.success("✅ Video analysis completed!")
                        if os.path.exists("video_results_log.xlsx"):
                            st.download_button(
                                label="Download Video Results",
                                data=open("video_results_log.xlsx", "rb").read(),
                                file_name="video_results_log.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                    else:
                        st.error(f"❌ Video analysis failed: {stderr}")
    
    # Reports
    elif page == "Reports":
        st.header("📄 Generate Reports")
        
        if st.button("Generate PDF Report"):
            with st.spinner("Generating report..."):
                success, stdout, stderr = run_script("generate_report.py")
                
                if success:
                    st.success("✅ Report generated successfully!")
                    if os.path.exists("ALPR & Data Logging.pdf"):
                        with open("ALPR & Data Logging.pdf", "rb") as f:
                            st.download_button(
                                label="Download PDF Report",
                                data=f.read(),
                                file_name="ALPR_Data_Logging_Report.pdf",
                                mime="application/pdf"
                            )
                else:
                    st.error(f"❌ Report generation failed: {stderr}")
        
        st.subheader("Available Log Files")
        log_files = ["batch_results_log.xlsx", "live_log.xlsx", "video_results_log.xlsx"]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                with open(log_file, "rb") as f:
                    st.download_button(
                        label=f"Download {log_file}",
                        data=f.read(),
                        file_name=log_file,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.info(f"{log_file} not found")
    
    # Settings
    elif page == "Settings":
        st.header("⚙️ Settings")
        
        st.subheader("Data Management")
        
        if st.button("🧹 Archive All Logs"):
            archive_and_clear_logs()
        
        st.subheader("System Information")
        st.write(f"**Python Version:** {sys.version}")
        st.write(f"**Working Directory:** {os.getcwd()}")
        
        # Check dependencies
        st.subheader("Dependencies Status")
        dependencies = ['cv2', 'pandas', 'numpy', 'torch', 'ultralytics', 'easyocr']
        
        for dep in dependencies:
            try:
                __import__(dep)
                st.success(f"✅ {dep}")
            except ImportError:
                st.error(f"❌ {dep}")

if __name__ == "__main__":
    main()