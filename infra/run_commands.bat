@echo off
python --version
python ./chat/scripts/ingest.py
aws s3 cp ./chroma_db.tar.gz s3://chatbot-chromadb-katcilane-9e85c834
aws s3 cp ./ready_flag s3://chatbot-chromadb-katcilane-9e85c834/ready_flag
