# PyInstaller hook for imageio
# 修复 imageio 元数据问题

from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules
import os
import glob

# 收集 imageio 的所有数据，包括元数据
datas, binaries, hiddenimports = collect_all('imageio')

# 收集 imageio_ffmpeg 的所有数据
try:
    imageio_ffmpeg_datas, imageio_ffmpeg_binaries, imageio_ffmpeg_hidden = collect_all('imageio_ffmpeg')
    datas += imageio_ffmpeg_datas
    binaries += imageio_ffmpeg_binaries
    hiddenimports += imageio_ffmpeg_hidden
except:
    pass

# 收集 moviepy 的所有数据
try:
    moviepy_datas, moviepy_binaries, moviepy_hidden = collect_all('moviepy')
    datas += moviepy_datas
    binaries += moviepy_binaries
    hiddenimports += moviepy_hidden
except:
    pass

# 收集 librosa 的所有数据
try:
    librosa_datas, librosa_binaries, librosa_hidden = collect_all('librosa')
    datas += librosa_datas
    binaries += librosa_binaries
    hiddenimports += librosa_hidden
except:
    pass

# 收集 pygame 的所有数据
try:
    pygame_datas, pygame_binaries, pygame_hidden = collect_all('pygame')
    datas += pygame_datas
    binaries += pygame_binaries
    hiddenimports += pygame_hidden
except:
    pass

# 确保包含元数据文件（.dist-info 目录）
try:
    import site
    import sys
    
    # 查找所有 site-packages 目录
    site_packages_dirs = site.getsitepackages()
    if hasattr(sys, 'real_prefix'):  # 虚拟环境
        site_packages_dirs.append(site.getusersitepackages())
    
    # 查找 imageio 的 dist-info 目录
    for site_dir in site_packages_dirs:
        if os.path.exists(site_dir):
            # 查找 imageio-*.dist-info 目录
            dist_info_pattern = os.path.join(site_dir, 'imageio-*.dist-info')
            for dist_info_path in glob.glob(dist_info_pattern):
                if os.path.isdir(dist_info_path):
                    datas.append((dist_info_path, '.'))
                    break
except:
    pass

