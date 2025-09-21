#!/usr/bin/env python3
"""
Setup script for AnythingLLM integration.
This script helps you upload documents to your AnythingLLM workspace.
"""

import os
import sys
import argparse
from pathlib import Path
from anythingllm_client import AnythingLLMClient

def upload_directory(client: AnythingLLMClient, directory_path: str, file_extensions: list = ['.txt']):
    """
    Upload all files with specified extensions from a directory to AnythingLLM.
    
    Args:
        client: AnythingLLM client instance
        directory_path: Path to directory containing files
        file_extensions: List of file extensions to upload
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        print(f"Directory {directory_path} does not exist")
        return False
    
    uploaded_count = 0
    failed_count = 0
    
    for ext in file_extensions:
        files = list(directory.glob(f"*{ext}"))
        print(f"Found {len(files)} {ext} files in {directory_path}")
        
        for file_path in files:
            print(f"Uploading {file_path.name}...")
            if client.upload_document(str(file_path)):
                uploaded_count += 1
                print(f"✓ Successfully uploaded {file_path.name}")
            else:
                failed_count += 1
                print(f"✗ Failed to upload {file_path.name}")
    
    print(f"\nUpload summary: {uploaded_count} successful, {failed_count} failed")
    return failed_count == 0

def create_sample_data():
    """Create sample scientific papers for testing."""
    data_dir = Path("./data")
    papers_dir = data_dir / "papers"
    papers_dir.mkdir(parents=True, exist_ok=True)
    
    sample_papers = [
        {
            "filename": "paper_1.txt",
            "content": """Title: Deep Learning for Natural Language Processing: A Comprehensive Survey

Abstract: This paper presents a comprehensive survey of deep learning techniques applied to natural language processing (NLP). We review the evolution from traditional statistical methods to modern neural architectures, including recurrent neural networks, transformers, and large language models. Our analysis covers key applications such as machine translation, sentiment analysis, question answering, and text generation. We discuss the challenges and future directions in the field, emphasizing the importance of interpretability, efficiency, and ethical considerations in NLP systems.

Keywords: deep learning, natural language processing, transformers, neural networks, machine learning

Introduction: Natural language processing has undergone a revolutionary transformation with the advent of deep learning techniques. This survey aims to provide researchers and practitioners with a comprehensive overview of the current state of the art in deep learning for NLP."""
        },
        {
            "filename": "paper_2.txt", 
            "content": """Title: Attention Mechanisms in Computer Vision: From CNNs to Vision Transformers

Abstract: Attention mechanisms have become a cornerstone of modern computer vision architectures. This paper traces the evolution of attention in vision models, from early spatial attention in convolutional neural networks to the revolutionary Vision Transformer (ViT) architecture. We analyze different types of attention mechanisms, including spatial, channel, and self-attention, and their impact on model performance across various vision tasks. Our experimental evaluation demonstrates the effectiveness of attention-based models in image classification, object detection, and semantic segmentation.

Keywords: attention mechanisms, computer vision, transformers, convolutional neural networks, image processing

Introduction: The introduction of attention mechanisms has fundamentally changed how we approach computer vision problems, enabling models to focus on relevant parts of the input and achieve unprecedented performance."""
        },
        {
            "filename": "paper_3.txt",
            "content": """Title: Federated Learning: Privacy-Preserving Machine Learning for Distributed Data

Abstract: Federated learning has emerged as a promising paradigm for training machine learning models on distributed data while preserving privacy. This paper provides an in-depth analysis of federated learning algorithms, communication protocols, and privacy guarantees. We examine the challenges of non-IID data distribution, communication efficiency, and system heterogeneity in federated settings. Our work includes a comprehensive evaluation of different aggregation strategies and their impact on model convergence and performance.

Keywords: federated learning, privacy preservation, distributed machine learning, differential privacy, secure aggregation

Introduction: As data privacy concerns grow and regulations like GDPR become more stringent, federated learning offers a compelling solution for collaborative machine learning without centralizing sensitive data."""
        }
    ]
    
    for paper in sample_papers:
        file_path = papers_dir / paper["filename"]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(paper["content"])
    
    print(f"Created {len(sample_papers)} sample papers in {papers_dir}")
    return str(papers_dir)

def main():
    parser = argparse.ArgumentParser(description="Setup AnythingLLM workspace with scientific papers")
    parser.add_argument("--papers-dir", type=str, help="Directory containing paper files")
    parser.add_argument("--create-samples", action="store_true", help="Create sample papers for testing")
    parser.add_argument("--check-connection", action="store_true", help="Check connection to AnythingLLM")
    
    args = parser.parse_args()
    
    try:
        # Initialize client
        print("Initializing AnythingLLM client...")
        client = AnythingLLMClient()
        
        if args.check_connection:
            print("Checking connection to AnythingLLM...")
            workspace_info = client.get_workspace_info()
            if workspace_info:
                print("✓ Successfully connected to AnythingLLM")
                print(f"Workspace: {workspace_info.get('workspace', {}).get('name', 'Unknown')}")
            else:
                print("✗ Failed to connect to AnythingLLM")
                print("Please check your API URL and API key in the .env file")
                return
        
        if args.create_samples:
            print("Creating sample papers...")
            papers_dir = create_sample_data()
            args.papers_dir = papers_dir
        
        if args.papers_dir:
            print(f"Uploading papers from {args.papers_dir}...")
            success = upload_directory(client, args.papers_dir, ['.txt'])
            if success:
                print("✓ All papers uploaded successfully!")
            else:
                print("✗ Some papers failed to upload")
        
        if not args.papers_dir and not args.create_samples and not args.check_connection:
            print("No action specified. Use --help for options.")
            print("\nQuick start:")
            print("1. python setup_anythingllm.py --check-connection")
            print("2. python setup_anythingllm.py --create-samples")
            print("3. python setup_anythingllm.py --papers-dir /path/to/your/papers")
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. AnythingLLM running on http://localhost:3001")
        print("2. Valid API key in .env file")
        print("3. Workspace 'scientific-papers' created in AnythingLLM")

if __name__ == "__main__":
    main()