# TaskMaestro

**TaskMaestro** is a free, cross-platform orchestration engine that coordinates multiple LLMs to collaboratively complete complex tasks. It operates like a virtual project team, where each agent plays a defined role (manager, submanager, worker), creating a hierarchy that adapts dynamically to the structure of any given problem.

## 🚀 Key Features

- **Agent Hierarchy**: A top-level ManagerAgent breaks down complex tasks into subtasks and delegates them to WorkerAgents or SubManagerAgents (which are just ManagerAgents handling subparts).
- **Recursive Delegation**: If a Worker determines a task is too complex, it promotes itself to a ManagerAgent and subdivides the task further.
- **Multi-Model Support**: Use OpenAI, Anthropic (Claude), Google (Gemini), DeepSeek, xAI (Grok), and local models via Ollama — all configurable via simple CLI arguments.
- **Dependency Awareness**: Tasks can specify dependencies using `depends_on`, and TaskMaestro will ensure execution happens in the correct order.
- **LLM-Agnostic Routing**: A Router handles communication and execution order, resolving dependencies and delegating tasks across agents.
- **Iterative Task Execution**: Support for task repetition based on conditions and results.
- **Comprehensive Logging**: Detailed logging of task execution, dependencies, and results.

## 🧠 How It Works

1. The user defines a high-level task.
2. A ManagerAgent receives the task, analyzes it, and outputs a JSON list of agent assignments.
3. The Router reads the output and spins up appropriate agents to handle each task.
4. Workers either:
   - Complete the task directly
   - Or promote themselves to managers and decompose the task further.
5. Results are collected and optionally synthesized by the original ManagerAgent.

## 📦 Installation

```bash
git clone https://github.com/yourname/taskmaestro.git
cd taskmaestro
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 🔑 Environment Setup

Set up your API keys for the LLM providers you want to use:

```bash
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GOOGLE_API_KEY="your-google-key"
export DEEPSEEK_API_KEY="your-deepseek-key"
export XAI_API_KEY="your-xai-key"
```

## 🧪 Running the Project

```bash
python src/main.py --type api --provider openai --model gpt-4
```

or with local models:

```bash
python src/main.py --type local --model llama2
```

## 🛠 Available CLI Arguments

| Flag         | Description                             | Required |
|--------------|-----------------------------------------|----------|
| `--type` / `-l`    | Either `api` or `local`                    | ✅        |
| `--provider` / `-p` | LLM provider name (`openai`, `anthropic`, `google`, `deepseek`, `xai`) | 🔁        |
| `--model` / `-m`   | Model name (e.g., `gpt-4`, `claude-3`, `gemini-pro`)     | ✅        |
| `--task` / `-t`    | The task to execute (optional, defaults to "How to bake a cake") | ❌        |

## 🧩 Extending TaskMaestro

- Add more LLM providers inside `LLMAccess` class in `src/llm/access.py`
- Modify role descriptions in `src/agents/manager.py` and `src/agents/worker.py`
- Expand dependency handling logic in `src/agents/router.py`
- Add new logging features in `src/utils/logging.py`

## 🔮 Future Features

- Result synthesis by top-level manager
- Agent memory and message history
- Interactive UI for task tree visualization
- Parallel execution of independent agents
- Enhanced error handling and retry mechanisms
- Support for more LLM providers and models

## 📝 Logging

TaskMaestro maintains detailed logs in the `logs` directory, with timestamps for each run. Logs include:
- Task execution details
- Dependency resolution
- Agent interactions
- Results and iterations
- Error messages and warnings