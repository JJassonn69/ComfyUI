import sys
from importlib.abc import MetaPathFinder
from importlib.util import spec_from_file_location, module_from_spec
import os
import site

class MultiPathFinder(MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        # Special handling for comfy.__version__
        if fullname == 'comfy':
            # Try site-packages first
            site_paths = site.getsitepackages()
            for site_path in site_paths:
                comfy_init = os.path.join(site_path, 'comfy', '__init__.py')
                if os.path.exists(comfy_init):
                    return spec_from_file_location(fullname, comfy_init)

        # Handle other comfy.* imports
        if fullname.startswith('comfy.'):
            parts = fullname.split('.')
            # Try site-packages first for API components
            if 'api' in parts:
                site_paths = site.getsitepackages()
                for site_path in site_paths:
                    module_path = os.path.join(site_path, *parts)
                    # Try as .py file
                    if os.path.exists(module_path + '.py'):
                        return spec_from_file_location(fullname, module_path + '.py')
                    # Try as directory with __init__.py
                    init_path = os.path.join(module_path, '__init__.py')
                    if os.path.exists(init_path):
                        return spec_from_file_location(fullname, init_path)

            # Fall back to local ComfyUI directory for other imports
            comfyui_path = os.environ.get('COMFY_UI_PATH', '/workspace/ComfyUI')
            local_path = os.path.join(comfyui_path, *parts)
            if os.path.exists(local_path + '.py'):
                return spec_from_file_location(fullname, local_path + '.py')
            init_path = os.path.join(local_path, '__init__.py') 
            if os.path.exists(init_path):
                return spec_from_file_location(fullname, init_path)

        return None

# Install the finder at the start of meta_path
sys.meta_path.insert(0, MultiPathFinder())