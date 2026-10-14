import pathlib
p = pathlib.Path('cts2/scratch.py')
t = p.read_text()
if 'assets[asset_id] = None' not in t:
    t = t.replace('for asset_id, data in assets.items():', 'for asset_id, data in list(assets.items()):\n            assets[asset_id] = None  # free patched')
    p.write_text(t)

p2 = pathlib.Path('cts2/gamedata.py')
t2 = p2.read_text()
# patch 1: free raw
if 'raw_body = None' not in t2:
    t2 = t2.replace('img.png = encode_png', 'try:\n                    img.raw_body = None\n                except: pass\n                img.png = encode_png')

# patch 2: skip FRAME_EVENTS 13117 BEFORE decrypt in _decoded_chunks - fixes 25min hang
if 'fast_frames and cid == 13117' not in t2:
    t2 = t2.replace(
        '            raw = r.read(size)\n            chunk = _Chunk(cid, flags, size, raw)',
        '            raw = r.read(size)\n            if getattr(self, "fast_frames", False) and cid == 13117:\n                # skip huge event chunk without decrypt - perf fix\n                continue\n            chunk = _Chunk(cid, flags, size, raw)'
    )

p2.write_text(t2)
print("patched ok")
