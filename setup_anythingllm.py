#!/usr/bin/env python3
"""
Setup script for AnythingLLM integration.
This script helps you upload documents to your AnythingLLM workspace.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the sci_platform directory to the path
sys.path.append('sci_platform')

from anythingllm_client import AnythingLLMClient

def upload_documents_from_directory(client: AnythingLLMClient, directory: str, file_extension: str = ".txt"):
    """Upload all files with specified extension from a directory to AnythingLLM."""
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist. Skipping...")
        return 0
    
    uploaded_count = 0
    files = [f for f in os.listdir(directory) if f.endswith(file_extension)]
    
    print(f"Found {len(files)} {file_extension} files in {directory}")
    
    for filename in files:
        file_path = os.path.join(directory, filename)
        print(f"Uploading {filename}...")
        
        if client.upload_document(file_path, filename):
            uploaded_count += 1
            print(f"✓ Successfully uploaded {filename}")
        else:
            print(f"✗ Failed to upload {filename}")
    
    return uploaded_count

def main():
    """Main setup function."""
    print("AnythingLLM Setup Script")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    try:
        # Initialize AnythingLLM client
        client = AnythingLLMClient()
        print(f"✓ Connected to AnythingLLM at {client.api_url}")
        print(f"✓ Using workspace: {client.workspace_slug}")
        
        # Check if workspace exists
        workspace_info = client.get_workspace_info()
        if not workspace_info:
            print("Workspace not found. Creating new workspace...")
            if client.create_workspace():
                print("✓ Workspace created successfully")
            else:
                print("✗ Failed to create workspace")
                return
        else:
            print("✓ Workspace found")
        
        # Upload documents from common directories
        total_uploaded = 0
        
        # Define directories to check for documents
        document_directories = [
            "./data/papers",
            "./data/papers_future", 
            "./data/authors",
            "./Papers",
            "./Papers_future",
            "./Authors/books"
        ]
        
        for directory in document_directories:
            if os.path.exists(directory):
                print(f"\nUploading documents from {directory}...")
                uploaded = upload_documents_from_directory(client, directory)
                total_uploaded += uploaded
                print(f"Uploaded {uploaded} files from {directory}")
        
        print(f"\n" + "=" * 50)
        print(f"Setup complete! Total files uploaded: {total_uploaded}")
        
        if total_uploaded == 0:
            print("\nNo documents were uploaded. Please ensure you have:")
            print("1. Extracted your paper archives (papers.tar.gz, papers_future.tar.gz, etc.)")
            print("2. Placed them in one of these directories:")
            for directory in document_directories:
                print(f"   - {directory}")
            print("\nYou can also manually upload documents through the AnythingLLM web interface.")
        
    except ValueError as e:
        print(f"✗ Configuration error: {e}")
        print("\nPlease ensure your .env file contains:")
        print("ANYTHINGLLM_API_KEY=your_api_key_here")
        print("ANYTHINGLLM_API_URL=http://localhost:3001/api")
        print("ANYTHINGLLM_WORKSPACE_SLUG=scientific-papers")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nPlease ensure:")
        print("1. AnythingLLM is running and accessible")
        print("2. Your API key is valid")
        print("3. The workspace exists or can be created")

if __name__ == "__main__":
    main()