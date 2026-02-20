"""
安装配置脚本
"""

from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="upload-tool",
    version="1.0.0",
    description="文件压缩上传工具",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Fly",
    python_requires=">=3.8",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'paramiko>=2.12.0',
        'scp>=0.14.5',
        'tqdm>=4.66.1',
        'click>=8.1.7',
        'cryptography>=41.0.7',
    ],
    entry_points={
        'console_scripts': [
            'upload-tool=cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
