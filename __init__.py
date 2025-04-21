bl_info = {
    "name": "Microphone Audio Driver",
    "author": "F1dg3t",
    "version": (0, 1, 0),
    "blender": (4, 3, 2),
    "location": "View3D > Sidebar > AudioRig",
    "description": "Use your Microphone as an Animation Driver in Blender.",
    "category": "Animation",
}

import bpy
from . import main, operator, panel

def register():
    main.register()
    operator.register()
    panel.register()

def unregister():
    panel.unregister()
    operator.unregister()
    main.unregister()