import bpy
import sounddevice as sd

class AudioDriverProperties(bpy.types.PropertyGroup):
    device_index: bpy.props.IntProperty(name="Device Index", default=0)
    target_object: bpy.props.PointerProperty(name="Target Object", type=bpy.types.Object)
    data_path: bpy.props.StringProperty(name="Data Path", description="e.g. pose.bones[\"bone\"].rotation_euler[0]")
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
    bl_category = "AudioRig"

    def draw(self, context):
        layout = self.layout
        props = context.scene.audio_driver_props

        layout.prop(props, "device_index")
        layout.prop(props, "target_object")  # Enables eyedropper selection
        layout.prop(props, "data_path")
        layout.prop(props, "volume_scale")
        layout.prop(props, "default_value")
        layout.prop(props, "update_interval")

        row = layout.row()
        row.operator("audio_driver.start")
        row.operator("audio_driver.stop")

class AUDIO_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    def draw(self, context):
        self.layout.operator("audio_driver.install_libs", icon="CONSOLE")

def register():
    bpy.utils.register_class(AudioDriverProperties)
    bpy.utils.register_class(AUDIO_PT_Panel)
    bpy.utils.register_class(AUDIO_OT_Start)
    bpy.utils.register_class(AUDIO_OT_Stop)
    bpy.utils.register_class(AUDIO_OT_InstallLibs)
    bpy.utils.register_class(AUDIO_AddonPreferences)
    bpy.types.Scene.audio_driver_props = bpy.props.PointerProperty(type=AudioDriverProperties)

def unregister():
    bpy.utils.unregister_class(AudioDriverProperties)
    bpy.utils.unregister_class(AUDIO_PT_Panel)
    bpy.utils.unregister_class(AUDIO_OT_Start)
    bpy.utils.unregister_class(AUDIO_OT_Stop)
    bpy.utils.unregister_class(AUDIO_OT_InstallLibs)
    bpy.utils.unregister_class(AUDIO_AddonPreferences)
    del bpy.types.Scene.audio_driver_props
