# Scientific Idea Generation with AnythingLLM

This is a modified version of the scientific idea generation application that uses AnythingLLM as the primary knowledge base and LLM provider instead of local FAISS indices and Ollama.

## Prerequisites

### 1. AnythingLLM Setup

1. **Install AnythingLLM**: Follow the official installation guide at [AnythingLLM Documentation](https://docs.anythingllm.com/)
   
   Using Docker (recommended):
   ```bash
   docker run -d -p 3001:3001 --cap-add SYS_ADMIN -v ${PWD}/server/storage:/app/server/storage -v ${PWD}/collector/hotdir:/app/collector/hotdir -v ${PWD}/collector/outputs:/app/collector/outputs -e STORAGE_DIR="/app/server/storage" mintplexlabs/anythingllm
   ```

2. **Access AnythingLLM**: Open http://localhost:3001 in your browser

3. **Configure LLM Provider**: 
   - Go to Settings → LLM Providers
   - Configure your preferred LLM (OpenAI, Anthropic, Ollama, etc.)
   - For local setup, you can use Ollama with models like `llama3.1`

4. **Configure Embedding Provider**:
   - Go to Settings → Embedding Providers  
   - Configure embedding model (e.g., Ollama with `mxbai-embed-large`)

5. **Create Workspace**:
   - Create a new workspace named "scientific-papers" (or update the slug in .env)
   - Note the workspace slug for configuration

6. **Generate API Key**:
   - Go to Settings → API Keys
   - Generate a new API key
   - Copy this key for the .env file

### 2. Environment Configuration

1. **Copy and configure the .env file**:
   ```bash
   cp .env.example .env
   ```

2. **Update .env with your settings**:
   ```env
   ANYTHINGLLM_API_URL=http://localhost:3001/api
   ANYTHINGLLM_API_KEY=your_actual_api_key_here
   ANYTHINGLLM_WORKSPACE_SLUG=scientific-papers
   ```

### 3. Python Environment

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Data Setup

### Option 1: Use Sample Data (Recommended for Testing)

```bash
cd sci_platform
python setup_anythingllm.py --create-samples
```

This creates sample scientific papers and uploads them to your AnythingLLM workspace.

### Option 2: Use Your Own Papers

1. **Prepare your papers**: Organize your scientific papers as .txt files in a directory

2. **Upload to AnythingLLM**:
   ```bash
   cd sci_platform
   python setup_anythingllm.py --papers-dir /path/to/your/papers
   ```

### Option 3: Manual Upload via Web Interface

1. Open AnythingLLM web interface
2. Navigate to your "scientific-papers" workspace
3. Use the upload feature to add your documents

## Running the Application

### 1. Test Connection

```bash
cd sci_platform
python setup_anythingllm.py --check-connection
```

### 2. Run the Simulation

```bash
cd sci_platform
python run.py
```

### 3. Custom Parameters

```bash
python run.py --runs 1 --team_limit 1 --max_discuss_iteration 3 --max_team_member 3 --epochs 2
```

## Key Changes from Original

### Architecture Changes

1. **Knowledge Base**: Replaced local FAISS indices with AnythingLLM's RAG system
2. **LLM Integration**: Uses AnythingLLM API instead of direct Ollama calls
3. **Document Management**: Documents are managed through AnythingLLM workspace
4. **Embedding Search**: Leverages AnythingLLM's built-in semantic search

### File Changes

- **New Files**:
  - `anythingllm_client.py`: Client for AnythingLLM API interactions
  - `setup_anythingllm.py`: Helper script for data upload and setup
  - `agentscope-main/src/agentscope/models/anythingllm_model.py`: AnythingLLM model wrapper
  - `.env`: Environment configuration

- **Modified Files**:
  - `sci_platform.py`: Removed FAISS, added AnythingLLM integration
  - `sci_agent.py`: Updated to use AnythingLLM for RAG and generation
  - `model_configs.json`: Added AnythingLLM model configuration
  - `requirements.txt`: Added new dependencies

### Benefits

1. **Simplified Setup**: No need for local FAISS indices or complex data preprocessing
2. **Better RAG**: AnythingLLM provides advanced RAG capabilities with better document chunking
3. **Web Interface**: Easy document management through AnythingLLM's web UI
4. **Scalability**: AnythingLLM can handle larger document collections more efficiently
5. **Flexibility**: Support for multiple LLM providers through AnythingLLM

## Troubleshooting

### Common Issues

1. **Connection Error**: 
   - Ensure AnythingLLM is running on http://localhost:3001
   - Check API key is correct in .env file

2. **Workspace Not Found**:
   - Verify workspace slug in .env matches your AnythingLLM workspace
   - Create the workspace if it doesn't exist

3. **No Documents Found**:
   - Upload documents using `setup_anythingllm.py` or web interface
   - Verify documents are processed in AnythingLLM workspace

4. **Model Configuration**:
   - Ensure LLM and embedding providers are configured in AnythingLLM
   - Check model names match your AnythingLLM setup

### Debug Mode

Add debug logging to see API interactions:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Output

The application generates the same outputs as the original:
- `team_info/`: JSON files with team ideas and abstracts
- `team_log/`: Detailed conversation logs
- Console output showing simulation progress

## Performance Notes

- AnythingLLM handles document chunking and embedding automatically
- RAG performance depends on your AnythingLLM configuration
- Consider using GPU acceleration for better performance with local models