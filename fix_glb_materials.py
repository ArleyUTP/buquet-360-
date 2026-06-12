#!/usr/bin/env python3
"""Fix material names in tulipan and gerbera GLBs."""

import copy, sys
from pathlib import Path

sys.path.insert(0, '/tmp/glbenv/lib/python3.12/site-packages')
from pygltflib import GLTF2

def fix_glb_materials(glb_path, mesh_to_slot):
    """mesh_to_slot: dict mapping mesh_name -> slot ('flor','liston','papel','tallos')"""
    gltf = GLTF2().load(str(glb_path))

    slot_names = {
        'flor':   'flor_mat',
        'liston': 'liston_mat',
        'papel':  'papel_envoltura_mat',
        'tallos': 'tallos_hojas_mat',
    }

    # Get the original single shared material
    orig_mat = gltf.materials[0]

    # Create 4 materials (clones of original with different names)
    new_materials = []
    for slot, mat_name in slot_names.items():
        new_mat = copy.deepcopy(orig_mat)
        new_mat.name = mat_name
        new_materials.append(new_mat)

    gltf.materials = new_materials

    # Assign correct material index to each mesh
    mat_index = {slot: i for i, slot in enumerate(slot_names.keys())}

    for mesh in gltf.meshes:
        mesh_name = mesh.name
        if mesh_name in mesh_to_slot:
            slot = mesh_to_slot[mesh_name]
            idx = mat_index[slot]
            for prim in mesh.primitives:
                prim.material = idx
            print(f'  {mesh_name} → {slot_names[slot]} (idx {idx})')
        else:
            print(f'  ⚠ {mesh_name} NOT in mapping, keeping material 0')

    gltf.save(str(glb_path))
    print(f'✅ Saved {glb_path.name}')


ROOT = Path(__file__).parent

print('=== Tulipan ===')
fix_glb_materials(ROOT / 'tulipan_bouquet_3d.glb', {
    'Mesh_3.001': 'flor',    # 229K verts → flower head
    'Mesh_1.001': 'liston',  # 92K verts → ribbon (smallest)
    'Mesh_2.001': 'tallos',  # 533K verts → stems/leaves (most complex)
    'Mesh_0.001': 'papel',   # 466K verts → wrapping paper
})

print()
print('=== Gerberas ===')
fix_glb_materials(ROOT / 'gerberas_bouquet_3d.glb', {
    'Mesh_1': 'flor',    # 579K verts → flower (biggest, gerbera has tons of petals)
    'Mesh_0': 'liston',  # 53K verts → ribbon (smallest)
    'Mesh_3': 'papel',   # 356K verts → paper
    'Mesh_2': 'tallos',  # 367K verts → stems
})
