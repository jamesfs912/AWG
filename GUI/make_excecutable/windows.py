import subprocess
import sys
import os

def install_pyinstaller():
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])

def check_pyinstaller_installed():
    try:
        subprocess.run(['pyinstaller', '--version'], capture_output=True)
        return True
    except FileNotFoundError:
        return False

if __name__ == "__main__":
    os.chdir('..')
    print(os.getcwd())

    if not check_pyinstaller_installed():
        print("PyInstaller not found. Installing...")
        install_pyinstaller()

    cmd = ['pyinstaller']

    onefile=True
    if onefile:
        cmd.append('--onefile')
    else:
        cmd.extend(['-y'])

    cmd.extend(['--hide-console', "hide-late"])

    # Add hidden imports to the command
    hidden_imports = []
    for hidden_import in hidden_imports:
        cmd.extend(['--hidden-import', hidden_import])
        
    cmd.extend(['--distpath', "bin/windows"])
    cmd.extend(['--workpath', "bin/build_garbage"])
    #cmd.extend(['--specpath', "bin/build_garbage"])
    #cmd.extend(['--strip'])
    cmd.extend(['--icon', "icon.ico"])
    cmd.extend(['--name', "AWG"])
    cmd.extend(['--add-data', "icon.ico:."])

    cmd.append("main.py")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode == 0:
        print("Packaging successful!")
    else:
        print("Packaging failed!")
        
    os.remove("AWG.spec")
