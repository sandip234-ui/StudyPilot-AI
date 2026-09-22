# StudyPilot — AI-Powered Personalized Learning Assistant

StudyPilot is an academic-grade, locally-hosted web application that provides personalized learning sessions powered by local Large Language Models (LLMs) via Ollama. It features a complete experimental laboratory for evaluating prompt engineering strategies and a transparent, rubric-based evaluation framework.

---

## 1. Problem Statement

Standard educational resources and generic AI chatbots often provide one-size-fits-all explanations. When students ask questions, they typically receive unstructured text that:
- Ignores the student's existing knowledge level (e.g., overwhelming beginners with esoteric syntax or boring advanced students with trivialities).
- Disregards available study time and preferred explanation style.
- Fails to provide active learning materials such as analogies, code demonstrations, self-test quizzes, and revision checklists.
- Lacks prompt transparency and rigorous educational evaluation.

---

## 2. Solution

StudyPilot addresses these challenges by acting as a personalized educational compiler:
1. **Context-Aware Prompt Engineering**: Converts student profile parameters (knowledge level, learning goal, available time, difficulty, explanation style, output type) into structured LLM prompts.
2. **Deterministic Response Structuring**: Enforces strict JSON output schemas from local LLMs, parsing raw model outputs into interactive educational components (objectives, step-by-step breakdown, code snippets, analogies, interactive multiple-choice quizzes, and revision checklists).
3. **Prompt Engineering Lab**: Provides a controlled experimental environment comparing four prompt engineering techniques (`baseline`, `role`, `personalized`, `structured`) on the exact same student request.
4. **Few-Shot Experimentation Lab**: Compares `zero-shot` vs `few-shot` prompting with curated demonstrations under strictly controlled variables.
5. **Human-in-the-Loop Evaluation Framework**: Evaluates generated content across 8 academic criteria using transparent 1–5 rubrics and verified score calculations without relying on self-grading LLM judges.

---

## 3. Core Features

### 🎓 1. Personalized Learning Session
- Collects required student context (`topic`, `knowledge_level`, `learning_goal`) and optional preferences (`available_time`, `explanation_style`, `difficulty`, `output_type`).
- Generates a rich, structured learning session featuring:
  - Measurable Learning Objectives
  - Core Concept Explanation
  - Step-by-Step Topic Breakdown
  - Concrete Code Examples with Explanations
  - Conceptual Analogies
  - Self-Check Practice Questions
  - Interactive Multiple-Choice Quiz with instant feedback and explanations
  - Interactive Revision Checklist with completion progress tracking

### 🔬 2. Prompt Engineering Lab
- Allows researchers and students to experimentally compare four prompt engineering strategies:
  - **Baseline**: Direct, minimal instruction prompt.
  - **Role**: Injects pedagogical persona (`expert AI tutor`).
  - **Personalized**: Progressively injects learner context and adaptive constraints.
  - **Structured**: Injects explicit schema instructions and structured output format.
- Executes strategies sequentially on local hardware to prevent memory thrashing.
- Provides side-by-side comparative cards with raw prompt inspectors and performance metrics (generation time in ms, token usage).

### 💡 3. Few-Shot Prompting Lab
- Controlled comparison of **Zero-Shot** vs **Few-Shot** prompting.
- Keeps topic, student context, model, task, instructions, and output schema identical.
- Injects fixed, curated demonstration examples (`Variables in Java`) into the few-shot condition to examine formatting and output consistency without prompt answer leakage.
- Collapsible prompt and demonstration example inspectors.

### 📊 4. Rubric-Based Evaluation Framework
- Evaluates model outputs across **8 standardized academic criteria**:
  1. Relevance
  2. Personalization
  3. Instruction Adherence
  4. Clarity
  5. Completeness
  6. Difficulty Alignment
  7. Time Alignment (supports N/A when time is unspecified)
  8. Structure / Schema Quality
- Standard 5-point scale (1 = Poor, 2 = Needs Improvement, 3 = Acceptable, 4 = Good, 5 = Excellent).
- Real-time transparent scoring formula:
  $$\text{Percentage} = \left( \frac{\sum \text{Applicable Scores}}{\sum \text{Applicable Maximum Scores}} \right) \times 100$$
- Backend validation endpoint (`POST /api/evaluate`).
- Comparative Criteria Matrix table stored in browser `localStorage`.
- Zero automated rankings or winner declarations.

---

## 4. System Architecture

```text
                               +----------------------------------+
                               |     React + Tailwind Frontend    |
                               |  (Vite Dev Server / Port 5173)   |
                               +-----------------+----------------+
                                                 |
                                     Relative HTTP Requests
                                     (Vite Proxy: /api/*)
                                                 |
                                                 v
                               +-----------------+----------------+
                               |       FastAPI Backend API        |
                               |      (Uvicorn / Port 8000)       |
                               +-----------------+----------------+
                                                 |
                       +-------------------------+-------------------------+
                       |                         |                         |
                       v                         v                         v
               /api/learn, /api/prompt-lab,  /api/few-shot-lab       /api/evaluate
                       |                         |                         |
                       v                         v                         v
            +----------+----------+   +----------+----------+   +----------+----------+
            |  Prompt Engineering |   | Few-Shot Prompting  |   | Evaluation Service  |
            |       Engine        |   |       Module        |   |  (Score & N/A Calc) |
            +----------+----------+   +----------+----------+   +---------------------+
                       |                         |
                       +------------+------------+
                                    |
                                    v
                       +------------+------------+
                       |      Ollama Service     |
                       |    (HTTPX Client Pool)  |
                       +------------+------------+
                                    |
                               HTTP Requests
                             (localhost:11434)
                                    |
                                    v
                       +------------+------------+
                       |       Local Ollama      |
                       |       llama3.2:3b       |
                       +------------+------------+
                                    |
                            Raw Model Response
                                    |
                                    v
                       +------------+------------+
                       |     Response Parser     |
                       |   (Markdown Stripping & |
                       |    JSON Normalization)  |
                       +------------+------------+
                                    |
                                    v
                       +------------+------------+
                       |   Pydantic Validation   |
                       |  (StructuredSession)    |
                       +------------+------------+
                                    |
                          Validated JSON Payload
                                    |
                                    v
                       +------------+------------+
                       |    React UI Components  |
                       |   (5-State Learning UI) |
                       +-------------------------+
```

---

## 5. Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI 0.115.0
- **ASGI Server**: Uvicorn 0.32.0
- **Validation**: Pydantic v2 (2.9.2)
- **HTTP Client**: HTTPX 0.27.2
- **Testing**: pytest 8.3.3 (274 unit & integration tests)

### Frontend
- **Framework**: React 19
- **Build Tool**: Vite 8.3.0
- **Styling**: Tailwind CSS v4
- **State Management**: React Hooks (`useState`, `useCallback`, `useRef`, custom hooks)
- **Persistence**: Browser `localStorage`

### Local AI / LLM
- **Engine**: Local Ollama Daemon
- **Active Model**: `llama3.2:3b` (3.2 Billion Parameters)
- **Privacy**: 100% local inference. Zero cloud API calls, zero telemetry, zero API keys required.

---

## 6. Prompt Engineering Techniques

| Strategy | Primary Technique | Description |
| :--- | :--- | :--- |
| **Baseline** | Direct Instruction | Minimal prompt containing only the topic, knowledge level, and learning goal. |
| **Role** | Role / Persona Prompting | Injects the persona of an expert educational AI tutor specializing in personalized instruction. |
| **Personalized** | Dynamic Context Injection | Injects all learner context parameters and adaptive pedagogical constraints. |
| **Structured** | Output Schema Enforcement | Injects explicit section headers, formatting rules, and strict JSON output schemas. |
| **Zero-Shot** | Zero-Shot Task Execution | Generates structured learning session without demonstration examples. |
| **Few-Shot** | In-Context Demonstration | Injects static, curated demonstration examples (`Variables in Java`) to guide structure. |

---

## 7. Installation & Setup

### Prerequisites
- macOS, Linux, or Windows (WSL recommended for Windows).
- Python 3.11+.
- Node.js 18+ and npm.
- [Ollama](https://ollama.com/) installed and running.

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd StudyPilot
```

### Step 2: Set Up Local Ollama Model
Ensure Ollama is running, then pull the `llama3.2:3b` model:
```bash
ollama serve
# In another terminal window:
ollama pull llama3.2:3b
```

### Step 3: Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS / Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

Verify backend tests:
```bash
pytest -v
# All 274 tests should pass
```

Start the FastAPI backend:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000
```
Backend will be live at `http://127.0.0.1:8000`. API documentation is available at `http://127.0.0.1:8000/docs`.

### Step 4: Frontend Setup
In a new terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Run lint and production build check
npm run lint
npm run build

# Start Vite development server
npm run dev
```
Frontend will be live at `http://127.0.0.1:5173`.

---

## 8. Usage Guide

1. **Personalized Learning (`🎓 Learning`)**:
   - Enter any learning topic (e.g., `Explain recursion in Java`).
   - Select your knowledge level and primary learning goal.
   - (Optional) Customize available time, explanation style, difficulty, and output format.
   - Click **Generate Learning Session**.
   - Interact with the code examples, take the interactive quiz, and check off items in the revision checklist.
2. **Prompt Engineering Lab (`🔬 Prompt Lab`)**:
   - Input your topic and preferences.
   - Click **Run Experiment** to execute all 4 strategies sequentially.
   - Inspect raw prompts and compare outputs side-by-side.
3. **Few-Shot Lab (`💡 Few-Shot Lab`)**:
   - Compare Zero-Shot vs Few-Shot prompt outputs side-by-side.
   - Toggle **View Demonstration Examples** to inspect the static curated in-context example.
4. **Evaluation Framework (`📊 Evaluation`)**:
   - Select a generated session or built-in reference session.
   - Inspect the learner context and unmodified model output on the left.
   - Rate each of the 8 criteria (1–5) and toggle N/A for Time Alignment if applicable.
   - Provide short justifications.
   - Click **⚡ Verify with Backend** and **💾 Save Evaluation** to record scores in the criteria comparison matrix.

---

## 9. Hardware & Performance Notes

- **Target Architecture**: Designed and verified on Apple Silicon (**M1 chip with 8 GB unified memory**).
- **Execution Model**: Multi-strategy experiments execute **sequentially** rather than concurrently, preventing memory pressure and thermal throttling on 8GB machines.
- **Typical Generation Time**:
  - `llama3.2:3b` generates a complete structured session in **18–25 seconds** on Apple Silicon GPU acceleration (Metal).

---

## 10. Verification & Quality Assurance

- **Backend Test Suite**: 274 tests passing (0 failures).
- **Frontend Linter**: ESLint passes with 0 errors and 0 warnings.
- **Frontend Build**: Vite production build transforms and bundles all assets cleanly.
- **Error Handling**: Comprehensive mapping of timeouts (504), Ollama unavailability (503), malformed outputs (502), and validation errors (422).
