# 📚 Ariv API Documentation

This document provides comprehensive API documentation for developers who want to integrate Ariv into their applications.

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Core Classes](#core-classes)
- [Pipeline API](#pipeline-api)
- [Orchestrator API](#orchestrator-api)
- [Tool API](#tool-api)
- [Configuration API](#configuration-api)
- [REST API](#rest-api)
- [Examples](#examples)

---

## 🚀 Quick Start

### Basic Usage

```python
from core.orchestrator import JugaadOrchestrator
from core.trv_pipeline import TRVPipeline
from config import get_model_paths
import yaml

# Initialize
model_paths = get_model_paths()
orchestrator = JugaadOrchestrator(model_paths)

# Load prompts
with open("prompts/meta_prompts.yaml", 'r') as f:
    prompts = yaml.safe_load(f)

pipeline = TRVPipeline(orchestrator, prompts)

# Query in any Indian language
result = pipeline.execute(
    query="एक रस्सी की दो टुकड़े, दोनों के दोनों रूखे",
    language="hindi",
    enable_critic=True,
    enable_deep_cot=True
)

print(result['final_answer'])
```

---

## 🏗️ Core Classes

### JugaadOrchestrator

The main orchestrator that manages model loading and generation.

```python
from core.orchestrator import JugaadOrchestrator

# Initialize with model paths
orchestrator = JugaadOrchestrator({
    'translator': 'models/translator.gguf',
    'reasoner': 'models/reasoner.gguf',
    'critic': 'models/critic.gguf'
})

# Generate with a specific model
response = orchestrator.generate(
    role='reasoner',
    prompt='What is 2+2?',
    max_tokens=512,
    temperature=0.7
)

print(response)
```

**Methods:**

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `generate(role, prompt, **kwargs)` | Generate text with specified model | role: str, prompt: str, max_tokens: int, temperature: float | str |
| `generate_with_tools(role, prompt, tools)` | Generate with tool calling | role: str, prompt: str, tools: List[str] | Dict |
| `chain_of_thought_generate(role, prompt, **kwargs)` | Generate with CoT reasoning | role: str, prompt: str, cot_depth: int | Dict |
| `self_consistency_generate(role, prompt, **kwargs)` | Generate with self-consistency | role: str, prompt: str, num_paths: int | Dict |
| `load_model(role, **kwargs)` | Load a model by role | role: str, n_ctx: int, n_gpu_layers: int | Llama |
| `unload_model()` | Unload current model | - | None |
| `get_stats()` | Get statistics | - | Dict |

### TRVPipeline

The main pipeline that implements the Translate-Reason-Verify loop.

```python
from core.trv_pipeline import TRVPipeline

# Initialize with orchestrator and prompts
pipeline = TRVPipeline(orchestrator, prompts)

# Execute a query
result = pipeline.execute(
    query="What is the capital of India?",
    language="english",
    enable_critic=True,
    enable_deep_cot=True,
    enable_self_consistency=True
)

print(result['final_answer'])
print(f"Time taken: {result['pipeline_time']}s")
```

**Methods:**

| Method | Description | Parameters | Returns |
|--------|-------------|------------|---------|
| `execute(query, language, **kwargs)` | Execute full TRV pipeline | query: str, language: str, enable_critic: bool, enable_deep_cot: bool | Dict |
| `benchmark_arc_agi_2(problems)` | Run ARC-AGI 2 benchmark | problems: List[Dict] | Dict |
| `get_stats()` | Get pipeline statistics | - | Dict |
| `reset_stats()` | Reset statistics | - | None |

---

## 🔧 Pipeline API

### Basic Pipeline Execution

```python
# Simple execution
result = pipeline.execute("What is 2+2?", "english")

# With advanced settings
result = pipeline.execute(
    query="एक रस्सी की दो टुकड़े, दोनों के दोनों रूखे",
    language="hindi",
    enable_critic=True,
    enable_deep_cot=True,
    enable_self_consistency=True,
    reasoning_model="reasoner"
)
```

### Response Format

```python
{
    "final_answer": "The answer in the original language",
    "reasoning_trace": [
        {
            "phase": "ingestion",
            "output": "Translated and culturally contextualized query"
        },
        {
            "phase": "reasoning",
            "output": "Step-by-step logical analysis"
        },
        {
            "phase": "critic",
            "output": "Verification and validation"
        },
        {
            "phase": "synthesis",
            "output": "Final answer with cultural adaptation"
        }
    ],
    "language": "hindi",
    "pipeline_time": 2.5,
    "critic_iterations": 2,
    "metadata": {
        "reasoning_model": "reasoner",
        "deep_cot": True,
        "self_consistency": True,
        "tools_enabled": False
    }
}
```

### Advanced Pipeline Features

#### Custom Reasoning Depth

```python
# Adjust reasoning depth
result = pipeline.execute(
    query="Complex mathematical problem...",
    language="english",
    enable_deep_cot=True,
    cot_depth=5  # Deeper reasoning
)
```

#### Tool-Enabled Pipeline

```python
# Enable tool calling
result = pipeline.execute(
    query="Calculate the area of a circle with radius 5",
    language="english",
    enable_tools=True,
    max_tool_calls=5
)
```

#### Batch Processing

```python
# Process multiple queries
queries = [
    {"query": "What is 2+2?", "language": "english"},
    {"query": "भारत की राजधानी क्या है?", "language": "hindi"},
    {"query": "2+2 என்ன?", "language": "tamil"}
]

results = []
for query in queries:
    result = pipeline.execute(**query)
    results.append(result)
```

---

## 🛠️ Orchestrator API

### Model Management

```python
from core.orchestrator import JugaadOrchestrator

# Initialize with model configuration
orchestrator = JugaadOrchestrator({
    'translator': 'models/sarvam-1-2b-q4.gguf',
    'reasoner': 'models/deepseek-r1-llama-8b-q4.gguf',
    'critic': 'models/airavata-7b-q4.gguf',
    'bridge': 'models/openhathi-7b-q4.gguf',
    'tamil_specialist': 'models/tamil-llama-7b-q4.gguf'
})

# Load and use a model
model = orchestrator.load_model('reasoner', n_ctx=4096)
response = orchestrator.generate('reasoner', 'What is AI?')
```

### Advanced Generation

```python
# Chain-of-thought generation
cot_result = orchestrator.chain_of_thought_generate(
    role='reasoner',
    prompt='Solve this step by step: If a train travels 120 km in 2 hours...',
    cot_depth=3,
    enable_reflection=True,
    enable_adversarial=True
)

print(cot_result['final_answer'])
for step in cot_result['reasoning_chain']:
    print(f"{step['step']}: {step['content'][:100]}...")
```

### Tool-Enabled Generation

```python
# Generate with tool calling
tool_result = orchestrator.generate_with_tools(
    role='reasoner',
    prompt='Calculate 15 * 23 and explain the result',
    tools=['calculator'],
    max_tool_calls=3
)

print(f"Response: {tool_result['text']}")
print(f"Tools used: {tool_result['tool_calls']}")
```

### Self-Consistency Generation

```python
# Multiple reasoning paths
sc_result = orchestrator.self_consistency_generate(
    role='reasoner',
    prompt='What is the next number in sequence: 2, 4, 8, 16, ?',
    num_paths=5,
    temperature=0.7
)

print(f"Final answer: {sc_result['final_answer']}")
print(f"Confidence: {sc_result['consistency_score']:.2%}")
print(f"Reasoning paths: {len(sc_result['reasoning_paths'])}")
```

---

## 🔧 Tool API

### Using Built-in Tools

```python
from tools.registry import ToolRegistry
from tools.tools import CalculatorTool, KnowledgeBaseTool

# Create registry
registry = ToolRegistry()

# Get tool information
info = registry.get_tool_info()
print(info)

# Execute a tool directly
calc = CalculatorTool()
result = calc.execute("15 * 23 + 7")
print(f"Result: {result}")
```

### Creating Custom Tools

```python
from tools.tools import BaseTool

class WeatherTool(BaseTool):
    def get_schema(self):
        return {
            "name": "weather",
            "description": "Get weather information for a location",
            "parameters": {
                "location": {
                    "type": "string",
                    "description": "City name or coordinates"
                }
            },
            "returns": "Weather information"
        }
    
    def execute(self, location):
        # Your weather API logic here
        return f"Weather in {location}: Sunny, 25°C"

# Register the tool
registry = ToolRegistry()
registry.register('weather', WeatherTool())

# Use in generation
result = orchestrator.generate_with_tools(
    role='reasoner',
    prompt='What is the weather like in Mumbai?',
    tools=['weather']
)
```

---

## ⚙️ Configuration API

### Loading Configuration

```python
from config import (
    INDIAN_LANGUAGES_22,
    MODEL_CONFIG,
    PIPELINE_CONFIG,
    get_model_paths,
    get_language_config,
    get_supported_languages
)

# Get all supported languages
languages = get_supported_languages()
print(f"Supported languages: {len(languages)}")

# Get language configuration
hindi_config = get_language_config('hindi')
print(f"Hindi script: {hindi_config['script']}")

# Get model paths
paths = get_model_paths()
print(f"Available models: {list(paths.keys())}")
```

### Custom Configuration

```python
# Override default settings
from config import PIPELINE_CONFIG

# Create custom config
custom_config = PIPELINE_CONFIG.copy()
custom_config['max_critic_iterations'] = 10
custom_config['temperature']['reasoning'] = 0.8

# Use with pipeline
pipeline = TRVPipeline(orchestrator, prompts, config=custom_config)
```

---

## 🌐 REST API

Ariv includes a FastAPI-based REST API for web integration.

### Starting the API Server

```bash
python deploy/api_wrapper.py
# Server runs on http://localhost:8000
```

### API Endpoints

#### POST /query

Execute a query through the Ariv pipeline.

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is 2+2?",
    "language": "english",
    "enable_critic": true,
    "enable_deep_cot": true,
    "enable_self_consistency": true
  }'
```

**Response:**
```json
{
  "final_answer": "4",
  "reasoning_trace": [...],
  "language": "english",
  "pipeline_time": 2.5,
  "critic_iterations": 1,
  "metadata": {...}
}
```

#### GET /languages

Get list of supported languages.

```bash
curl http://localhost:8000/languages
```

**Response:**
```json
{
  "languages": ["hindi", "tamil", "bengali", "telugu", ...],
  "count": 23
}
```

#### GET /status

Get system status and available models.

```bash
curl http://localhost:8000/status
```

**Response:**
```json
{
  "status": "ready",
  "models": {
    "translator": {"exists": true, "size_gb": 1.5},
    "reasoner": {"exists": true, "size_gb": 5.0}
  },
  "memory": {"allocated_gb": 2.1, "available_gb": 13.9}
}
```

#### POST /batch

Process multiple queries in batch.

```bash
curl -X POST http://localhost:8000/batch \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      {"query": "2+2?", "language": "english"},
      {"query": "2+2 कितना?", "language": "hindi"}
    ],
    "settings": {"enable_critic": true}
  }'
```

---

## 📚 Examples

### Example 1: Basic Query

```python
from core.trv_pipeline import TRVPipeline
from core.orchestrator import JugaadOrchestrator
from config import get_model_paths
import yaml

# Setup
model_paths = get_model_paths()
orchestrator = JugaadOrchestrator(model_paths)
with open("prompts/meta_prompts.yaml", 'r') as f:
    prompts = yaml.safe_load(f)
pipeline = TRVPipeline(orchestrator, prompts)

# Query
result = pipeline.execute(
    query="भारत की राजधानी क्या है?",
    language="hindi"
)

print(result['final_answer'])
# Output: भारत की राजधानी नई दिल्ली है।
```

### Example 2: Mathematical Problem

```python
result = pipeline.execute(
    query="यदि एक ट्रेन 120 किमी दूरी 2 घंटे में तय करती है, तो इसकी औसत गति कितनी है?",
    language="hindi",
    enable_tools=True
)

print(result['final_answer'])
# Output: ट्रेन की औसत गति 60 किलोमीटर प्रति घंटा है।
```

### Example 3: Chain-of-Thought Reasoning

```python
result = pipeline.execute(
    query="सभी गुलाब फूल हैं। कुछ फूल जल्दी मुरझाते हैं। इसलिए, कुछ गुलाब जल्दी मुरझाते हैं। क्या यह तर्क सही है?",
    language="hindi",
    enable_deep_cot=True,
    enable_critic=True
)

print(result['final_answer'])
# Output: यह तर्क तर्कसंगत नहीं है...
```

### Example 4: Batch Processing

```python
queries = [
    {"query": "What is 2+2?", "language": "english"},
    {"query": "2+2 कितना?", "language": "hindi"},
    {"query": "2+2 என்ன?", "language": "tamil"},
    {"query": "2+2 কত?", "language": "bengali"}
]

results = []
for query in queries:
    result = pipeline.execute(**query)
    results.append({
        "query": query["query"],
        "language": query["language"],
        "answer": result["final_answer"]
    })

print(results)
# Output: [{'query': 'What is 2+2?', 'language': 'english', 'answer': '4'},
#          {'query': '2+2 कितना?', 'language': 'hindi', 'answer': '२ + २ = ४'},
#          ...]
```

### Example 5: Custom Tool Integration

```python
from tools.registry import ToolRegistry
from tools.tools import BaseTool

class MyCustomTool(BaseTool):
    def get_schema(self):
        return {
            "name": "my_tool",
            "description": "Does something custom",
            "parameters": {"input": {"type": "string"}},
            "returns": "Custom result"
        }
    
    def execute(self, input):
        return f"Processed: {input}"

# Register and use
registry = ToolRegistry()
registry.register('my_tool', MyCustomTool())

# Use in orchestrator
result = orchestrator.generate_with_tools(
    role='reasoner',
    prompt='Use my_tool to process "hello world"',
    tools=['my_tool']
)
```

---

## 📊 Error Handling

### Pipeline Errors

```python
try:
    result = pipeline.execute("Invalid query", "invalid_language")
except ValueError as e:
    print(f"Invalid input: {e}")
except RuntimeError as e:
    print(f"Pipeline error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Model Loading Errors

```python
try:
    orchestrator.load_model('nonexistent_model')
except FileNotFoundError as e:
    print(f"Model not found: {e}")
except ModelLoadError as e:
    print(f"Failed to load model: {e}")
```

### Tool Errors

```python
try:
    result = registry.execute_tool_call('invalid_tool_call')
except ToolExecutionError as e:
    print(f"Tool execution failed: {e}")
except ValueError as e:
    print(f"Invalid tool call: {e}")
```

---

## 🔍 Logging and Debugging

### Enable Debug Logging

```python
import logging

# Set log level
logging.basicConfig(level=logging.DEBUG)

# Use in your application
logger = logging.getLogger('my_app')
logger.debug('Debug message')
```

### Pipeline Logging

```python
# Log pipeline execution
result = pipeline.execute(
    query="Test query",
    language="english",
    log_level="DEBUG"  # Enable detailed logging
)
```

### Statistics and Monitoring

```python
# Get detailed statistics
stats = pipeline.get_stats()
print(f"Queries: {stats['queries_processed']}")
print(f"Avg time: {stats['average_query_time']}")
print(f"Language dist: {stats['language_distribution']}")

# Get orchestrator stats
orch_stats = orchestrator.get_stats()
print(f"Models loaded: {orch_stats['models_loaded']}")
print(f"Avg tokens/sec: {orch_stats['average_tokens_per_second']}")
```

---

This API documentation covers the main interfaces of Ariv. For more detailed information, see the source code and inline documentation.
