import subprocess
import os

def setup_task():
    task_name = "SitebuilderMonitorTask"
    # 获取当前脚本所在目录的绝对路径，并定位到 .bat 文件
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bat_path = os.path.join(current_dir, "run_monitor.bat")
    
    # Delete task if it exists
    subprocess.run(["schtasks", "/delete", "/tn", task_name, "/f"], capture_output=True)
    
    # Create task: Hourly, every 4 hours
    # /sc hourly /mo 4 means every 4 hours
    cmd = [
        "schtasks", "/create", 
        "/tn", task_name, 
        "/tr", f'"{bat_path}"', 
        "/sc", "hourly", 
        "/mo", "4",
        "/f"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Successfully created scheduled task: {task_name}")
        print("The monitor will run every 4 hours.")
    else:
        print(f"Failed to create scheduled task. Error: {result.stderr}")

if __name__ == "__main__":
    setup_task()
