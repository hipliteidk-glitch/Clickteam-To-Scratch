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
# patch 2: skip events entirely when fast_frames - this is the 25min hang fix
if 'SKIP_EVENTS_FAST' not in t2 or 'skipped_events' not in t2:
    # replace the loop start
    old_loop = '            for chunk in self._decoded_chunks(r):'
    if old_loop in t2:
        t2 = t2.replace(old_loop, '''            skipped_events = 0  # SKIP_EVENTS_FAST
            for chunk in self._decoded_chunks(r):
                if getattr(self, 'fast_frames', False) and chunk.id == FRAME_EVENTS:
                    skipped_events += 1
                    continue''')
    # also make _decoded_chunks skip decompressing events when fast
    # add early check in _read_frame header loop - events chunk size can be huge, skip decoding by not entering _decoded_chunks? We already skip after decode, but to save decrypt, make _decoded_chunks yield raw for events when fast
    # Patch _decoded_chunks method to early-return empty for events when fast
    if 'if getattr(self, \'fast_frames\'' not in t2:
        t2 = t2.replace(
            '    def _decoded_chunks(self, r: Reader) -> List[_Chunk]:',
            '    def _decoded_chunks(self, r: Reader) -> List[_Chunk]:\n        # fast_frames optimization - will be filtered later'
        )

p2.write_text(t2)
print("repo patch_oom.py updated")
