# SmarToken MCP

<!-- mcp-name: io.github.LiuXiyun/smartoken-mcp -->

[Create a SmarToken account](https://thesmartoken.com/register?utm_source=github&utm_medium=repository&utm_campaign=smartoken_mcp)

A stdio MCP server exposing `list_models` (public model metadata and pricing) and `chat_completion` (one text request). Model list and pricing can change; consult [the live model endpoint](https://thesmartoken.com/v1/models) and [pricing](https://thesmartoken.com/pricing).

The model lookup and one paid DeepSeek V4.1 Flash completion have been verified against the production API through the official Python MCP client. Other models and individual host applications should be verified in their own environments.

`chat_completion` sends the user's prompt to SmarToken and can incur charges. It uses the user's own `SMTOKEN_API_KEY`, bounded output, and does not automatically retry. A timeout or server error can leave the outcome unknown: check usage and request logs before retrying. Model output is untrusted content. Review your MCP client's approval settings; tool annotations do not guarantee approval prompts.

## Get started

1. [Create an account or sign in](https://thesmartoken.com/register). Registration does not include free API credit.
2. Open [Billing](https://thesmartoken.com/dashboard/billing) and add prepaid credit before making billable calls. Check the payment amount before confirming.
3. Open [API keys](https://thesmartoken.com/dashboard/api-keys) and create a key. Copy the full key when shown; existing keys cannot be revealed again. Set an appropriate budget and model scope.
4. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and configure your MCP client below. Use your own key and keep it private.

### Cursor and Claude Desktop configuration

Use the following entry in Cursor's global `~/.cursor/mcp.json` or a project's `.cursor/mcp.json`. For Claude Desktop, use `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\\Claude\\claude_desktop_config.json` on Windows. Merge the entry into an existing `mcpServers` object rather than replacing other servers. See [Cursor's MCP guide](https://docs.cursor.com/context/model-context-protocol) and the [MCP SDK Claude guide](https://py.sdk.modelcontextprotocol.io/get-started/real-host/).

```json
{
  "mcpServers": {
    "smartoken": {
      "command": "/absolute/path/to/uvx",
      "args": ["smartoken-mcp==0.1.3"],
      "env": { "SMTOKEN_API_KEY": "YOUR_SMARTOKEN_KEY" }
    }
  }
}
```

Replace the executable path with the result of `which uvx` on macOS/Linux or `where uvx` on Windows, and replace the placeholder with your SmarToken key. Windows paths in JSON need escaped backslashes. These JSON files contain a secret: restrict file access, do not commit or share them, and prefer your client's secure secret storage if available. Restart the client and confirm that `list_models` and `chat_completion` appear. `list_models` does not require a key or charge; `chat_completion` sends the prompt and can incur charges. Ask the client to list SmarToken models first; then explicitly request a short completion with an available text model.

The server reports links when a key is missing or invalid. For HTTP 402 it distinguishes insufficient balance from a key budget/model-scope limit when the API identifies the cause; otherwise check both Billing and API keys. Errors from network failures or HTTP 5xx can leave the request outcome unknown: inspect usage before retrying. Do not automatically retry.

This is a local stdio server, not a remote URL. It does not change the host application's underlying model and does not provide balance or account-management tools. It does not support tool calls, images or structured output in model requests. Client approval settings determine whether tool use prompts for confirmation.

The MCP server is a tool interface; installing it does not change your host application’s underlying model. See the [API quickstart](https://github.com/LiuXiyun/smartoken-api-quickstart) for direct Python, JavaScript and LiteLLM examples.
