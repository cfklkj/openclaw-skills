"""
Deploy Mgr - 远程服务部署管理工具
安装脚本
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="deploy-mgr",
    version="1.0.0",
    author="OpenClaw",
    author_email="",
    description="远程服务部署管理工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cfklkj/openclaw-skills",
    packages=find_packages(where="src", exclude=["tests"]),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "paramiko>=2.7.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "deploy-mgr=cli:cli",
        ],
    },
)
