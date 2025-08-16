bl_info = {
    "name": "MAD (Microphone Audio Driver)",
    "blender": (4, 2, 0),
    "category": "Animation"
}

import bpy
import sounddevice as sd
import numpy as np
import sys
import locale

# Globals
current_volume = 0.0
stream = None
should_run = False

# UI Properties
def get_microphone_items(self, context):
    items = []
    try:
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device["max_input_channels"] > 0:
                try:
                    # Handle device name encoding issues
                    device_name = device["name"]
                    if isinstance(device_name, bytes):
                        # Try to decode bytes to string
                        try:
                            device_name = device_name.decode('utf-8')
                        except UnicodeDecodeError:
                            try:
                                device_name = device_name.decode('shift_jis')
                            except UnicodeDecodeError:
                                try:
                                    device_name = device_name.decode('cp932')
                                except UnicodeDecodeError:
                                    device_name = f"Device {i}"
                    
                    # Clean up device name - remove null characters and control characters
                    device_name = ''.join(char for char in device_name if ord(char) >= 32 and ord(char) != 127)
                    device_name = device_name.strip()
                    
                    # Fallback name if cleaning resulted in empty string
                    if not device_name:
                        device_name = f"Audio Device {i}"
                    
                    # Truncate very long names
                    if len(device_name) > 50:
                        device_name = device_name[:47] + "..."
                    
                    label = f"{i}: {device_name}"
                    items.append((label, device_name, f"Input device {i}"))
                    
                except Exception as e:
                    print(f"[MAD] Error processing device {i}: {e}")
                    # Fallback item
                    items.append((f"{i}: Audio Device {i}", f"Audio Device {i}", f"Input device {i}"))
                    
    except Exception as e:
        print(f"[MAD] Error querying audio devices: {e}")
        # Add a fallback item
        items.append(("0: Default Audio Device", "Default Audio Device", "Default input device"))
    
    # Ensure we always have at least one item
    if not items:
        items.append(("0: No Audio Devices", "No Audio Devices", "No audio input devices found"))
        
    return items

class AudioRigSettings(bpy.types.PropertyGroup):
    mic_list: bpy.props.EnumProperty(
        name="Microphone",
        description="Select input device",
        items=get_microphone_items
    )
    object_ref: bpy.props.PointerProperty(
        name="Object",
        type=bpy.types.Object,
        description="Select the target object"
    )
    property_path: bpy.props.StringProperty(
        name="Property Path",
        description="Data path to drive (e.g. 'location.0', 'rotation_euler.2', 'scale[0]')",
        default="location.0"
    )
    bone_name: bpy.props.EnumProperty(
        name="Bone",
        description="Select bone to drive (if Armature)",
        items=lambda self, context: (
            [(b.name, b.name, "") for b in self.object_ref.pose.bones]
            if self.object_ref and self.object_ref.type == 'ARMATURE' and hasattr(self.object_ref, "pose") else []
        )
    )
    volume_scale: bpy.props.FloatProperty(name="Volume to Value Scale", default=1.0)
    update_interval: bpy.props.FloatProperty(name="Update Interval (s)", default=0.05, min=0.001, max=1.0)

# Audio callback
def audio_callback(indata, frames, time, status):
    global current_volume
    try:
        if status:
            print(f"[MAD] Audio stream status: {status}")
        volume = np.linalg.norm(indata) / frames
        current_volume = min(volume, 1.0)  # clamp to 1.0 for safety
    except Exception as e:
        print(f"[MAD] Error in audio callback: {e}")
        current_volume = 0.0

# Blender-safe update loop
def update_bone_rotation():
    global should_run
    if not should_run:
        return None

    s = bpy.context.scene.audio_rig_settings
    obj = s.object_ref
    # Update the UI audio level property
    bpy.context.scene["mad_audio_level"] = current_volume

    if not obj:
        return s.update_interval

    try:
        # If Armature and bone_name is set, drive the bone property
        if obj.type == 'ARMATURE' and s.bone_name:
            bone = obj.pose.bones.get(s.bone_name)
            if bone:
                # Default to driving rotation_euler.x, but allow property_path override
                path = s.property_path.split('.')
                target = bone
                for p in path[:-1]:
                    if '[' in p and ']' in p:
                        arr_name, idx = p[:-1].split('[')
                        target = getattr(target, arr_name)[int(idx)]
                    else:
                        target = getattr(target, p)
                last = path[-1]
                if '[' in last and ']' in last:
                    arr_name, idx = last[:-1].split('[')
                    arr = getattr(target, arr_name)
                    arr[int(idx)] = current_volume * s.volume_scale
                else:
                    setattr(target, last, current_volume * s.volume_scale)
            else:
                print("Bone not found")
        else:
            # Drive the property on the object itself
            path = s.property_path.split('.')
            target = obj
            for p in path[:-1]:
                if '[' in p and ']' in p:
                    arr_name, idx = p[:-1].split('[')
                    target = getattr(target, arr_name)[int(idx)]
                else:
                    target = getattr(target, p)
            last = path[-1]
            if '[' in last and ']' in last:
                arr_name, idx = last[:-1].split('[')
                arr = getattr(target, arr_name)
                arr[int(idx)] = current_volume * s.volume_scale
            else:
                setattr(target, last, current_volume * s.volume_scale)
    except Exception as e:
        print(f"Failed to set property: {e}")

    return s.update_interval  # reschedule

# Operators
class AUDIO_OT_RefreshDevices(bpy.types.Operator):
    bl_idname = "wm.audio_refresh_devices"
    bl_label = "Refresh Audio Devices"
    bl_description = "Refresh the list of available audio input devices"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            # Force refresh of device list
            context.scene.audio_rig_settings.mic_list = context.scene.audio_rig_settings.mic_list
            self.report({'INFO'}, "Audio device list refreshed")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to refresh devices: {e}")
        return {'FINISHED'}

class AUDIO_OT_Start(bpy.types.Operator):
    bl_idname = "wm.audio_driver_ui_start"
    bl_label = "Start MAD"
    bl_description = "Start MAD audio driver"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global stream, should_run
        s = context.scene.audio_rig_settings
        should_run = True

        try:
            # Extract device index more safely
            mic_string = s.mic_list
            if ":" in mic_string:
                try:
                    mic_index = int(mic_string.split(":")[0])
                except ValueError:
                    self.report({'ERROR'}, "Invalid microphone selection")
                    return {'CANCELLED'}
            else:
                mic_index = 0  # Default to first device
                
            print(f"[MAD] Attempting to start audio stream with device index: {mic_index}")
            
            stream = sd.InputStream(device=mic_index, channels=1, callback=audio_callback)
            stream.start()
            print(f"[MAD] Audio stream started successfully on device {mic_index}")
            
        except Exception as e:
            print(f"[MAD] Failed to start mic stream: {e}")
            self.report({'ERROR'}, f"Failed to start mic stream: {e}")
            return {'CANCELLED'}

        bpy.app.timers.register(update_bone_rotation)
        self.report({'INFO'}, "MAD audio driver started successfully")
        return {'FINISHED'}

class AUDIO_OT_Stop(bpy.types.Operator):
    bl_idname = "wm.audio_driver_ui_stop"
    bl_label = "Stop Audio Driver"
    bl_description = "Stop MAD audio driver"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global stream, should_run
        should_run = False
        
        if stream:
            try:
                stream.stop()
                stream.close()
                print("[MAD] Audio stream stopped successfully")
            except Exception as e:
                print(f"[MAD] Error stopping stream: {e}")
            finally:
                stream = None
                
        self.report({'INFO'}, "MAD audio driver stopped")
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
        global should_run, current_volume

        # Add device refresh button
        row = layout.row()
        row.prop(s, "mic_list")
        refresh_op = row.operator("wm.audio_refresh_devices", text="", icon='FILE_REFRESH')
        
        layout.prop(s, "object_ref")
        if s.object_ref and s.object_ref.type == 'ARMATURE':
            layout.prop(s, "bone_name")
        layout.prop(s, "property_path")
        layout.prop(s, "volume_scale")
        layout.prop(s, "update_interval")

        row = layout.row()
        row.operator("wm.audio_driver_ui_start", text="Start")
        row.operator("wm.audio_driver_ui_stop", text="Stop")

        # Indicator for active state and audio level
        if should_run:
            layout.label(text="Audio Driver: ACTIVE", icon='PLAY')
            # Draw a progress bar for the current audio level
            try:
                layout.prop(
                    context.scene, 
                    '["mad_audio_level"]', 
                    text="Audio Level", 
                    slider=True
                )
            except:
                layout.label(text=f"Audio Level: {current_volume:.2f}")
        else:
            layout.label(text="Audio Driver: Inactive", icon='PAUSE')

# --- Add a property to hold the audio level for UI updates ---
def update_audio_level(self, context):
    pass  # Dummy update, not used

def ensure_audio_level_property():
    if not hasattr(bpy.types.Scene, "mad_audio_level"):
        bpy.types.Scene.mad_audio_level = bpy.props.FloatProperty(
            name="Audio Level",
            description="Current audio input level",
            default=0.0,
            min=0.0,
            max=1.0,
            update=update_audio_level
        )

# Register
classes = (
    AudioRigSettings,
    AUDIO_OT_RefreshDevices,
    AUDIO_OT_Start,
    AUDIO_OT_Stop,
    AUDIO_PT_MicDriverPanel,
)

def register():
    ensure_audio_level_property()
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.audio_rig_settings = bpy.props.PointerProperty(type=AudioRigSettings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.audio_rig_settings
    if hasattr(bpy.types.Scene, "mad_audio_level"):
        del bpy.types.Scene.mad_audio_level

if __name__ == "__main__":
    register()
