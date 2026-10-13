import pathlib
p=pathlib.Path('converters/ctf_to_sb3.py')
t=p.read_text()
# force ultra low-mem: write images immediately, never keep full list
t=t.replace('fast_frames = os.environ.get("CTS2_FAST_FRAMES") == "1"', 'fast_frames = True')
t=t.replace('if fast_frames:', 'if True:')
# add streaming
if 'STREAM_IMAGES' not in t:
    t=t.replace('fast_frames = True', 'fast_frames = True\nSTREAM_IMAGES=True')
# ensure we drop raw_body always
if 'del img["raw_body"]' not in t:
    t=t.replace('img["md5ext"] = f"{h}.{ext}"', 'img["md5ext"] = f"{h}.{ext}"\n                    if fast_frames:\n                        del img["raw_body"]')
print('patched')
