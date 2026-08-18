[app]

# (str) Title of your application
title = Tecnologia Store - Divulgador Shopee

# (str) Package name
package.name = tecnologiastore

# (str) Package domain (needed for android/ios packaging)
package.domain = com.tecnologiastore

# (str) Source code where main.py live
source.dir = .

# (list) List of source files to include
source.include_exts = py,png,jpg,kv,atlas,txt

# (str) Application version
version = 1.0.0

# (list) Application requirements
requirements = python3,kivy,requests,beautifulsoup4,pillow,pyjnius

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (str) Android permissions
android.permissions = INTERNET

# (str) Android API level
android.api = 35

# Automatically accept Android SDK licenses in GitHub Actions.
android.accept_sdk_license = True
android.minapi = 23

# (bool) Indicate if the application should not use fullscreen mode
# android.accept_sdk_license = False

[buildozer]

# (str) Directory where buildozer should store build artifacts
build_dir = .buildozer

# (str) Directory where to store the APK
bin_dir = bin

# (str) Log level
log_level = 2
