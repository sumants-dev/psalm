# Pontus

`Pontus` creates a zero-trust microservice layer between you and LLM providers. Our main feature is that we provide the ability to santize PII in prompts and documents retrieved from RAG systems, yet keep AIs ability to personalize and answer approriately.

![Pontus, Architecture](./LLM_Architecture.png)


## Why Pontus

Open Source: Extensibility and transparency are core to our mission.
Privacy: We tokenize PII and prevent it from being sent to AI services.
Zero-Trus: We do not store PII anywhere at REST.
Secure RAG: We add context and prevent hallucination through RAG without exposing unsantized document data.
Safety: We prevent dangerous content from being sent to or from AI services.
Monitoring: We provide monitoring and auditing of AI requests and responses.
Decoupling: We decouple your application from AI services, allowing you to switch between AI services without changing your application.
Self Hosting: We allow you to self host Pontus, giving you full control over your data.

## Quickstart

1. Create the following configuration file `pontus.yaml`
```yaml
version: "0.1"
provider:
  type: openai
  api_key: put-your-api-key-here
vector_db:
  type: pgvector
  conn_str: put-your-connection-string-here
embedder:
  type: sentence
  model: all-MiniLM-L6-v2
anoymizer:
  type: presidio
  # this is an example key don't use in prod
  key: WmZq4t7w!z%C&F)J
  threshold: .5
  entity_resolution: containment
  pii_types:
    - person
    - email_address
```

2. Create your virtual environment `python -m venv .venv`
3. Activate virtual environment `source .venv/bin/activate`
4. Install requirements `pip env install`
5. Run Development Server `make dev`
6. Make your first call to the microservice layer. We give an example in python, but any language will do.

```python
import requests, json
api_url = "http://localhost:8000"

request = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": "system",
            "content": "Context: Rushabh is very passionate about technology and loves tinkering with new products. He enjoys spending quality time in nature in his free time. He's early in his career, so he's willing to forgo salary for career growth. Jonah is an entrepreneur at heart and believes that tech companies are the best suited for making lots of money. He's willing to work long hours, as long as he's working on a cause he believes in.",
            "name": "context"
        },
        {
            "role": "system",
            "content": "Please provide a JSON response with the following format: {name: [ordered list of features]}"
        },
        {
            "role": "user",
            "content": "Rank the importance of these features of jobs for Rushabh and Jonah: 1. Compensation 2. Work Life Balance 3. Company Mission",
            "name": "rankings"
        }
    ]
}

res = requests.post(api_url + "/llm/chat/completions?debug=true", json=request)
response = res.json()
```