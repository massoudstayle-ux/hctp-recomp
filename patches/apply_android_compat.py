from pathlib import Path

root = Path("PS2Recomp")
chain = root / "ps2xRuntime/src/lib/ps2_chain.cpp"
movie = root / "ps2xRuntime/src/lib/hctp_native_movie.cpp"

s = chain.read_text()
old = "    const uint32_t ra = ctx ? static_cast<uint32_t>(ctx->r[31].m128i_u32[0]) : 0u;"
new = """    uint32_t ra = 0u;
    // Read the low 32 bits portably; m128i_u32 is not available on Android ARM64.
    if (ctx)
        std::memcpy(&ra, &ctx->r[31], sizeof(ra));"""
if old not in s:
    raise SystemExit("Expected ARM64-incompatible register access was not found")
if "#include <cstring>" not in s:
    lines = s.splitlines()
    insert_at = next((i for i, line in enumerate(lines) if line.startswith("#include")), 0)
    lines.insert(insert_at, "#include <cstring>")
    s = "\n".join(lines) + "\n"
s = s.replace(old, new, 1)
chain.write_text(s)

s = movie.read_text()
marker = '#include "hctp_native_movie.h"'
if s.count(marker) != 1:
    raise SystemExit("Unexpected movie source header layout")
if "#if PS2X_HAS_FFMPEG" in s:
    raise SystemExit("Movie source already has FFmpeg guard")
s = s.replace(marker, marker + "\n#if PS2X_HAS_FFMPEG", 1)
stubs = """
#else
// Android runtime build without bundled FFmpeg: movies remain unavailable.
extern "C" bool hctpMovieOpen(int, const char *, int, bool) { return false; }
extern "C" void hctpMovieStop(int) {}
extern "C" void hctpMoviePause(int, bool) {}
extern "C" bool hctpMovieActive(int) { return false; }
extern "C" int hctpMovieStatus(int) { return 0; }
extern "C" void hctpMovieSetVolume(int, float) {}
extern "C" bool hctpMovieFrame(int, uint8_t *, int, int) { return false; }
#endif
"""
s = s.rstrip() + "\n" + stubs
movie.write_text(s)

# The VU1 interpreter uses the Windows _BitScanForward intrinsic only to find
# the first set bit in a 32-bit register mask. Provide the same behavior on Android.
vu = root / "ps2xRuntime/src/lib/vu/ps2_vu1_core.cpp"
s = vu.read_text()
old = "#include <intrin.h>"
new = """#if defined(__ANDROID__)
static inline unsigned char _BitScanForward(unsigned long *index, unsigned long mask)
{
    if (mask == 0ul)
        return 0;
    *index = static_cast<unsigned long>(__builtin_ctzl(mask));
    return 1;
}
#else
#include <intrin.h>
#endif"""
if old not in s:
    raise SystemExit("Expected intrin.h include was not found")
s = s.replace(old, new, 1)
vu.write_text(s)

# Use the bundled sse2neon compatibility header on ARM64 instead of Clang's
# x86-only xmmintrin.h. The build already defines USE_SSE2NEON on Android.
native_vu = root / "ps2xRuntime/src/lib/hctp_native_vu1.cpp"
s = native_vu.read_text()
old = "#include <xmmintrin.h>"
new = """#if defined(__ANDROID__) && defined(USE_SSE2NEON)
#include <sse2neon.h>
#else
#include <xmmintrin.h>
#endif"""
if old not in s:
    raise SystemExit("Expected xmmintrin.h include was not found")
s = s.replace(old, new, 1)
native_vu.write_text(s)

print("Applied Android-only compatibility edits to the CI checkout.")
