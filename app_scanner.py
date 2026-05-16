import os
import json

def scan_installed_apps():
    apps = {}
    
    # Common Start Menu locations
    paths = [
        os.path.join(os.environ["ProgramData"], "Microsoft", "Windows", "Start Menu", "Programs"),
        os.path.join(os.environ["AppData"], "Microsoft", "Windows", "Start Menu", "Programs")
    ]
    
    for path in paths:
        if not os.path.exists(path):
            continue
            
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".lnk"):
                    app_name = file.replace(".lnk", "").lower()
                    app_path = os.path.join(root, file)
                    # Use "start" command which handles .lnk files perfectly on Windows
                    apps[app_name] = f'start "" "{app_path}"'
    
    # Add manual overrides/common aliases
    apps.update({
        "chrome": "start chrome",
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "calculator": "calc.exe",
        "notepad": "notepad.exe",
        "paint": "mspaint.exe",
        "cmd": "start cmd",
        "powershell": "start powershell"
    })
    
    return apps

if __name__ == "__main__":
    print("Scanning for installed apps...")
    apps = scan_installed_apps()
    with open("apps.json", "w") as f:
        json.dump(apps, f, indent=4)
    print(f"Found {len(apps)} apps. Saved to apps.json")
