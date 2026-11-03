# Android Port Status

Last inspected: 2026-11-03

## Goal

Build a native Android ARM64 port of WWE SmackDown! Here Comes the Pain (USA, SLUS-20787). This is intended to be an Android application, not a PSP/PS2 emulator frontend.

## Repository safety

- Keep upstream `BigDaddyJRich/hctp-recomp` unchanged.
- Keep development on this fork's `android-port` branch; do not merge into `main` until reviewed.
- Never commit the user's ISO, extracted disc files, SLUS ELF, generated game C++, game assets, saves, or a game-containing APK.
- Game-derived inputs and binaries must stay in the user's private storage. CI may only build/test a runtime shell that contains no game data unless a private, authorized workflow is designed and reviewed separately.

## Confirmed repository state

- Fork: `massoudstayle-ux/hctp-recomp`
- Working branch: `android-port`
- HCTP repository submodule `PS2Recomp` is pinned to commit `f2a246a6f11ef5203ce4d74763c2c4599ab4f895`.
- The HCTP repo stores game-specific overrides in `overrides_hctp/`; the existing Windows handoff says these are copied into `PS2Recomp/ps2xRuntime/src/runner/` before compiling. The actual generated game code is also produced locally from the user's own disc.
- The Android Gradle project is inside the PS2Recomp submodule at `PS2Recomp/android/`. Its manifest uses Android NativeActivity and loads the `ps2EntryRunner` native library.
- Android build settings use SDK 34, NDK 28.2.13676358, CMake 3.22.1, minSdk 28, and ABI filters `arm64-v8a` and `x86_64`. The Gradle project does not include the Gradle wrapper scripts; its README says to generate a Gradle 8.9 wrapper or use Android Studio.
- The PS2Recomp top-level CMake file detects Android, disables the recompiler/analyzer/tests/studio, and builds the runtime. It uses raylib's Android platform backend and links Android system libraries.
- The runtime creates `ps2EntryRunner` as a shared library for Android and uses the configured `PS2X_DEFAULT_BOOT_ELF` path because Android NativeActivity does not provide a normal command-line argument.

## Important blockers found in source

1. **The HCTP native renderer is Windows-only.** Its documented native host uses Win32, Direct3D 11, XInput and XAudio2. Android cannot build this host as-is.
2. **The optional paraLLEl-GS/Vulkan GPU backend is currently guarded by `WIN32 AND NOT PS2X_IS_ANDROID` in `ps2xRuntime/CMakeLists.txt`.** Therefore the Android build does not compile `gs_gpu_parallel.cpp` or `gs_vulkan_present.cpp`; it selects `gs_gpu_none.cpp`. The comment in that file describes the no-paraLLEl-GS configuration as CPU-renderer-only. The existence of a Vulkan presenter source file does not mean it is enabled on Android.
3. **Touch controls are not implemented.** `ps2xRuntime/src/lib/ps2_android_runtime.cpp` currently contains a TODO for an on-screen joystick/button overlay and no implementation.
4. **Game-specific code is not automatically in the Android APK.** The Android build must compile the HCTP-specific overrides and locally generated runner sources. The current Android Gradle file only points CMake at the PS2Recomp submodule and sets a default ELF path; it does not perform the HCTP disc extraction/recompilation or copy the HCTP override files.
5. **Video support is reduced by default on Android.** PS2Recomp's CMake defaults FFmpeg off for Android, with MPEG video falling back to stub frames unless a compatible Android video path is added.

## Recommended implementation order

1. Add a CI smoke-build for the generic Android runtime only (no ISO, ELF, generated game code, or game assets). This validates the Android toolchain and APK packaging, not gameplay.
2. Create an Android-specific preparation/build script that copies only source override files from this repository into the submodule's runner source directory and accepts generated game code from a private local build step.
3. Keep the existing raylib Android host initially. Confirm the CPU GS path can boot HCTP before attempting GPU acceleration.
4. Add Android touch controls and controller mapping after the first successful boot.
5. Profile the CPU GS path. If it is too slow, design a real Android Vulkan GS backend; do not assume the existing Windows Vulkan presenter can be reused unchanged.
6. Restore video playback with an Android-compatible decoder only after the core game and audio work.
7. Build and test on a physical Android ARM64 device before calling the port playable.

## Verification record

- Confirmed: fork branch and repository files inspected remotely; Android Gradle files, Android manifest, PS2Recomp CMake files, renderer selection logic, and Android runtime stub inspected.
- Not done: no Android APK build, no device install, no game boot, no touch-input test, and no performance test.
- The user's ISO has not been accessed or inspected by this workflow.
