# BlockSmith AI

Describe a Minecraft idea, let a local Ollama model create a structured plan, review it, and build the files. Prompts and generation run locally; no cloud AI API key is used.

## First launch (Windows)

1. Launch BlockSmith AI.
2. In **Local AI setup**, choose a model (default: \`llama3.2:3b\`).
3. Click **Install / Set up local AI**.
4. If Ollama is missing, BlockSmith downloads the official Windows installer from Ollama and verifies its Authenticode signature before launching it. Complete the visible installer.
5. BlockSmith waits for Ollama, then downloads the selected model and displays pull progress.
6. Generate a plan, review it, and build.

The model download can be several GB and may take a while. Ollama itself and its model remain installed separately from BlockSmith. The app does not uninstall or silently replace existing software. Setup currently supports Windows; on other platforms install Ollama from https://ollama.com/download.

## Requirements

- Windows 10 22H2 or newer for Ollama's native Windows app.
- Internet access for initial installer/model downloads.
- Enough free disk space for Ollama and the selected model.
- Python 3.10+ only when running from source.

Official installer: https://ollama.com/download/OllamaSetup.exe

## Run from source

    python gui.py

## Platforms

- **Bedrock:** behavior/resource pack scaffolding, items, blocks, shaped recipes, and function files.
- **Java:** datapack/resource-pack scaffolding, functions, and recipes.
- Fabric/NeoForge mod generation is not enabled yet.

## Windows EXE

The Windows release workflow packages \`gui.py\` with PyInstaller. The EXE still downloads Ollama and the model on first setup; neither is bundled into the app. This keeps the app installer smaller and lets users choose their model.

## Notes

Minecraft schemas and Java pack formats vary by game version. Review generated files in Minecraft before distributing them. The local AI produces a structured plan; BlockSmith's compiler writes files and does not give the model arbitrary filesystem access.

## License

MIT
