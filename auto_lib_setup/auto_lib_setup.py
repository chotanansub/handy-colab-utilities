import os
import importlib
import subprocess
import sys
import time


RED,GREEN,YELLOW,BLUE,PURPLE = "\033[31m","\033[32m","\033[33m","\033[34m","\033[35m"
COLOR_CLS = "\033[0m"

def colab_dependencies_setup(dependency_requirements : dict, log_output_dir= '/content/'):
  LOG_PATH = os.path.join(log_output_dir, 'setup_log.txt')
  RESET_FLAG = False
  LOGS = []
  def update_log(log):
    LOGS.append(log)
    print(log)
    with open(LOG_PATH, 'a') as f:
      f.write(log + '\n')

  for module, required_version in dependency_requirements.items():
      try:
          imported_module = importlib.import_module(module)
          installed_version = getattr(imported_module, '__version__', None)

          if not installed_version:
              update_log(f"🚀 {PURPLE}{module}{COLOR_CLS} is installed but version is missing. Reinstalling...")
              subprocess.run([sys.executable, "-m", "pip", "install", module], check=True)
              RESET_FLAG = True
              continue 

          if required_version and installed_version != required_version:
              update_log(f"🚀 {PURPLE}{module}{COLOR_CLS} is updating : {installed_version} → {GREEN}{required_version}{COLOR_CLS}")
              subprocess.run([sys.executable, "-m", "pip", "install", f"{module}=={required_version}"], check=True)
              RESET_FLAG = True

      except (ImportError, ModuleNotFoundError):
          if required_version:
              update_log(f"🚚 {PURPLE}{module}{COLOR_CLS} not found. Installing {module}=={required_version}...")
              install_command = [sys.executable, "-m", "pip", "install", f"{module}=={required_version}"]
          else:
              update_log(f"🚚 {PURPLE}{module}{COLOR_CLS} not found. Installing the latest version...")
              install_command = [sys.executable, "-m", "pip", "install", module]

          try:
              subprocess.run(install_command, check=True)
              RESET_FLAG = True
          except subprocess.CalledProcessError:
              update_log(f"❌ Failed to install {RED}{module}{COLOR_CLS}. Please check manually.")

  if RESET_FLAG:
    update_log(f'🔄 Restarting to apply changes {YELLOW}[Please rerun this cell!]{COLOR_CLS}')
    time.sleep(0.5)
    os.kill(os.getpid(), 9)
  else:
    if os.path.exists(LOG_PATH):
      with open(LOG_PATH, 'r') as f:
        print(f.read())
      print('='*50)
    print(f'✅ {GREEN} All dependencies match the required versions. {COLOR_CLS}')

if __name__ == "__main__":
    # Example usage 
    requirements = {
        'autogluon.tabular': None,
        'scikit-learn': '1.4.1',
    }
    colab_dependencies_setup(requirements)