from setuptools import setup, find_packages

setup(
    name="pb-chatbot",
    version="0.1.0",
    description="Sistema de chatbot para documentos jurídicos",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.34.0",
        "langchain-aws>=0.1.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "langchain-chroma>=0.0.1",
        "chromadb>=0.4.22",
        "python-dotenv==1.0.0",
        "pypdf>=3.17.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.23.2",
        "pydantic>=2.4.2",
    ],
    python_requires="==3.12.3",
) 