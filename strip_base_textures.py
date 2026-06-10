#!/usr/bin/env python3
"""
Strip baseColorTexture from colorizable materials in the bouquet GLB.

Materials to modify (user-facing color pickers):
  - rosas_mat       → solid color (default red)
  - liston_mat      → solid color (default off-white)
  - papel_envoltura_mat → solid color (default kraft)
  - tallos_hojas_mat → KEEPS its texture (not colorizable in UI)

IMPORTANT: Only modifies material properties. Does NOT remove textures
from the glTF arrays — that would invalidate indices for other materials.
"""

import sys
from pathlib import Path

sys.path.insert(0, '/tmp/glbenv/lib/python3.12/site-packages')
from pygltflib import GLTF2

GLB_PATH = Path(__file__).parent / 'rose_bouquet_3d.glb'
BACKUP   = GLB_PATH.with_suffix('.glb.bak')

MATERIAL_CONFIG = {
    'rosas_mat':           [0.75, 0.14, 0.23, 1.0],  # ~#c0233a (sRGB)
    'liston_mat':          [0.96, 0.93, 0.91, 1.0],  # ~#f5ede8 (sRGB)
    'papel_envoltura_mat': [0.83, 0.72, 0.59, 1.0],  # ~#d4b896 (sRGB)
    # tallos_hojas_mat keeps its texture
}

def main():
    if not GLB_PATH.exists():
        print(f'❌ GLB not found: {GLB_PATH}')
        sys.exit(1)

    # Backup only if not already backed up
    if not BACKUP.exists():
        import shutil
        shutil.copy2(GLB_PATH, BACKUP)
        print(f'📦 Backup saved: {BACKUP.name}')
    else:
        print(f'📦 Backup exists: {BACKUP.name}')

    gltf = GLTF2().load(str(GLB_PATH))

    modified = 0
    for mat in gltf.materials:
        if mat.name not in MATERIAL_CONFIG:
            continue

        pbr = mat.pbrMetallicRoughness
        if not pbr:
            print(f'⚠  {mat.name}: no pbrMetallicRoughness, skipping')
            continue

        # Remember texture ref before nulling
        tex_ref = pbr.baseColorTexture

        # Remove the base color texture reference
        pbr.baseColorTexture = None

        # Set solid base color (sRGB values — Three.js converts to linear)
        pbr.baseColorFactor = MATERIAL_CONFIG[mat.name]

        modified += 1
        print(f'✅ {mat.name}: baseColorTexture removed (was idx {tex_ref.index if tex_ref else "?"}), baseColorFactor → {pbr.baseColorFactor}')

    print(f'\n📐 {modified} materials modified')

    # ── Save ──
    gltf.save(str(GLB_PATH))
    new_size = GLB_PATH.stat().st_size
    print(f'💾 GLB saved: {GLB_PATH.name} ({new_size / 1e6:.1f} MB)')

    # ── Verify (load fresh) ──
    verify = GLTF2().load(str(GLB_PATH))
    for mat in verify.materials:
        pbr = mat.pbrMetallicRoughness
        tex = pbr.baseColorTexture if pbr else None
        fac = pbr.baseColorFactor if pbr else None
        print(f'  Verify {mat.name}: baseColorTexture={tex is not None}, baseColorFactor={fac}')
        # Also verify tallos still has texture
        if mat.name not in MATERIAL_CONFIG:
            norm = mat.normalTexture
            orm  = pbr.metallicRoughnessTexture if pbr else None
            print(f'    ↳ normalTexture={norm.index if norm else "N/A"}, metallicRoughnessTexture={orm.index if orm else "N/A"}')

if __name__ == '__main__':
    main()
