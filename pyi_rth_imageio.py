# PyInstaller runtime hook for imageio
# 修复 imageio 元数据读取问题

import sys
import os

# 在 PyInstaller 打包的应用中，修复 imageio 的元数据读取
if hasattr(sys, '_MEIPASS'):
    # 设置环境变量，让 imageio 跳过元数据检查
    os.environ['IMAGEIO_IGNORE_WARNINGS'] = '1'
    
    # 尝试修复 importlib.metadata 的问题
    try:
        import importlib.metadata
        # 如果 imageio 的元数据不存在，提供一个默认值
        original_version = importlib.metadata.version
        
        def patched_version(package):
            try:
                return original_version(package)
            except importlib.metadata.PackageNotFoundError:
                # 如果找不到包元数据，返回一个默认版本
                if package == 'imageio':
                    return '2.31.0'  # 使用一个合理的默认版本
                raise
        
        # 替换 version 函数
        importlib.metadata.version = patched_version
    except:
        pass

