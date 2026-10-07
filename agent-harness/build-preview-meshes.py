import gzip
import json
from pathlib import Path

import numpy as np
import trimesh


root = Path(__file__).resolve().parents[1]
directory = root / 'assets/models/so101/assets'
records = []
for source in sorted(directory.glob('*.stl')):
    mesh = trimesh.load(source, force='mesh')
    preview = mesh
    bounds_error = 0
    for ratio in [0.15, 0.3, 0.5, 0.75]:
        target = min(len(mesh.faces), max(500, round(len(mesh.faces) * ratio)))
        candidate = mesh.simplify_quadric_decimation(face_count=target)
        error = float(np.max(np.abs(mesh.bounds - candidate.bounds)))
        if error <= 0.0005:
            preview = candidate
            bounds_error = error
            break
    output = source.with_suffix('.preview.stl.gz')
    output.write_bytes(gzip.compress(preview.export(file_type='stl'), mtime=0))
    records.append({'file': source.name, 'original_faces': len(mesh.faces),
                    'preview_faces': len(preview.faces), 'bounds_error_m': bounds_error,
                    'bytes': output.stat().st_size})
(directory / 'preview-meshes.json').write_text(json.dumps(records, indent=2) + '\n')
print(json.dumps(records, indent=2))
