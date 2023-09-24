# Pontus - The Open Source AI Orchestration Layer

`Pontus` creates a zero-trust microservice AI layer between services and LLM. With a configuration first approach, Pontus allows you to manage multiple AI building blocks such as PII, RAG, Caching, and more.

![Pontus, Architecture](./LLM_Architecture.png)


## Why Pontus

* Open Source: Extensibility and transparency are core to our mission.
* Privacy: We tokenize PII and prevent it from being sent to AI services.
* Zero-Trust: We do not store PII anywhere at REST.
* Secure RAG: We add context and prevent hallucination through RAG without exposing unsantized document data.
* Safety: We prevent dangerous content from being sent to or from AI services.
* Monitoring: We provide monitoring and auditing of AI requests and responses.
* Decoupling: We decouple your application from AI services, allowing you to switch between AI services without changing your application.
* Self Hosting: We allow you to self host Pontus, giving you full control over your data.

## Quickstart

1. Create the following configuration file `pontus.yaml`
```yaml
version: "0.1"
application:
  database:
    type: postgres
    conn_str: postgresql://postgres:postgres@localhost:5435/pontus
  authentication:
    type: api_key
    default_admin_username: admin
    default_admin_api_key: "1234"
llm:
  provider:
    type: openai
    default_model: gpt-3.5-turbo
    api_key: <put-api-key-here>
  anoymizer:
    type: presidio
    # don't use this key in production, it's just for testing
    key: WmZq4t7w!z%C&F)J
    threshold: .5
    entity_resolution: containment
    pii_types:
      - person
      - email_address
  cache:
    type: small_cache
    vector_db:
      type: pgvector
      conn_str: <put-conn-str>
      collection_name: prompt_cache
    embedder:
      type: sentence
      model: all-MiniLM-L6-v2
      max_length: 256

  pre_processors:
    remove_toxicity:
      type: simple
rag:
  vector_db:
    type: pgvector
    conn_str: <put-conn-str>
    collection_name: node
  embedder:
    type: sentence
    model: all-MiniLM-L6-v2
    max_length: 256
  anoymizer:
    type: presidio
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
