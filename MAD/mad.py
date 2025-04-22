bl_info = {
    "name": "MAD (Microphone Audio Rig Driver)",
    "blender": (4, 3, 2),
    "category": "Animation"
}

import bpy
import sounddevice as sd
import numpy as np

# Globals
current_volume = 0.0
stream = None
should_run = False

# UI Properties
def get_microphone_items(self, context):
    items = []
    for i, device in enumerate(sd.query_devices()):
        if device["max_input_channels"] > 0:
            label = f"{i}:{device['name']}"
            items.append((label, device["name"], ""))
    return items

class AudioRigSettings(bpy.types.PropertyGroup):
    mic_list: bpy.props.EnumProperty(
        name="Microphone",
        description="Select input device",
        items=get_microphone_items
    )
    object_name: bpy.props.StringProperty(name="Armature Object", default="SemiBot_ARM")
    bone_name: bpy.props.StringProperty(name="Bone Name", default="funny_hinge")
    volume_scale: bpy.props.FloatProperty(name="Volume to Rotation Scale", default=-2.0)
    update_interval: bpy.props.FloatProperty(name="Update Interval (s)", default=0.05, min=0.01, max=1.0)

# Audio callback
def audio_callback(indata, frames, time, status):
    global current_volume
    volume = np.linalg.norm(indata) / frames
    current_volume = min(volume, 1.0)  # clamp to 1.0 for safety

# Blender-safe update loop
def update_bone_rotation():
    global should_run
    if not should_run:
        return None

    s = bpy.context.scene.audio_rig_settings
    armature = bpy.data.objects.get(s.object_name)
    if not armature:
        return s.update_interval
    bone = armature.pose.bones.get(s.bone_name)
    if not bone:
        return s.update_interval

    # Apply volume to X rotation
    rot = list(bone.rotation_euler)
    rot[0] = current_volume * s.volume_scale
    bone.rotation_euler = rot

    return s.update_interval  # reschedule

# Operators
class AUDIO_OT_Start(bpy.types.Operator):
    bl_idname = "audio_driver.start"
    bl_label = "Start Audio Driver"

    def execute(self, context):
        global stream, should_run
        s = context.scene.audio_rig_settings
        should_run = True

        try:
            mic_index = int(s.mic_list.split(":")[0])
            stream = sd.InputStream(device=mic_index, channels=1, callback=audio_callback)
            stream.start()
        except Exception as e:
            self.report({'ERROR'}, f"Failed to start mic stream: {e}")
            return {'CANCELLED'}

        bpy.app.timers.register(update_bone_rotation)
        return {'FINISHED'}

class AUDIO_OT_Stop(bpy.types.Operator):
    bl_idname = "audio_driver.stop"
    bl_label = "Stop Audio Driver"

    def execute(self, context):
        global stream, should_run
        should_run = False
        if stream:
            stream.stop()
            stream.close()
            stream = None
        return {'FINISHED'}

# UI Panel
class AUDIO_PT_MicDriverPanel(bpy.types.Panel):
    bl_label = "MAD"
    bl_idname = "AUDIO_PT_mic_driver_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MAD"

    def draw(self, context):
        layout = self.layout
        s = context.scene.audio_rig_settings

        layout.prop(s, "mic_list")
        layout.prop(s, "object_name")
        layout.prop(s, "bone_name")
        layout.prop(s, "volume_scale")
        layout.prop(s, "update_interval")

        row = layout.row()
        row.operator("audio_driver.start", text="Start")
        row.operator("audio_driver.stop", text="Stop")

# Register
classes = (
    AudioRigSettings,
    AUDIO_OT_Start,
    AUDIO_OT_Stop,
    AUDIO_PT_MicDriverPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.audio_rig_settings = bpy.props.PointerProperty(type=AudioRigSettings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.audio_rig_settings

if __name__ == "__main__":
    register()
