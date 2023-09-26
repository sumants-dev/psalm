
<div align="center">

  <img src="logo.jpg"  width="400"/>

  [Home](https://www.pontus.so) - [Docs](https://docs.pontus.so) - [Bug Report](https://github.com/PontusAI/Pontus/issues/new?assignees=&labels=bug&projects=&template=bug_report.md&title=%5BBUG%5D) 
</div>

`Pontus` allows you to build AI faster with privacy embeded throughout easily. 

Privacy should be easy. A declarative config defines core building blocks such as **PII Santization**, **Caching**, **Secure RAG**, and more. Pontus takes this yaml and constructs a microservices that acts a layer between your services and LLM providers.

## Table of Contents
* [Overview](#overview)
* [Features](#features)
* [Installation](#installation)
* [Quickstart](#quickstart)
* [Doc and Support](#docs-and-support)
* [Contributing](#contributing)
* [Philosophy](#philosophy)
* [Open Core](#open-core-model)

## Overview
The following diagram shows how Pontus works at high level.

![Pontus, Architecture](./LLM_Architecture.png)

We act as a layer in between you and LLMs. We make sure privacy is ensured when interacting with LLM providers.

## Features
✅ **Smart Tokenization**: Emails, names, addresses are automatically detected and tokenized when interacting with LLMs

✅ **Caching**: Save on GPT calls with semantic prompt cache

✅ **Secure Retrieval Augmented Generation**: All documents stored in a vector db do not have any PII at Rest

✅ **Declarative**: Configure simply with yaml that specific LLM building

✅ **Self Hosting**: Limit 3rd parties places of attacks

⌛ **Validation**: Structure are enforced in safe way

⌛ **Toxicity Detection**: Prevent NSFW content from being sent 

⌛ **Monitoring**: Understand what prompts are being logged and sent

## Installation

1. Create the following configuration file `pontus.yaml`. Checkout our [docs](www.docs.pontus.so) for more configuration options


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
      type: sentence_transformer
      model: all-MiniLM-L6-v2

  pre_processors:
    remove_toxicity:
      type: simple
rag:
  vector_db:
    type: pgvector
    conn_str: <put-conn-str>
    collection_name: node
  chunker:
    type: sentence
    chunk_overlap: 10
  embedder:
    type: sentence_transformer
    model: all-MiniLM-L6-v2
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

## Quickstart

After running server, simply call the API. Please see the  [api refeference](www.api.pontus.so).

### Request Sent
```python
import requests, json
api_url = "http://localhost:8000"

request = {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "messages": [
        {
            "role": "system",
            "content": "Do not answer the question until the context below is used.\n Here is the context: Rushabh. Rushabh is very passionate about technology and loves tinkering with new products. He enjoys spending quality time in nature in his free time. He's early in his career, so he's willing to forgo salary for career growth. ",
            "name": "context"
        },
        {
            "role": "user",
            "content": "Please explain the importance of the following factor Compensation, Work Life Balance, Company mission when Rushabh is looking for jobs.",
            "name": "rankings"
        }
    ]
}

res = requests.post(api_url + "/llm/chat/completions?debug=true", json=request)
response = res.json()
```

### What LLM provider saw
```json
[
    {
        "role": "system",
        "content": "Ensure that all placeholders, including those inside quotes, are enclosed by the greek letter alpha (\u03b1), exactly as I have done in this prompt. You MUST use the greek letter (\u03b1) to indicate placeholders. Use the context below to help answer the question and follow the desired format accurately.",
        "name": null,
        "function": null
    },
    {
        "role": "system",
        "content": "Do not answer the question until the context below is used.\n Here is the context: \u03b1EZfKxDQ\u03b1. \u03b1l8knK-s\u03b1 is very passionate about technology and loves tinkering with new products. He enjoys spending quality time in nature in his free time. He's early in his career, so he's willing to forgo salary for career growth. ",
        "name": "context",
        "function": null
    },
    {
        "role": "user",
        "content": "Please explain the importance of the following factor Compensation, Work Life Balance, Company mission when \u03b1gaBu_GQ\u03b1 is looking for jobs.",
        "name": "rankings",
        "function": null
    }
]
```

### Response 
We just highlight the message here
```json
[
  {
    "role": "assistant",
    "content": "When Rushabh is looking for jobs, there are several factors that are important to consider. Compensation, work-life balance, and company mission are three key factors that can greatly impact Rushabh's job satisfaction and overall career growth.\n\nCompensation, the first factor, refers to the financial rewards and benefits that Rushabh will receive from a job. This includes the salary, bonuses, and other perks that come with the position. While Rushabh may be willing to forgo salary for career growth at this stage in his career, compensation is still an essential consideration. Adequate compensation not only ensures that Rushabh's financial needs are met, but it also serves as recognition of his skills and contributions.\n\nWork-life balance, the second factor, refers to the equilibrium between Rushabh's personal and professional life. It is important for Rushabh to find a job that allows him to maintain a healthy lifestyle and have time for his hobbies and interests outside of work. Rushabh's passion for spending quality time in nature suggests that work-life balance is crucial for his overall well-being. Finding a job that provides flexibility, reasonable working hours, and supportive policies can contribute to Rushabh's job satisfaction and overall happiness.\n\nLastly, company mission refers to the purpose and values of the organization that Rushabh is considering working for. This factor assesses whether the company's goals and values align with Rushabh's own beliefs and interests. Since Rushabh is passionate about technology and enjoys tinkering with new products, working for a company that shares his enthusiasm for technology and innovation could provide a more fulfilling and meaningful work experience. A strong company mission can also provide Rushabh with a sense of purpose and motivation in his work.\n\nIn conclusion, when Rushabh is looking for jobs, it is crucial to consider factors such as compensation, work-life balance, and company mission. These factors can greatly impact his job satisfaction, career growth, and overall well-being. Finding a job that offers a fair compensation package, promotes work-life balance, and aligns with his interests and values can lead to a more fulfilling and rewarding career path for Rushabh.",
    "name": null,
    "function": null
  }
]
```


## Docs and support
Read how to start [here](www.docs.pontus.so).

Check out our [tutorials](www.docs.pontus.so/tutorials) for step-by-step guides.

Learn more about [Pontus](www.pontus.so) here

## Contributing
We love new contribution from small to big. Support this project by doing this.
1. Give us a star
2. Submit a [feature request](https://github.com/PontusAI/Pontus/issues/new?assignees=&labels=&projects=&template=feature_request.md&title=) or [bug issue](https://github.com/PontusAI/Pontus/issues/new?assignees=&labels=bug&projects=&template=bug_report.md&title=%5BBUG%5D)
3. Open a [PR](https://github.com/PontusAI/Pontus/compare)

## Philosophy

We want to create a world where building AI products with privacy embedded is easy and fast. If it isn't easy nor fast, privacy first software won't be adopted. Pontus wants to solve this. Make privacy first AI software easy

## Open Core Model
This repo is available under [MIT expat license](/LICENSE), except `ee` directory if applicable. We have open core model. Building in open makes safer and better software. We do intend to charge for enterprise features that aren't applicable to 90% of developers.
