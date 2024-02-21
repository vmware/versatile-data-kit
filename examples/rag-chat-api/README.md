## RAG Question-answering Web Service

This script allows for the quick deployment of a local service which can answer questions based on
the context provided from a configured vector database.
To run it, you need to first install the required dependencies:
```
pip install -r requirements.txt
```

Then, you need to start the web service:
```
uvicorn chat_api:app --reload
```

You can now query the web service through the following command:
```
curl http://127.0.0.1:8000/question/ -H "Content-Type: application/json" -d '{"question": "INPUT-QUESTION-HERE"}
```

Alternatively, you can use the Python script for easier access + string formatting:
```
python question.py "INPUT-QUESTION-HERE"
```

### UI

To run the UI, you need to install `streamlit`:
```
pip install streamlit
```
Note that newer versions of `streamlit` require Python 3.8+.

Then, run the app:
```
streamlit run chat_app.py
```
