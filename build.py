import PyInstaller.__main__
import sys
import os

# 添加必要的数据文件
added_files = [
    ('templates', 'templates'),
    ('static', 'static'),
]

if __name__ == '__main__':
    PyInstaller.__main__.run([
        'app.py',  # 注意这里的路径
        '--name=PersonalNotebook',
        '--onefile',
        '--windowed',
        '--add-data=templates;templates',  # Windows 使用分号
        '--add-data=static;static',
        '--hidden-import=pymysql',
        '--hidden-import=passlib.hash',
        '--hidden-import=flask',
        '--collect-all=flask',
        '--noconfirm',  # 自动覆盖输出目录
        '--clean',  # 清理临时文件
    ]) 