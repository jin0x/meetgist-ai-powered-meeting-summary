from setuptools import setup, find_packages

setup(
    name="meetgist",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "fastapi",
        "supabase",
        "python-dotenv",
        "assemblyai",
        "requests"
    ],
)