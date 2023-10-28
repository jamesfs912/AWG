import subprocess
import sys

def install_pyinstaller():
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

def check_pyinstaller_installed():
    try:
        subprocess.run(['pyinstaller', '--version'], capture_output=True)
        return True
    except FileNotFoundError:
        return False

def package_with_pyinstaller(script_name, onefile=True):
    cmd = ['pyinstaller']

    if onefile:
        cmd.append('--onefile')
    cmd.append('--noconsole') 


    cmd.append(script_name)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode

if __name__ == "__main__":
    if not check_pyinstaller_installed():
        print("PyInstaller not found. Installing...")
        install_pyinstaller()

    return_code = package_with_pyinstaller('main.py', onefile=True)

    if return_code == 0:
        print("Packaging successful!")
    else:
        print("Packaging failed!")
