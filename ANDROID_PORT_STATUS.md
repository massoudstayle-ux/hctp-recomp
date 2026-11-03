# Android Port Status

## Goal

Prepare a native Android ARM64 build of WWE SmackDown! Here Comes the Pain (USA, SLUS-20787). This is a port/recompilation target, not a PSP/PS2 emulator frontend.

## Safety rules

- Keep the upstream repository and the `main` branch unchanged.
- Never commit an ISO, ELF, IRX, extracted game assets, generated game C++, save data, or other copyrighted game-derived files.
- Keep all game-derived build inputs and outputs on the user's private build machine/storage.
- Work only on the `android-port` branch until changes are reviewed.

## Repository findings (2026-11-03)

- The fork exists and its default branch is `main`.
- The HCTP repository includes PS2Recomp as a Git submodule, pinned to commit `f2a246a6f11ef5203ce4d74763c2c4599ab4f895`.
- At that exact submodule commit, the top-level PS2Recomp CMake file has an `ANDROID` branch that disables the recompiler, analyzer, tests and studio, and builds the runtime only.
- The pinned PS2Recomp submodule also contains an `android/` Gradle project. Its README describes an Android runner APK build using Android SDK 34, NDK, Gradle 8.7+ and JDK 17. The app targets `arm64-v8a` and `x86_64`, and expects a guest ELF path supplied through `PS2X_DEFAULT_BOOT_ELF`.
- This is evidence that the generic PS2Recomp runtime has an Android runner path; it does **not** prove that this HCTP game configuration, HCTP-specific overrides, GS/VU renderer, audio, video, or input currently work on Android.
- The HCTP root README describes a native Windows build and a Direct3D 11 renderer. The changelog and older handoff notes also refer to a Vulkan/paraLLEl-GS path. This documentation mismatch must be resolved by inspecting the exact checked-in renderer and CMake source before selecting an Android graphics backend.
- The HCTP repository's Windows build scripts use Windows batch files and MSVC-specific settings. They cannot simply be run by Android Gradle.

## Next engineering steps

1. Inspect the pinned PS2Recomp Android runner source and identify how the Android app launches the runtime and obtains game files.
2. Inspect HCTP-specific CMake options, overrides, renderer selection, GS/VU implementation and IOP/audio integration.
3. Determine whether the existing renderer can target Android/Vulkan or whether a separate Android renderer is required.
4. Add only the smallest Android-specific build integration, preserving Windows build files and defaults.
5. Build an APK from source without any game data, then test the runtime with a privately supplied legal game dump.
6. Add touch controls and Android file selection only after the game boots and renders reliably.

## Current verification

- Repository access and branch creation were confirmed through GitHub.
- Source files and submodule metadata were inspected remotely.
- No APK has been built, no game has been launched, and no Android device test has been performed yet.
