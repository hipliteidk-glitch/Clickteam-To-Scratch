import pathlib, re
p = pathlib.Path('cts2/scratch.py')
t = p.read_text()
# --- ensure zip streams and frees ---
# Replace BytesIO zip with direct file write if build_project is changed to use tempfile, but keep simple free logic
old = '''    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("project.json", json.dumps(project, separators=(",", ":")))
        zipped = 0
        for asset_id, data in list(assets.items()):
            z.writestr(asset_id, data)
            assets[asset_id] = None  # free
            zipped += 1
            if zipped % 50 == 0:
                gc.collect()
            progress.tick(zipped, step=f"packing asset {zipped}/{len(assets)}")
    # cleanup
    assets.clear()
    gc.collect()
    report["assets"] = zipped'''

# Ensure we have gc collect version (already applied, ensure list())
if 'assets[asset_id] = None' not in t:
    t = t.replace('for asset_id, data in assets.items():', 'for asset_id, data in list(assets.items()):\n            assets[asset_id] = None  # free patched')
    print("patched assets loop")
else:
    print("zip already patched")

p.write_text(t)

# Patch gamedata to not keep raw body
p2 = pathlib.Path('cts2/gamedata.py')
t2 = p2.read_text()
if 'raw_body = None' not in t2:
    # after decoding image, free raw
    t2 = t2.replace('img.png = encode_png', 'try:\n                    # free raw to save RAM\n                    img.raw_body = None\n                except: pass\n                img.png = encode_png')
    print("patched gamedata free")
    p2.write_text(t2)
else:
    print("gamedata already")

print("done")
