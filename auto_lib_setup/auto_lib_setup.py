import os
import importlib
import subprocess
import sys
import time
import threading
import IPython

RED, GREEN, YELLOW, BLUE, PURPLE = "\033[31m", "\033[32m", "\033[33m", "\033[34m", "\033[35m"
COLOR_CLS = "\033[0m"


def auto_lib_setup(dependency_requirements: dict, log_output_dir='/content/'):
    LOG_PATH = os.path.join(log_output_dir, 'setup_log.txt')
    RESET_FLAG = False
    LOGS = []

    def update_log(log):
        LOGS.append(log)
        print(log)
        with open(LOG_PATH, 'a') as f:
            f.write(log + '\n')

    def restart_colab_runtime():
        update_log("🔄 Restarting runtime...")
        time.sleep(2)  

        display(IPython.display.Javascript('''
            function reconnect() {
                console.log("🔄 Auto-reconnecting...");
                document.querySelector("colab-toolbar-button.reconnect-button").click();
            }
            setTimeout(reconnect, 3000);
        '''))
        update_log(f'🔄 Auto-reconnecting... {YELLOW}[{COLOR_CLS}Once reconnected, rerun this cell to continue.{YELLOW}]{COLOR_CLS}')
        time.sleep(0.5)
        os.kill(os.getpid(), 9)  

    def loading_wheel(stop_event):
        spinner = ['-', '\\', '|', '/']
        idx = 0
        while not stop_event.is_set():
            print(f"\r⏳ {BLUE}NongMind{COLOR_CLS} is helping you install... {spinner[idx]} ", end='', flush=True)
            idx = (idx + 1) % len(spinner)
            time.sleep(0.1)
        print()

    if not os.path.exists(LOG_PATH):
        update_log('~' * 80)
        update_log(' ' * 14 + f'{BLUE}⋆.ೃ࿔*:･🪼 NongMind\'s Auto Dependencies Setup ･:*࿔ೃ.⋆ {COLOR_CLS}')
        update_log('~' * 80)

    for module, required_version in dependency_requirements.items():
        try:
            imported_module = importlib.import_module(module)
            installed_version = getattr(imported_module, '__version__', None)

            if not installed_version:
                update_log(f"🚀 {PURPLE}{module}{COLOR_CLS} is installed but version is missing. Reinstalling...")

                stop_spinner = threading.Event()
                spinner_thread = threading.Thread(target=loading_wheel, args=(stop_spinner,))
                spinner_thread.start()

                subprocess.run([sys.executable, "-m", "pip", "install", module], check=True)

                stop_spinner.set()
                spinner_thread.join()

                RESET_FLAG = True
                continue  

            if required_version and installed_version != required_version:
                update_log(f"🚀 {PURPLE}{module}{COLOR_CLS} is updating : {RED}{installed_version}{COLOR_CLS} → {GREEN}{required_version}{COLOR_CLS}")

                stop_spinner = threading.Event()
                spinner_thread = threading.Thread(target=loading_wheel, args=(stop_spinner,))
                spinner_thread.start()

                subprocess.run([sys.executable, "-m", "pip", "install", f"{module}=={required_version}"], check=True)

                stop_spinner.set()
                spinner_thread.join()

                RESET_FLAG = True

        except (ImportError, ModuleNotFoundError):
            if required_version:
                update_log(f"🚚 {PURPLE}{module}{COLOR_CLS} not found. Installing {module}=={required_version}...")
                install_command = [sys.executable, "-m", "pip", "install", f"{module}=={required_version}"]
            else:
                update_log(f"🚚 {PURPLE}{module}{COLOR_CLS} not found. Installing the latest version...")
                install_command = [sys.executable, "-m", "pip", "install", module]

            stop_spinner = threading.Event()
            spinner_thread = threading.Thread(target=loading_wheel, args=(stop_spinner,))
            spinner_thread.start()

            try:
                subprocess.run(install_command, check=True)
                stop_spinner.set()
                spinner_thread.join()
                RESET_FLAG = True
            except subprocess.CalledProcessError:
                stop_spinner.set()
                spinner_thread.join()
                update_log(f"❌ Failed to install {RED}{module}{COLOR_CLS}. Please check manually.")

    if RESET_FLAG:
        time.sleep(0.5)
        restart_colab_runtime()
    else:
        if os.path.exists(LOG_PATH):
            with open(LOG_PATH, 'r') as f:
                print(f.read())
            print('~' * 80)

        print(f'✅ All dependencies match the required versions.')
        for module, required_version in dependency_requirements.items():
            current_version = required_version
            if not required_version:
                imported_module = importlib.import_module(module)
                current_version = getattr(imported_module, '__version__', None)
                current_version = f'{current_version} (latest)'

            print(f'- {PURPLE}{module}{COLOR_CLS} : {GREEN}{current_version}{COLOR_CLS}')


if __name__ == "__main__":
    # Example usage 
    requirements = {
        'autogluon.tabular': None,
        'numpy': '1.23.5',
    }
    auto_lib_setup(requirements)
