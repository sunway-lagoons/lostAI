# lostAI

lost and found but better

<<<<<<< Updated upstream
## Setup

This project uses [`uv`](https://docs.astral.sh/uv/) to manage the Python environment and dependencies. The core dependencies are:

- `gradio`
- `torch`
- `flask`
- `huggingface_hub`

### 1. Install uv

**macOS**

```bash
# Using the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh

# or with Homebrew
brew install uv
```

Restart your terminal (or run `source ~/.zshrc`) so the `uv` command is on your `PATH`.

**Windows**

```powershell
# Using the official installer (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# or with pip
pip install uv
```

Close and reopen your terminal so the `uv` command is available.

Verify the install on either platform:

```bash
uv --version
```

### 2. Create a virtual environment

**macOS**

```bash
uv venv
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
uv venv
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt)**

```bat
uv venv
.venv\Scripts\activate.bat
```

### 3. Install dependencies

Same command on both macOS and Windows:

```bash
uv pip install gradio torch flask huggingface_hub
```

> **Note (Windows):** If you need CUDA GPU support for `torch`, install it from the
> PyTorch index instead of the default PyPI wheel:
>
> ```powershell
> uv pip install torch --index-url https://download.pytorch.org/whl/cu121
> ```
>
> On macOS, the default `torch` wheel includes Apple Silicon (MPS) support.

### 4. Verify the install

```bash
python -c "import gradio, torch, flask, huggingface_hub; print('all good')"
```

## Running

```bash
python app.py
```
=======
## Run the backend

Install the backend dependencies and start the API from the repository root:

```sh
python -m pip install -r requirements.txt
python app_backend/main.py
```

The API listens on `http://127.0.0.1:5001`. Check `http://127.0.0.1:5001/api/health` for its health status. Set `APP_HOST` or `APP_PORT` to override the bind address or port.
>>>>>>> Stashed changes
