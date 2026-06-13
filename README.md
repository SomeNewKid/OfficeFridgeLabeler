# Office Fridge Labeler

Office Fridge Labeler is a small Python command-line sample for exploring local
Model Context Protocol resources and tools with the OpenAI Agents SDK. It
accepts a short natural-language description of food in a shared office fridge
and prints a formatted label.

> [!WARNING]
> This is an experimental project and should not be considered production-ready.

The project is intentionally small so the MCP workflow stays visible. The CLI
starts a local MCP server over stdio, reads an office fridge policy resource,
and asks an agent to call an MCP tool that generates the final label text.

## What It Does

The CLI accepts a request such as:

```powershell
.\.venv\Scripts\python.exe -m office_fridge_labeler "This is spicy chicken curry made by Priya"
```

The agent then:

- starts the local pretend office MCP server
- reads the `fridge://shared-food-rules` resource for policy context
- extracts the food item, owner, and optional expiry or removal date from the
  user's request
- calls the MCP tool named `generate_fridge_label`
- prints only the label text returned by the tool

The MCP tool applies simple local rules to choose whether the item is private,
communal, or mysterious, infer a removal date when none is supplied, and add
warnings for foods such as spicy, fishy, or nut-containing items.

## Requirements

- Python 3.11.
- PowerShell on Windows.
- An `OPENAI_API_KEY` environment variable for OpenAI model calls.

## Setup

Create the virtual environment and install the project with development
dependencies:

```powershell
.\scripts\setup-dev.ps1
```

The setup script expects Python 3.11 at the path configured in
`scripts\setup-dev.ps1`.

## Running

Run the labeler from the repository root:

```powershell
.\.venv\Scripts\python.exe -m office_fridge_labeler "This is a shared birthday cake for Susan"
```

Example output:

```text
COMMUNAL FOOD
Item: birthday cake
Owner: Susan
Remove after: 2026-06-16
Note: Take one piece. Leave civilisation intact.
```

Dates and wording can vary depending on the request, the current date, and the
agent's extraction of the food item and owner.

## Development Checks

Run formatting, linting, type checking, and tests:

```powershell
.\scripts\check.ps1
```

This runs:

- `ruff format .`
- `ruff check .`
- `pyright`
- `pytest`

## Project Structure

```text
src/office_fridge_labeler/
  __main__.py    Package entry point for python -m office_fridge_labeler
  cli.py         Agent setup, MCP client setup, and command-line entry point
  mcp_server.py  Local MCP resource and label-generation tool

tests/
  test_smoke.py

scripts/
  setup-dev.ps1
  check.ps1
```

## Notes

This project is an MCP learning exercise, not a real office facilities system.
The fridge domain exists to make the resource-and-tool pattern easy to see: the
resource supplies policy context, and the tool supplies deterministic local
behavior.

The MCP server is started locally with stdio transport by the CLI. Agent
behavior and final wording can vary between runs because request extraction is
model-driven. OpenAI API calls may incur usage costs.

## Third-Party Notices

This project has direct runtime dependencies on third-party Python packages,
including `openai-agents` (MIT) and `mcp` (MIT). See each package's PyPI
license metadata for full license and notice terms.

## License

GNU General Public License v3.0. See the `LICENSE` file for details.
