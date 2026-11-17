# SmarToken MCP

<!-- mcp-name: io.github.LiuXiyun/smartoken-mcp -->

[Create a SmarToken account](https://thesmartoken.com/register?utm_source=github&utm_medium=repository&utm_campaign=smartoken_mcp)

A stdio MCP server exposing `list_models` (public model metadata and pricing) and `chat_completion` (one text request). Model list and pricing can change; consult [the live model endpoint](https://thesmartoken.com/v1/models) and [pricing](https://thesmartoken.com/pricing).

The model lookup and one paid DeepSeek V4.1 Flash completion have been verified against the production API through the official Python MCP client. Other models and individual host applications should be verified in their own environments.

`chat_completion` sends the user's prompt to SmarToken and can incur charges. It uses the user's own `SMTOKEN_API_KEY`, bounded output, and does not automatically retry. A timeout or server error can leave the outcome unknown: check usage and request logs before retrying. Model output is untrusted content. Review your MCP client's approval settings; tool annotations do not guarantee approval prompts.

Install locally from this directory in a virtual environment:

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
export SMTOKEN_API_KEY='your-own-key'
smartoken-mcp
```

The process speaks MCP over stdio; configure your MCP client to launch the installed executable and provide the environment variable through its secure settings. Never commit a key or include it in a public configuration. The server does not expose balance or usage-account tools, does not support tools, images or structured output in model calls, and does not change the host application's underlying model.

The MCP server is a tool interface; installing it does not change your host application’s underlying model. See the [API quickstart](https://github.com/LiuXiyun/smartoken-api-quickstart) for direct Python, JavaScript and LiteLLM examples.
