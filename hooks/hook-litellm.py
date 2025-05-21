# hook-litellm.py
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all data files from litellm
datas = collect_data_files("litellm")

# Add specific paths for tokenizers
# datas += [
#     ('path/to/site-packages/litellm/litellm_core_utils/tokenizers/*.json', 'litellm/litellm_core_utils/tokenizers')
# ]

# Collect all submodules to be sure nothing is missed
hiddenimports = collect_submodules("litellm")
