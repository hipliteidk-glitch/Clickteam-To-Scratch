import pathlib
p = pathlib.Path('cts2/scratch.py')
t = p.read_text()
# Replace assets dict to use streaming
old = '''    progress.phase("zip", total=1 + len(assets))
    progress.tick(0, step="writing project.json")
    zf = zipfile.ZipFile
    out = __import__("io").BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("project.json", json.dumps(project, separators=(",", ":")))
        zipped = 0
        for asset_id, data in assets.items():
            z.writestr(asset_id, data)
            zipped += 1
            progress.tick(zipped, step=f"packing asset {zipped}/{len(assets)}")
    report["assets"] = len(assets)
    report["sprites"] = len(sprites)
    return out.getvalue(), report'''
new = '''    progress.phase("zip", total=1 + len(assets))
    progress.tick(0, step="writing project.json")
    import io, gc
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
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
    report["assets"] = zipped
    report["sprites"] = len(sprites)
    return out.getvalue(), report'''
if old in t:
    t = t.replace(old, new)
    print("patched zip")
else:
    print("old block not found, trying fuzzy")
    # try direct edit
    t = t.replace('for asset_id, data in assets.items():', 'for asset_id, data in list(assets.items()):\n            assets[asset_id] = None')
    
# Also patch gamedata to drop raw after decode
p.write_text(t)
print("written")
