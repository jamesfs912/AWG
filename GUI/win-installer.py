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

def package_with_pyinstaller(script_name, onefile=True, hidden_imports=[]):
    cmd = ['pyinstaller']

    if onefile:
        cmd.append('--onefile')
    cmd.append('--noconsole')

    # Add hidden imports to the command
    for hidden_import in hidden_imports:
        cmd.extend(['--hidden-import', hidden_import])

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

    # Add hidden imports here
    hidden_imports_list = ['numpy', 'pyserial', 'PyQt6', 'pyqtgraph']

    return_code = package_with_pyinstaller('main.py', onefile=True, hidden_imports=hidden_imports_list)

    if return_code == 0:
        print("Packaging successful!")
    else:
        print("Packaging failed!")
