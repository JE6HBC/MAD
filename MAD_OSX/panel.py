import bpy
import sounddevice as sd

def get_microphone_items(self, context):
    items = []
    for i, device in enumerate(sd.query_devices()):
        if device["max_input_channels"] > 0:
            label = f"{i}:{device['name']}"
            items.append((label, device['name'], ""))
    return items

class AudioDriverProperties(bpy.types.PropertyGroup):
    mic_list: bpy.props.EnumProperty(
        name="Microphone",
        description="Select input device",
        items=get_microphone_items
    )
    target_object: bpy.props.PointerProperty(
        name="Target Object",
        type=bpy.types.Object
    )
    data_path: bpy.props.StringProperty(
        name="Data Path",
        description="e.g. pose.bones[\"bone\"].rotation_euler[0]"
    )
    bone_name: bpy.props.EnumProperty(
        name="Bone",
        description="Select bone to drive (if Armature)",
        items=lambda self, context: (
            [(b.name, b.name, "") for b in self.target_object.pose.bones]
            if self.target_object and self.target_object.type == 'ARMATURE' and hasattr(self.target_object, "pose") else []
        )
    )
    volume_scale: bpy.props.FloatProperty(name="Volume Scale", default=1.0)
    default_value: bpy.props.FloatProperty(name="Default Value", default=0.0)
    update_interval: bpy.props.FloatProperty(name="Update Interval", default=0.05)
    running: bpy.props.BoolProperty(name="Running", default=False)
    stream: bpy.props.PointerProperty(name="Stream", type=bpy.types.ID)  # placeholder

class AUDIO_PT_Panel(bpy.types.Panel):
    bl_label = "MAD"
    bl_idname = "AUDIO_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "MAD"

    def draw(self, context):
        layout = self.layout
        props = context.scene.audio_driver_props

        layout.prop(props, "mic_list")
        layout.prop(props, "target_object")
        if props.target_object and props.target_object.type == 'ARMATURE':
            layout.prop(props, "bone_name")
        layout.prop(props, "data_path")
        layout.prop(props, "volume_scale")
        layout.prop(props, "default_value")
        layout.prop(props, "update_interval")

        row = layout.row()
        row.operator("wm.audio_driver_ui_start")
        row.operator("wm.audio_driver_ui_stop")

class AUDIO_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        self.layout.operator("audio_driver.install_libs", icon="CONSOLE")

def register():
    bpy.utils.register_class(AudioDriverProperties)
    bpy.utils.register_class(AUDIO_PT_Panel)
    bpy.utils.register_class(AUDIO_AddonPreferences)
    bpy.types.Scene.audio_driver_props = bpy.props.PointerProperty(type=AudioDriverProperties)

def unregister():
    bpy.utils.unregister_class(AudioDriverProperties)
    bpy.utils.unregister_class(AUDIO_PT_Panel)
    bpy.utils.unregister_class(AUDIO_AddonPreferences)
    del bpy.types.Scene.audio_driver_props