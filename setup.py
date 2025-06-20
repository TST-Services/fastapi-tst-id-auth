"""Setup скрипт для fastapi-tst-id-auth пакета"""

from setuptools import setup, find_packages
import os

# Читаем README для long_description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Читаем requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="fastapi-tst-id-auth",
    version="0.1.0",
    author="TST Team",
    author_email="support@tstservice.tech",
    description="FastAPI OAuth интеграция с TST ID для простой авторизации",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/tst-team/fastapi-tst-id-auth",
    project_urls={
        "Bug Tracker": "https://github.com/tst-team/fastapi-tst-id-auth/issues",
        "Documentation": "https://github.com/tst-team/fastapi-tst-id-auth#readme",
        "Source Code": "https://github.com/tst-team/fastapi-tst-id-auth",
        "TST ID Service": "https://id.tstservice.tech",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration :: Authentication/Directory",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "test": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
            "httpx>=0.24.0",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=9.0.0",
            "mkdocstrings[python]>=0.20.0",
        ],
    },
    include_package_data=True,
    package_data={
        "fastapi_tst_id_auth": ["py.typed"],
    },
    keywords=[
        "fastapi",
        "oauth",
        "authentication",
        "tst-id",
        "jwt",
        "auth",
        "authorization",
        "api",
        "microservice",
        "web",
        "async",
    ],
    entry_points={
        "console_scripts": [
            "tst-auth=fastapi_tst_id_auth.cli:main",
        ],
    },
    zip_safe=False,
) 