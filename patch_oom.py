import pathlib
print("applying aggressive OOM patch v4 - fixed indent")
p = pathlib.Path('cts2/scratch.py')
t = p.read_text()
if 'assets[asset_id] = None  # free patched' not in t:
    t = t.replace('for asset_id, data in assets.items():', 'for asset_id, data in list(assets.items()):\n            assets[asset_id] = None  # free patched')
    p.write_text(t)

p2 = pathlib.Path('cts2/gamedata.py')
t2 = p2.read_text()
# 1 free raw_body
if 'img.raw_body = None' not in t2:
    t2 = t2.replace('img.png = encode_png', 'try:\n                    img.raw_body = None\n                except: pass\n                img.png = encode_png')
# 2 skip events before decrypt
orig = '            raw = r.read(size)\n            chunk = _Chunk(cid, flags, size, raw)'
if orig in t2:
    t2 = t2.replace(orig, '            raw = r.read(size)\n            if getattr(self, "fast_frames", False) and cid == 13117:\n                del raw\n                continue\n            chunk = _Chunk(cid, flags, size, raw)\n            del raw')
# 3 fast skip set
if 'FAST_FRAMES_SKIP_SET' not in t2:
    t2 = t2.replace(
        '        try:\n            for chunk in self._decoded_chunks(r):',
        '        try:\n            FAST_FRAMES_SKIP_SET = {13117, 13111, 13113, 13114, 13115, 13116, 13122, 13124, 13125}\n            for chunk in self._decoded_chunks(r):\n                if getattr(self, "fast_frames", False) and chunk.id in FAST_FRAMES_SKIP_SET:\n                    try:\n                        chunk.raw = b""\n                    except:\n                        pass\n                    continue'
    )
# 4 gc per frame - correct indent (8 spaces)
if 'gc.collect() # patch frame' not in t2:
    t2 = t2.replace('        frame.items = list(self.objects.values())\n        self.frames.append(frame)', '        frame.items = list(self.objects.values())\n        self.frames.append(frame)\n        try:\n            import gc; gc.collect() # patch frame\n        except:\n            pass')
# 5 gc every 100
if 'gc every 100' not in t2:
    t2 = t2.replace('                img.png = encode_png', '                if (len(getattr(self, "images", [])) % 100) == 0:\n                    try:\n                        import gc; gc.collect() # gc every 100\n                    except: pass\n                img.png = encode_png')

p2.write_text(t2)
# verify compiles
import py_compile
py_compile.compile(str(p2), doraise=True)
print("patched gamedata.py v4 ok - compiles")
