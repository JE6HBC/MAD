# MAD
Microphone Audio Driver: A driver assignment tool for Blender.


# Swittching to v0.1.5 on MacOS
## Uninstalling MAD (Microphone Audio Driver) on macOS

Follow these steps to fully remove the MAD addon from Blender.

---

## ✅ 1. Remove the Addon via Blender UI

1. Open **Blender**.
2. Go to **Edit → Preferences**.
3. Click the **Add-ons** tab.
4. In the search bar, type **MAD** or **Microphone Audio Driver**.
5. Click the **Remove** button next to the addon.
6. (Optional) Restart Blender to complete the removal.

---

## ✅ 2. Manually Delete Leftover Addon Files (if necessary)

1. Open **Finder**.
2. Press `Cmd + Shift + G` to open the **Go to Folder** dialog.
3. Enter the following path:
`~/Library/Application Support/Blender
`
4. Open the folder corresponding to your Blender version, for example: `4.3/scripts/addons`
5. Look for the `mad` folder (or the folder you used when installing MAD) and **delete it**.

---

## ✅ 3. (Optional) Remove Installed Python Dependencies

If you installed `sounddevice` or other Python packages for MAD and want to clean them up:

1. In Blender, open the **Scripting tab**.
2. In the Python console, run:

```python
import sys
print(sys.executable)
```
This will print the path to Blender’s internal Python.

3. Open Terminal and run:

`/path/to/blender/python/bin/python3.11 -m pip uninstall sounddevice
`

Replace /path/to/blender/python/bin/python3.11 with the path you got from step 2.

# ✅ Installing v0.1.5 OSX
MAD should now be fully uninstalled from your system. 

- Now go get the latest version from the [releases tab](https://github.com/F1dg3tXD/MAD/releases).
- Unzip the file and look for `install_mad_dependencies.py` and load that into Blender's scripting workspace and run it.
- Then install the addon from the zip file.
-  Close Blender and start it from `~Applications/Blender/Contents/MacOS/Blender`
