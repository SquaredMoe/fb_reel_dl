"""Setup script for fb-reel-dl."""
from setuptools import setup, find_packages

setup(
    name="fb-reel-dl",
    version="1.0.0",
    description="Facebook Reels Bulk Downloader 📱 — Playwright + yt-dlp",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    author="nanofatdog",
    author_email="nutboy02.ai@gmail.com",
    url="https://github.com/nanofatdog/fb_reel_dl",
    project_urls={
        "Bug Tracker": "https://github.com/nanofatdog/fb_reel_dl/issues",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "playwright>=1.40.0",
        "yt-dlp>=2024.0.0",
    ],
    entry_points={
        "console_scripts": [
            "fb-reel-dl=fb_reel_dl.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Multimedia :: Video",
    ],
    include_package_data=True,
    zip_safe=False,
)
