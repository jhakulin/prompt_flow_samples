## Tracing function calls

In this sample, we will show how to trace OpenAI Function calling using promptflow.

### Prerequisites:

- Python 3.10
- Conda
- weatherAPI key (**WEATHER_API_KEY**). Sign up for the free account at https://www.weatherapi.com/ -- that will give you 1 Mio requests per month
- OpenAI API resouce (**OPENAI_API_BASE**, **OPENAI_API_KEY**) -- I recommend creating it in Sweden central. 
- Deployments of OpenAI models:
    - deployment of `gpt-35-turbo-1106` (**OPENAI_CHAT_MODEL**) or another model that supports functions
    - deployment of `dalle3` (**OPENAI_DALLE_MODEL**) 

Copy `.env.sample` to `.env` and fill in the values:

```bash
OPENAI_API_TYPE="azure"
OPENAI_API_VERSION="2023-12-01-preview"
OPENAI_API_BASE=https://***.openai.azure.com/
OPENAI_API_KEY=***
OPENAI_CHAT_MODEL=gpt-4-1106-preview
OPENAI_DALLE_MODEL=dalle3
WEATHER_API_KEY=***
WEATHER_API_BASE="http://api.weatherapi.com/v1/current.json?"
```

### Install dependencies

```bash
conda env create -f environment.yml
conda activate designer
```

### Turn on experimental promptflow features

To enable tracing, you need to turn on the internal features of promptflow. This can be done by setting the `enable_internal_features` to `true` in the promptflow configuration.

```bash
pf config set enable_internal_features=true
```
(see [here](https://github.com/microsoft/promptflow/blob/clwan/eager-mode-sample/examples/tutorials/trace/README.md) for more information)


### Run the sample

```bash
cd src
chainlit run app.py
```

The output will be similar to this (port numbers might differ):

```bash
INFO:waitress:Serving on http://127.0.0.1:61802
Start Prompt Flow Service on 61802, version: 1.7.0
You can view the traces from local: http://localhost:61802/v1.0/ui/traces/
2024-03-30 11:15:14 - Request URL: 'https://dc.services.visualstudio.com/v2.1/track'
Request method: 'POST'
Request headers:
    'Content-Type': 'application/json'
    'Content-Length': '2020'
    'Accept': 'application/json'
    'x-ms-client-request-id': '54367e9e-ee7e-11ee-a580-0e3a2dccaa78'
    'User-Agent': 'azsdk-python-azuremonitorclient/unknown Python/3.10.4 (macOS-10.16-x86_64-i386-64bit)'
A body is sent with the request
2024-03-30 11:15:14 - Your app is available at http://localhost:8000
```

Open two browser tabs, one to `http://localhost:8000` and one to `http://localhost:61802/v1.0/ui/traces/`
