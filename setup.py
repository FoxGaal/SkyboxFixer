import os
import subprocess
import re
import ctypes
import sys
import ctypes, sys
import time

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
HWND_BROADCAST = 0xFFFF
WM_SETTINGCHANGE = 0x001A

def find_latest_blender(blender_base_path):
    # List all directories inside the base Blender folder
    all_versions = [d for d in os.listdir(blender_base_path) if os.path.isdir(os.path.join(blender_base_path, d))]
    
    # Use regex to find valid Blender version folders (e.g., Blender 3.3, Blender 3.4)
    version_pattern = re.compile(r"Blender\s*(\d+\.\d+)")
    valid_versions = []
    
    for version in all_versions:
        match = version_pattern.search(version)
        if match:
            valid_versions.append((match.group(0), version))
    
    if valid_versions:
        # Sort versions and return the latest one
        valid_versions.sort(key=lambda x: x[0], reverse=True)
        latest_version_folder = valid_versions[0][1]
        latest_version_path = os.path.join(blender_base_path, latest_version_folder)
        return latest_version_path
    else:
        return None

def get_system_path():
    # Use REG command to query the system PATH environment variable (Windows)
    result = subprocess.run(r'reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH',
                            capture_output=True, text=True, shell=True)
    if result.returncode == 0:
        # Extract PATH value from the command output
        output = result.stdout
        path_line = output.split('    ')[-1].strip()  # The PATH is the last element in the output
        return path_line
    else:
        print("Failed to query system PATH.")
        return None

def add_blender_to_system_path(blender_path):
    system_path = get_system_path()
    
    if system_path:
        # Check if Blender path is already in the system PATH
        if blender_path not in system_path:
            # Append Blender path to the system PATH
            new_system_path = blender_path + os.pathsep + system_path
            
            try:
                # Use the REG command to update the system PATH
                result = subprocess.run(
                    f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment" /v PATH /d "{new_system_path}" /f',
                    capture_output=True, text=True, shell=True
                )
                
                # Check if there's an "Access is denied" error
                if result.returncode != 0 and "Access is denied" in result.stderr:
                    print("Error: Access is denied. Please run this script with administrative privileges.")
                else:
                    print("Blender has been added to the system PATH.")
                    
                    # Broadcast the setting change to update environment variables without a restart
                    refresh_environment_variables()

            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("Blender path is already in the system PATH.")
    else:
        print("Could not retrieve the system PATH.")

def refresh_environment_variables():
    """
    Broadcasts the WM_SETTINGCHANGE message to update environment variables
    across all running applications.
    """
    result = ctypes.windll.user32.SendMessageTimeoutW(
        HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment", 0x0002, 5000, ctypes.byref(ctypes.c_ulong())
    )
    if result == 0:
        print("Failed to broadcast environment variable update.")
    else:
        print("Environment variables updated. You can now use the Blender command in new terminals.")



if is_admin():
    result = subprocess.run('pip install flask',
                                capture_output=True, text=True, shell=True)
    if result.returncode == 0:
        print("Flask is now installed")
    else :
        print("Something went wrong while trying to install flask")

    result = subprocess.run('pip install pillow',
                                capture_output=True, text=True, shell=True)
    if result.returncode == 0:
        print("Pillow is now installed")
    else :
        print("Something went wrong while trying to install pillow")

    blender_base_path = r"C:\Program Files\Blender Foundation"  # Base path where Blender versions are installed
    latest_blender_path = find_latest_blender(blender_base_path)

    if latest_blender_path:
        add_blender_to_system_path(latest_blender_path)
        
    else:
        print("No valid Blender versions found. Please Install blender through blender.org NOT microsoft store")
    print("Setup has finished")
    time.sleep(5)  
else:
    # Re-run the program with admin rights
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
