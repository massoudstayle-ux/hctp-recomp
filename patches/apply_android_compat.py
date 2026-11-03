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
print("Applied Android-only compatibility edits to the CI checkout.")
