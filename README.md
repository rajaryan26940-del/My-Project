
# AdaptiveAI — Self-Learning Autonomous Agent Framework

AdaptiveAI is a self-learning autonomous agent system built in Python. It features episodic memory storage, self-evaluating execution rewards, dynamic strategy selection (balancing exploration and exploitation using ML models and contextual multi-armed bandit strategies), and an interactive web interface.

## Features

- **Autonomous Agent Execution Engine**: Executes tasks across code execution, web search, mathematical calculations, and data processing.
- **Episodic Memory & Reward System**: Logs execution metrics, execution time, and evaluates composite reward scores for continuous reinforcement learning.
- **ML Strategy Predictor**: Dynamically retrains machine learning models to choose the optimal reasoning and execution strategy per domain category.
- **Web UI & REST API**: Interactive dashboard built with HTML5, CSS3, and JavaScript, powered by a Python backend server.
- **Automated Benchmarking**: Built-in benchmark suite to demonstrate learning progression over sequential task batches.

## Directory Structure

```text
├── backend/
│   ├── agent.py            # Main AdaptiveAgent controller
│   ├── app.py              # Backend REST API server
│   ├── core/               # Core execution engine & strategy management
│   ├── learning/           # ML strategy predictor & reinforcement model
│   ├── memory/             # Episodic memory database management
│   └── tools/              # Tool integrations (Python executor, math, search)
├── frontend/
│   ├── index.html          # Web application user interface
│   ├── styles.css          # UI styles and modern dashboard layout
│   └── app.js              # Frontend logic & API interaction
├── data/                   # Episodic memory database storage
├── models/                 # Trained ML strategy models (.pkl)
├── tests/                  # Unit and integration test suite
├── run_demo.py             # Autonomous learning benchmark script
└── requirements.txt        # Project dependencies
```

## Getting Started

### Prerequisites

- Python 3.8+

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/rajaryan26940-del/My-Project.git
   cd My-Project
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Demonstration

To run the self-learning agent benchmark:

```bash
python run_demo.py
```

### Running the Web Server & UI

Start the backend API server:

```bash
python -m backend.app
```
<img width="1912" height="856" alt="Screenshot 2026-09-23 234821" src="https://github.com/user-attachments/assets/4a926347-e962-494d-a468-15c743458451" />

<img width="1917" height="868" alt="Screenshot 2026-09-23 234841" src="https://github.com/user-attachments/assets/0d8b26d6-2e28-4a7e-893a-653781ee2b87" />

<img width="1903" height="852" alt="Screenshot 2026-09-23 234901" src="https://github.com/user-attachments/assets/a6f705eb-dc31-4ea8-9621-e57103107b3b" />

<img width="1915" height="870" alt="Screenshot 2026-09-23 234915" src="https://github.com/user-attachments/assets/5abdebd4-12e9-4375-b723-8872bba48fd6" />

Then open `frontend/index.html` in your browser.

## License

MIT License
