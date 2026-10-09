# 🧠 ARCHIMEDES
### Visual Intelligence for Physics, Mathematics & Science

**ARCHIMEDES** is an AI-powered visual learning assistant designed to help students understand and solve problems in physics, mathematics, and science through image understanding, mathematical reasoning, and step-by-step explanations.

Transform a scientific problem into an interactive learning experience.

---

## 🚀 Overview

Understanding complex scientific concepts often requires more than a final answer. ARCHIMEDES helps learners explore the reasoning behind a solution by combining multimodal AI with an interactive question-and-answer interface.

Upload an image of a problem, ask a question, and receive a structured explanation designed to make challenging concepts easier to understand.

## ✨ Key Features

- **📷 Visual Problem Understanding** — Upload images containing equations, diagrams, graphs, scientific problems, and handwritten or printed questions.
- **🧮 Mathematical Reasoning** — Explore mathematical problems with formulas, calculations, and step-by-step solutions.
- **⚙️ Physics Problem Solving** — Get explanations of physics principles, equations, and numerical problems.
- **🔬 Scientific Explanations** — Understand the concepts and principles behind scientific questions.
- **💬 Interactive Follow-up Questions** — Continue the conversation to clarify concepts and explore related questions.
- **📧 Email Integration** — Send generated explanations through the Gmail API.
- **🌐 Cloud Deployment** — Access the application through a deployed Streamlit web interface.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Streamlit | Interactive web application |
| OpenRouter API | Access to multimodal AI models |
| Google Gemini-compatible or other vision-capable models via OpenRouter | Image and question understanding, depending on model availability |
| Gmail API | Email delivery |
| Google OAuth 2.0 | Gmail authorization |
| Git & GitHub | Version control and source code management |
| Streamlit Community Cloud | Application hosting |

## 🔄 How It Works

1. **Input:** The user uploads a scientific image or enters a question.
2. **Processing:** ARCHIMEDES prepares the question, image, and conversation context.
3. **AI Analysis:** The application sends the request to a vision-capable model through OpenRouter.
4. **Explanation:** The model generates a response with relevant concepts, formulas, calculations, and reasoning.
5. **Follow-up:** The user can ask additional questions in the same conversation.
6. **Email:** The user can send the latest explanation through the integrated Gmail feature.

## 📐 Example Use Cases

- Solving geometry and algebra problems.
- Understanding equations and mathematical derivations.
- Analyzing physics diagrams and numerical questions.
- Explaining scientific illustrations and graphs.
- Learning the principles behind a solution rather than memorizing an answer.

## 📦 Project Structure

```text
ARCHIMEDES/
├── app.py
├── prompts.py
├── requirements.txt
├── README.md
├── .gitignore
└── .streamlit/
    └── secrets.toml.example
```

**File descriptions**

- `app.py` — Main Streamlit application, image processing, AI interaction, conversation management, and email functionality.
- `prompts.py` — System prompt and instructions that guide the AI tutor's responses.
- `requirements.txt` — Python dependencies.
- `.gitignore` — Excludes local environments and sensitive credentials from version control.
- `.streamlit/secrets.toml.example` — Example configuration for required secrets without exposing actual credentials.

## ⚙️ Local Installation

### Prerequisites

- Python 3.10 or later
- Git
- An OpenRouter API key
- Google OAuth credentials configured for Gmail API access

### 1. Clone the repository

```bash
git clone https://github.com/the-nikhil-11/ARCHIMEDES.git
cd ARCHIMEDES
```

### 2. Create a virtual environment

**Windows**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run the application using the virtual environment's Python executable directly.

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure secrets

Create `.streamlit/secrets.toml` locally and configure the credentials required by the application.

Example:

```toml
OPENROUTER_API_KEY = "your_openrouter_api_key"
GMAIL_ADDRESS = "your_gmail_address"
```

Configure the Gmail OAuth credentials according to the application's authentication implementation.

**Security:** Never commit API keys, OAuth tokens, client secrets, or personal credentials to GitHub.

### 5. Run the application

```bash
streamlit run app.py
```

Open the local URL displayed in the terminal.

## ☁️ Deployment

ARCHIMEDES can be deployed using Streamlit Community Cloud.

1. Push the project to GitHub.
2. Sign in to Streamlit Community Cloud.
3. Create a new app and select the ARCHIMEDES repository.
4. Select the `main` branch and set the main file to `app.py`.
5. Configure the required application secrets in the app settings.
6. Deploy and test the live application.

Keep sensitive credentials in Streamlit Secrets rather than in the repository.

## 🔐 Security Practices

- API keys and credentials should be stored outside source control.
- Local virtual environments and OAuth token files should be excluded through `.gitignore`.
- Production deployments should use securely configured secrets.
- OAuth credentials should be handled according to Google's security recommendations.

## 🎯 Project Objective

The goal of ARCHIMEDES is to make scientific learning more interactive, accessible, and understandable by combining visual input with AI-powered reasoning.

Instead of simply returning an answer, the application aims to help learners understand the concepts and methods used to reach it.

## 🔮 Future Improvements

- Interactive mathematical and physics visualizations.
- More structured derivations and equation rendering.
- Topic-wise learning paths and practice questions.
- Improved conversation history and downloadable explanations.
- Expanded support for scientific diagrams, graphs, and handwritten notes.

## 👨‍💻 Author

**Nikhil**

Creator and developer of ARCHIMEDES.

**GitHub:** [@the-nikhil-11](https://github.com/the-nikhil-11)

## 📄 License

Choose and add an appropriate open-source license before redistributing this project. Until a license is added, all rights remain with the copyright holder.

---

*ARCHIMEDES — Turning scientific questions into clearer understanding.*
