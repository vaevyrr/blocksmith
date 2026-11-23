# BlockSmith

A small generator for starter Minecraft Bedrock add-on structures. BlockSmith creates a behavior pack and resource pack folder with matching manifests, UUIDs, a sample custom item, and a sample custom block definition.

It generates a **starting point**, not a finished in-game add-on. Bedrock's content schema changes over time; validate generated packs against the game version you target.

## Requirements

Python 3.10+. No external dependencies.

## Generate

```bash
python blocksmith.py create copper_tools --output ./generated
```

This creates:

- `copper_tools_BP/manifest.json`
- `copper_tools_BP/items/sample_item.json`
- `copper_tools_BP/blocks/sample_block.json`
- `copper_tools_RP/manifest.json`
- `copper_tools_RP/textures/item_texture.json`
- `copper_tools_RP/textures/terrain_texture.json`
- `README.txt` with the generated pack locations

The sample definitions are deliberately minimal and may need adjustments for the exact Bedrock release and experiment settings in use.

## Safety

The generator writes only beneath the output directory and refuses to overwrite an existing project directory unless `--force` is supplied.

## Tests

```bash
python -m unittest discover -s tests -v
```

## License

MIT
