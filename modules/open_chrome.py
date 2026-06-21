'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html
            
GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Support me: https://github.com/sponsors/GodsScion

version:    26.01.20.5.08
'''

from modules.helpers import get_default_temp_profile, make_directories
from config.settings import run_in_background, stealth_mode, disable_extensions, safe_mode, file_name, failed_file_name, logs_folder_path, generated_resume_path
from config.questions import default_resume_path
if stealth_mode:
    import undetected_chromedriver as uc
else: 
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    # from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from modules.helpers import find_default_profile_directory, critical_error_log, print_lg
from selenium.common.exceptions import SessionNotCreatedException
import re
import os
import sys
from pathlib import Path

def get_chrome_major_version(chrome_path: str | None = None) -> int | None:
    if not chrome_path:
        from modules.chrome_detect import find_chrome
        chrome_path = find_chrome()
    if not chrome_path:
        return None

    # 1. Try reading macOS Info.plist (fast, no process execution)
    if sys.platform == "darwin" and "Google Chrome.app" in chrome_path:
        try:
            import plistlib
            p = Path(chrome_path)
            # Find Contents/Info.plist
            plist_path = p.parents[1] / "Info.plist"
            if plist_path.is_file():
                with open(plist_path, "rb") as fp:
                    plist = plistlib.load(fp)
                    version = plist.get("CFBundleShortVersionString")
                    if version:
                        major = version.split(".")[0]
                        return int(major)
        except Exception:
            pass

    # 2. Try directory search for Windows
    if sys.platform.startswith("win"):
        try:
            chrome_dir = Path(chrome_path).parent
            version_pattern = re.compile(r'^\d+(\.\d+){3}$')
            if chrome_dir.is_dir():
                for sub in chrome_dir.iterdir():
                    if sub.is_dir() and version_pattern.match(sub.name):
                        major = sub.name.split('.')[0]
                        return int(major)
        except Exception:
            pass

    # 3. Fallback: Run the binary with --version
    try:
        import subprocess
        res = subprocess.run([chrome_path, "--version"], capture_output=True, text=True, timeout=3)
        m = re.search(r'\d+', res.stdout)
        if m:
            return int(m.group(0))
    except Exception:
        pass

    return None

def createChromeSession(isRetry: bool = False):
    make_directories([file_name,failed_file_name,logs_folder_path+"/screenshots",default_resume_path,generated_resume_path+"/temp"])
    # Set up WebDriver with Chrome Profile
    options = uc.ChromeOptions() if stealth_mode else Options()
    if run_in_background:   options.add_argument("--headless")
    if disable_extensions:  options.add_argument("--disable-extensions")

    print_lg("IF YOU HAVE MORE THAN 10 TABS OPENED, PLEASE CLOSE OR BOOKMARK THEM! Or it's highly likely that application will just open browser and not do anything!")
    profile_dir = find_default_profile_directory()
    if isRetry:
        print_lg("Will login with a guest profile, browsing history will not be saved in the browser!")
    elif profile_dir and not safe_mode:
        options.add_argument(f"--user-data-dir={profile_dir}")
    else:
        print_lg("Logging in with a guest profile, Web history will not be saved!")
        options.add_argument(f"--user-data-dir={get_default_temp_profile()}")

    from modules.chrome_detect import find_chrome
    chrome_path = find_chrome()
    if chrome_path:
        print_lg(f"Using Google Chrome binary at: {chrome_path}")
        options.binary_location = chrome_path

    if stealth_mode:
        print_lg("Downloading Chrome Driver... This may take some time. Undetected mode requires download every run!")
        major_version = get_chrome_major_version(chrome_path)
        
        kwargs = {"options": options}
        if chrome_path:
            kwargs["browser_executable_path"] = chrome_path
        if major_version:
            print_lg(f"Detected Chrome major version: {major_version}. Passing version_main={major_version} to undetected_chromedriver.")
            kwargs["version_main"] = major_version
        
        driver = uc.Chrome(**kwargs)
    else:
        driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    wait = WebDriverWait(driver, 5)
    actions = ActionChains(driver)
    return options, driver, actions, wait

try:
    options, driver, actions, wait = None, None, None, None
    options, driver, actions, wait = createChromeSession()
except SessionNotCreatedException as e:
    critical_error_log("Failed to create Chrome Session, retrying with guest profile", e)
    options, driver, actions, wait = createChromeSession(True)
except Exception as e:
    msg = 'Seems like Google Chrome is out dated. Update browser and try again! \n\n\nIf issue persists, try Safe Mode. Set, safe_mode = True in config.py \n\nPlease check GitHub discussions/support for solutions https://github.com/GodsScion/Auto_job_applier_linkedIn \n                                   OR \nReach out in discord ( https://discord.gg/fFp7uUzWCY )'
    if isinstance(e,TimeoutError): msg = "Couldn't download Chrome-driver. Set stealth_mode = False in config!"
    print_lg(msg)
    critical_error_log("In Opening Chrome", e)
    from pyautogui import alert
    alert(msg, "Error in opening chrome")
    try: driver.quit()
    except NameError: exit()
    
