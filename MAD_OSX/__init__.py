bl_info = {
    "name": "MAD (Microphone Audio Driver)",
    "author": "F1dg3t",
    "version": (0, 1, 5),
    "blender": (4, 3, 2),
    "location": "View3D > Sidebar > MAD",
    "description": "Use your Microphone as an Animation Driver in Blender.",
    "category": "Animation",
}

import bpy
from . import main, operator, panel

def register():
    from .main import ensure_audio_level_property
    ensure_audio_level_property()
    operator.register()
    panel.register()

def unregister():
    panel.unregister()
    operator.unregister()
    main  # no explicit unregister needed