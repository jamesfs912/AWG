import subprocess
import sys

def check_and_install_pyinstaller():
    try:
        subprocess.check_output(['pyinstaller', '--version'])
    except FileNotFoundError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])

def package_with_pyinstaller(script_name, onefile=True):
    cmd = ['pyinstaller']

    if onefile:
        cmd.append('--onefile')

    cmd.append(script_name)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode

if __name__ == "__main__":
    check_and_install_pyinstaller()
    
    return_code = package_with_pyinstaller(
        'main.py',  
        onefile=True,
    )

    if return_code == 0:
        print("Packaging successful!")
    else:
        print("Packaging failed!")
