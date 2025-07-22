# Flask Text Summarizer

A simple web application for extractive text summarization using Python, Flask, and NLTK. This app allows users to input text and receive a concise summary, either via a web form or a REST API.

## Features

- **Extractive Summarization**: Summarizes input text by selecting the most important sentences based on word frequency.
- **Web Interface**: User-friendly form for submitting text and viewing summaries.
- **REST API**: `/api/summarize` endpoint for programmatic access.
- **Health Check**: `/health` endpoint for service monitoring.
- **Robust NLTK Handling**: Automatically downloads required NLTK data if missing.

## Requirements

- Python 3.7+
- Flask
- NLTK

## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/flask-text-summarizer.git
   cd flask-text-summarizer
   ```

2. **Create a virtual environment (optional but recommended):**
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

   If `requirements.txt` does not exist, install manually:
   ```sh
   pip install flask nltk
   ```

4. **Download NLTK data (optional):**
   The app will attempt to download required NLTK data automatically on first run.

## Usage

### Run the Application

```sh
python app.py
```

The app will be available at [http://localhost:5000](http://localhost:5000).

### Web Interface

- Open your browser and go to [http://localhost:5000](http://localhost:5000).
- Enter the text you want to summarize and specify the number of summary sentences.

### API Usage

Send a POST request to `/api/summarize` with JSON payload:

```json
{
  "text": "Your text to summarize goes here.",
  "summary_length": 3
}
```

Example using `curl`:

```sh
curl -X POST http://localhost:5000/api/summarize \
     -H "Content-Type: application/json" \
     -d '{"text": "Your text here.", "summary_length": 3}'
```

### Health Check

Check if the service is running:

```sh
curl http://localhost:5000/health
```

## Project Structure

```
app.py
templates/
    index.html
    result.html
static/
    js/
        script.js
```

## Customization

- Adjust the default summary length or allowed range in [`app.py`](app.py).
- Modify the summarization logic in the `TextSummarizer` class for improved results.

## License

MIT License

---

**Author:** Tushar Mathur  
**GitHub:** https://github.com/TusharMathur24
