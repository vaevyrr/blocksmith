# BlockSmith AI

BlockSmith turns a natural-language Minecraft idea into a structured pack plan using a local Ollama model, then deterministically builds the pack from that plan.

No cloud AI API key is required. The desktop GUI talks to Ollama on your own machine at http://127.0.0.1:11434.

## Flow

Prompt -> local AI JSON plan -> review -> build -> generated pack

Example request:

Make a magic sword called Starfall with 500 durability, 18 damage, a star projectile ability, and a 10 second cooldown.

The AI does not get direct filesystem access. It produces a structured plan and BlockSmith's Python compiler writes the files. That makes the project easier to inspect and keeps arbitrary model output away from the filesystem.

## Platforms

### Bedrock
Generates behavior/resource pack scaffolding, custom item/block definitions, shaped recipes and function files.

### Java
Generates a datapack + resource-pack scaffold with functions and recipes.

Fabric/NeoForge mod source generation is not enabled yet because those loaders need version-specific templates and mappings.

## Requirements

- Python 3.10+
- Ollama installed and running
- A local model installed in Ollama

Install Ollama from https://ollama.com/download

Example:

    ollama pull llama3.2

Start the local server if needed:

    ollama serve

Run BlockSmith:

    python gui.py

Then choose Bedrock or Java, choose your Ollama model, describe the pack, generate the plan, review it, and build it.

## Windows EXE

The existing GitHub Actions Windows GUI release workflow builds gui.py with PyInstaller, so the BlockSmith AI desktop app is the application being packaged.

The EXE only needs Ollama running on the computer that uses it. The model itself stays local.

## CLI

The original deterministic scaffold generator is still available:

    python blocksmith.py create copper_tools --output ./generated

## Important

Minecraft content schemas and Java pack formats vary by game version. BlockSmith intentionally generates conservative scaffolding rather than pretending every requested feature can be represented by one universal JSON schema. Review generated files against the Minecraft version you target.

## License

MIT
