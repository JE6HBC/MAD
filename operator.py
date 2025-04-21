import bpy
import subprocess
import sys

class AUDIO_OT_Start(bpy.types.Operator):
    bl_idname = "audio_driver.start"
    bl_label = "Start Audio Driver"

    def execute(self, context):
        from .main import start_audio_driver
        start_audio_driver()
        return {'FINISHED'}

class AUDIO_OT_Stop(bpy.types.Operator):
    bl_idname = "audio_driver.stop"
    bl_label = "Stop Audio Driver"

    def execute(self, context):
        from .main import stop_audio_driver
        stop_audio_driver()
        return {'FINISHED'}

class AUDIO_OT_InstallLibs(bpy.types.Operator):
    bl_idname = "audio_driver.install_libs"
    bl_label = "Install sounddevice"

    def execute(self, context):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "sounddevice"])
        return {'FINISHED'}
