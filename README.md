
# 📊 Security Rules & Targets Dashboard

A lightweight, browser-based dashboard for viewing, searching, and analyzing **security rules** and **targets**, with **dark mode**, **search filters**, and **LLM-powered explanations**.

Built using **HTML + TailwindCSS + Chart.js + Vanilla JS**, with optional integration to **Ollama** for local AI-powered rule and target analysis.

---

## ✨ Features

- **Navigation Tabs** – Switch between:
  - Dashboard (overview & charts)
  - Rules (searchable table with LLM explanation buttons)
  - Targets (searchable table with LLM risk analysis)
- **Dark Mode Toggle** – Persists between sessions using `localStorage`
- **Responsive Tables** – Mobile-friendly UI for rules and targets
- **Search Filtering** – Instant filtering for rules and targets
- **Interactive Charts** – Rule counts by source and type using Chart.js
- **LLM Integration (Optional)**:
  - **Explain Rule** – Summarizes rule purpose in plain language
  - **Analyze Target** – Performs quick risk analysis on a target
  - Uses [Ollama](https://ollama.ai/) running locally at `localhost:11434`

---

## 📂 Project Structure

```

.
├── index.html          # Main dashboard HTML
├── style.css           # TailwindCSS (or compiled styles)
├── script.js           # All dashboard logic (navigation, charts, theme, LLM calls)
├── rules.json          # Optional JSON dataset for rules
├── targets.json        # Optional JSON dataset for targets
└── README.md           # This file

````

---

## 🚀 Getting Started

### 1. Clone this repo
```bash
git clone https://github.com/your-username/security-dashboard.git
cd security-dashboard
````

### 2. Install dependencies

This project uses CDN links for **TailwindCSS** and **Chart.js**, so no build step is needed.
Just open `index.html` in a browser.

If you want **LLM integration**:

* Install [Ollama](https://ollama.ai/download)
* Pull your desired model:

```bash
ollama pull gemma3:1b
```

### 3. Serve the files

For some browsers, `fetch('rules.json')` requires an HTTP server:

```bash
# Python
python3 -m http.server 8000
# Node.js
npx serve
```

Then visit: [http://localhost:8000](http://localhost:8000)

---

## ⚙️ Configuration

* **Dark Mode**:
  Default is **dark** if no preference is saved in `localStorage`.

* **Data Files**:

  * `rules.json` should be an array of objects:

    ```json
    [
      {
        "rule_id": "R001",
        "name": "Suspicious Login",
        "data_source": "CDR",
        "rule_type": "Authentication",
        "description": "Detects unusual login patterns",
        "tags": ["login", "security"]
      }
    ]
    ```
  * `targets.json` (optional) should be an array:

    ```json
    [
      {
        "target_id": "T001",
        "target_type": "Server",
        "identifier": "srv-01",
        "status": "Active",
        "description": "Main application server"
      }
    ]
    ```

* **Ollama API**:
  The LLM buttons send POST requests to:

  ```
  http://localhost:11434/api/generate
  ```

  with payload:

  ```json
  {
    "model": "gemma3:1b",
    "prompt": "...",
    "stream": false
  }
  ```

---

## 🖥️ Usage

* **Switch Tabs**: Click "Dashboard", "Rules", or "Targets"
* **Dark/Light Mode**: Click the top-right toggle button
* **Explain Rule**: In the Rules table, click "Explain Rule ✨"
* **Analyze Target**: In the Targets table, click "Analyze Target ✨"
* **Search**: Type in the search bar to filter instantly

---

## 📊 Chart Behavior

* **Rules by Source** – CDR vs IPDR counts
* **Rules by Type** – Breakdown of rule categories
* Charts **update theme colors** when switching light/dark mode
* Chart instances are destroyed and recreated to avoid duplication

---

## 🛠 Development Notes

* Written in **vanilla JS** for portability
* Theme persistence via `localStorage`
* Chart.js configuration uses dynamic legend & tooltip colors
* Designed to run entirely **client-side** (except optional Ollama API calls)

---

## 📜 License

MIT License — Free to use, modify, and distribute.

---

