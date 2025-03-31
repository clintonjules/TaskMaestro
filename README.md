# TaskMaestro

**TaskMaestro** is a free, cross-platform orchestration engine that coordinates multiple LLMs to collaboratively complete complex tasks. It operates like a virtual project team, where each agent plays a defined role (manager, submanager, worker), creating a hierarchy that adapts dynamically to the structure of any given problem.

## 🚀 Key Features

- **Agent Hierarchy**: A top-level ManagerAgent breaks down complex tasks into subtasks and delegates them to WorkerAgents or SubManagerAgents (which are just ManagerAgents handling subparts).
- **Recursive Delegation**: If a Worker determines a task is too complex, it promotes itself to a ManagerAgent and subdivides the task further.
- **Multi-Model Support**: Use OpenAI, Anthropic (Claude), Google (Gemini), DeepSeek, xAI (Grok), and local models via Ollama — all configurable via simple CLI arguments or LLM-generated specs.
- **Dependency Awareness**: Tasks can specify dependencies using `depends_on`, and TaskMaestro will ensure execution happens in the correct order.
- **LLM-Agnostic Routing**: A Router handles communication and execution order, resolving dependencies and delegating tasks across agents.

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

## 🧪 Running the Project

```bash
python src/main.py --type api --provider openai --model gpt-4o
```

or with local models:

```bash
python src/main.py --type local --model llama3
```

## 🛠 Available CLI Arguments

| Flag         | Description                             | Required |
|--------------|-----------------------------------------|----------|
| `--type` / `-t`    | Either `api` or `local`                    | ✅        |
| `--provider` / `-p` | LLM provider name (`openai`, `ollama`, etc) | 🔁        |
| `--model` / `-m`   | Model name (`gpt-4o`, `mistral`, etc)     | ✅        |

## 🧩 Extending TaskMaestro

- Add more LLM providers inside `LLMAccess` class in `access.py`
- Modify role descriptions in `manager.py` and `worker.py`
- Expand dependency handling logic in `router.py`

## 🔮 Future Features

- Result synthesis by top-level manager
- Agent memory and message history
- Interactive UI for task tree visualization
- Parallel execution of independent agents

## 🤖 Example Output

```json
{
  "agents": [
    {
      "llm_type": "api",
      "api_provider": "openai",
      "model": "gpt-4o",
      "role": "worker",
      "task": "List ingredients for a vanilla cake"
    },
    {
      "llm_type": "local",
      "model": "mistral",
      "role": "worker",
      "task": "Describe how to bake the cake",
      "depends_on": "List ingredients for a vanilla cake"
    }
  ]
}
```

---

Made with ⚙️, LLMs, and recursive ambition.

