import subprocess
import sys
import platform  # Add this import to detect the OS

def check_and_install_pyinstaller():
    try:
        subprocess.check_output(['pyinstaller', '--version'])
    except FileNotFoundError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])

def package_with_pyinstaller(script_name, onefile=True, hidden_imports=[]):
    cmd = ['pyinstaller']

    if onefile:
        cmd.append('--onefile')

    # Automatically use --windowed when packaging for macOS
    if platform.system() == "Darwin":
        cmd.append('--windowed')

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
    check_and_install_pyinstaller()

    hidden_imports_list = ['numpy', 'pyserial', 'PyQt6', 'pyqtgraph']

    return_code = package_with_pyinstaller(
        'main.py',  
        onefile=True,
        hidden_imports=hidden_imports_list
    )

    if return_code == 0:
        print("Packaging successful!")
    else:
        print("Packaging failed!")
