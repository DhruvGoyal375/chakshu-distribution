import os
import subprocess
import sys
import shutil
from pathlib import Path
import textwrap


def clean_previous_builds():
    """Clean up previous build artifacts"""
    for path in ['dist', 'build']:
        if os.path.exists(path):
            shutil.rmtree(path)
    for file in Path('.').glob('*.spec'):
        file.unlink()


def create_runtime_hook():
    """Create runtime hook for multiprocessing and scipy/sklearn support"""
    content = textwrap.dedent("""
        import os
        import sys
        import multiprocessing

        # Fix multiprocessing on Windows
        if sys.platform.startswith('win'):
            try:
                multiprocessing.set_start_method('spawn')
            except RuntimeError:
                pass

        try:
            import scipy.stats._stats_py
        except ImportError:
            pass

        # Fix scipy stats module
        def _fix_scipy_stats():
            try:
                from scipy.stats import _stats_py
                _stats_py.obj = object
            except ImportError:
                pass

        _fix_scipy_stats()
    """)
    with open('runtime_hook.py', 'w') as f:
        f.write(content)
    return os.path.abspath('runtime_hook.py')


def build_app():
    try:
        # Clean previous builds
        clean_previous_builds()

        # Create runtime hook
        runtime_hook = create_runtime_hook()

        # Get paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        web_dir = os.path.join(base_dir, "web")
        venv_path = os.path.dirname(sys.executable)
        models_path = r".venv\Lib\site-packages\openwakeword\resources\models"

        # Platform-specific separator
        separator = ';' if sys.platform.startswith('win') else ':'

        # PyInstaller command
        cmd = [
            sys.executable,
            '-m', 'PyInstaller',
            '--name=ChakshuAssistant',
            '--onefile',
            f'--add-data={web_dir}{separator}web',
            f'--add-data={models_path}{separator}openwakeword/resources/models',
            '--hidden-import=scipy._lib.messagestream',
            '--hidden-import=pyttsx3.drivers',
            '--hidden-import=scipy.special.cython_special',
            '--hidden-import=scipy.stats._stats_py',
            '--hidden-import=sklearn.utils._cython_blas',
            '--hidden-import=sklearn.neighbors.typedefs',
            '--hidden-import=sklearn.neighbors.quad_tree',
            '--hidden-import=sklearn.tree._utils',
            '--hidden-import=sklearn.utils._weight_vector',
            '--collect-all=openwakeword',
            '--collect-all=sklearn',
            '--collect-all=scipy',
            '--collect-all=numpy',
            f'--runtime-hook={runtime_hook}',
            '--clean',
            'app.py'
        ]

        # Run PyInstaller
        subprocess.run(cmd, check=True)

    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise
    finally:
        # Cleanup
        if os.path.exists('runtime_hook.py'):
            os.remove('runtime_hook.py')


if __name__ == '__main__':
    build_app()
