import os
import sys

# Streamlit run karne ka alternative method
def run_streamlit():
    try:
        # Python ke scripts folder mein streamlit.exe dhoondo
        python_path = sys.executable
        scripts_path = python_path.replace("python.exe", "Scripts\\streamlit.exe")
        
        if os.path.exists(scripts_path):
            os.system(f'"{scripts_path}" run app.py')
        else:
            print("Streamlit not found. Installing...")
            os.system("pip install streamlit")
            os.system(f'"{scripts_path}" run app.py')
            
    except Exception as e:
        print(f"Error: {e}")
        print("Please install streamlit manually: pip install streamlit")

if __name__ == "__main__":
    run_streamlit()