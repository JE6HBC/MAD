import bpy
import threading
import sounddevice as sd
import numpy as np
import time

def get_volume(indata):
    return np.linalg.norm(indata) * 10

def update_driver():
    while bpy.context.scene.audio_driver_props.running:
        try:
            props = bpy.context.scene.audio_driver_props
            obj = props.target_object
            if not obj or not props.data_path:
                continue

            volume = get_volume(props.stream.read(1024)[0])
            value = max(0.0, min(1.0, volume * props.volume_scale))

            # Update the driven property
            obj.path_resolve(props.data_path, False)[:] = props.default_value + value

            # Update the audio level bar in the UI
            bpy.context.scene["mad_audio_level"] = value

            time.sleep(props.update_interval)
        except Exception as e:
            print(f"Audio driver error: {e}")
            break

def start_audio_driver():
    props = bpy.context.scene.audio_driver_props
    if props.running:
        return

    try:
        device_index = int(props.mic_list.split(":")[0])
        props.stream = sd.InputStream(device=device_index, channels=1)
        props.stream.start()
        props.running = True
        threading.Thread(target=update_driver, daemon=True).start()
    except Exception as e:
        print(f"Failed to start audio driver: {e}")

def stop_audio_driver():
    props = bpy.context.scene.audio_driver_props
    if props.running:
        props.running = False
        if props.stream:
            props.stream.stop()
            props.stream.close()
        props.stream = None
