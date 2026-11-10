/* Portable validation shared by the native launcher and focused host tests.
 * Paths in the compiled manifest are ASCII, relative and '/' separated.
 */
#ifndef LEVEL2_PREVIEW_LAUNCHER_POLICY_H
#define LEVEL2_PREVIEW_LAUNCHER_POLICY_H
#include <stddef.h>
#include <string.h>
#include <wchar.h>

typedef struct { const wchar_t *path; const char *sha256; unsigned long long size; } PreviewFile;
typedef struct { const wchar_t *name; const wchar_t *value; } PreviewEnv;

static const PreviewEnv preview_reviewed_env[] = {
    {L"BUILDING313_FAMILY_OBSERVER_ENABLE", L"1"},
    {L"BUILDING313_FAMILY_CANVAS_ENABLE", L"1"},
    {L"BUILDING313_FAMILY_GROUND_ENABLE", L"1"},
    {L"BUILDING313_FAMILY_CLIFF_ENABLE", L"1"},
    {L"BUILDING313_FAMILY_CORNER_ENABLE", L"1"},
    {L"BUILDING313_TERRAIN_CONTINUITY_ENABLE", L"1"},
    {L"BUILDING313_FAMILY_STATIC340_ENABLE", L"1"},
    {L"LAMP272_FAMILY_CANVAS_ENABLE", L"1"},
    {L"GRAY325_FAMILY_CANVAS_ENABLE", L"1"},
    {L"LONGFACE573_FAMILY_CANVAS_ENABLE", L"1"},
    {L"TRIPLE275_FAMILY_CANVAS_ENABLE", L"1"},
    {L"BUILDING313_TERRAIN_BLEND_RETIRE_ENABLE", L"1"},
    {L"LAMP272_LATER_THREE_ENABLE", L"1"},
    {L"LAMP272_MIDDLE_PAIR_ENABLE", L"1"},
    {L"EMBER269_FAMILY_CANVAS_ENABLE", L"1"},
    {L"BUILDING313_V6_PHASE0", L"assets/hd/level2-family-v1/building/phase0.argb32le"},
    {L"BUILDING313_V6_PHASE1", L"assets/hd/level2-family-v1/building/phase1.argb32le"},
    {L"BUILDING313_V6_PHASE2", L"assets/hd/level2-family-v1/building/phase2.argb32le"},
    {L"LAMP272_FAMILY_ASSET_DIR", L"assets/hd/packs/asteroid1-ten-v1"},
    {L"GRAY325_FAMILY_ASSET_DIR", L"assets/hd/packs/asteroid1-ten-v1"},
    {L"TRIPLE275_FAMILY_ASSET_DIR", L"assets/hd/packs/asteroid1-ten-v1"},
    {L"EMBER269_FAMILY_ASSET_DIR", L"assets/hd/packs/asteroid1-ten-v1"},
    {L"LONGFACE573_FAMILY_ASSET_DIR", L"assets/hd/level2-family-v1/longface"},
    {L"BUILDING313_TERRAIN_FALLBACK_ENABLE", L"1"},
    {L"BUILDING313_PLAYER_FALLBACK_ENABLE", L"1"},
    {L"BUILDING313_TANK_FALLBACK_ENABLE", L"1"},
    {L"BUILDING313_FAMILY_HUD_ENABLE", L"1"},
    {L"LONGFACE573_LATER230240_ENABLE", L"1"},
    {L"ENEMY_SHOT_FAMILY_ENABLE", L"1"},
    {L"ENEMY_SHOT_FAMILY_ASSET_DIR", L"assets/hd/current-compat/tank-shell"},
    {L"TANK194_FAMILY_ENABLE", L"1"},
    {L"TANK194_FAMILY_ASSET_DIR", L"assets/hd/artwork/type15-eightheading-smooth-contour-v2/output"},
    {L"SMALLROCKS_ENABLE", L"1"},
    {L"SMALLROCKS_ASSET_DIR", L"assets/hd/packs/asteroid1-ten-v1"},
    {L"RANDOM_PROPS_ENABLE", L"1"},
    {L"RANDOM_PROPS_ASSET_DIR", L"assets/hd/packs/asteroid1-ten-v1"},
    {L"PLAYER_SHIP_FAMILY_ENABLE", L"1"},
    {L"PLAYER_SHIP_FAMILY_ASSET_DIR", L"assets/hd/current-compat/talon"},
    {L"LAMP272_LATER_SIXTEEN_ENABLE", L"1"},
    {L"EMBER269_LATER_FIVE_ENABLE", L"1"},
    {L"TRIPLE275_LATER_132_ENABLE", L"1"},
    {L"FORK284_ENABLE", L"1"},
    {L"FORK284_ASSET_DIR", L"assets/hd/packs/asteroid1-ten-v1"},
    {L"TURRET273_COMBAT_ENABLE", L"1"},
    {L"TURRET273_BODY_ASSET_DIR", L"assets/hd/packs/asteroid1-ten-v1"},
    {L"LINKED338_NORMAL_ENABLE", L"1"},
    {L"LINKED338_NORMAL_ASSET_DIR", L"assets/hd/packs/asteroid1-ten-v1"},
    {L"LINKED_PROP287288_ENABLE", L"1"},
    {L"LINKED_PROP287288_ASSET_DIR", L"assets/hd/packs/asteroid1-ten-v1"},
    {L"LATE_ACTORS_ENABLE", L"1"},
    {L"LATE_ACTORS_ASSET_DIR", L"assets/hd/packs/asteroid1-ten-v1"},
    {L"NORMAL270_ENABLE", L"1"},
    {L"NORMAL270_ASSET_DIR", L"assets/hd/packs/asteroid1-ten-v1"},
};
#define PREVIEW_REVIEWED_ENV_COUNT (sizeof(preview_reviewed_env) / sizeof(preview_reviewed_env[0]))

static int preview_ascii_lower(int c) { return c >= 'A' && c <= 'Z' ? c + 32 : c; }
static int preview_equal_ci(const wchar_t *a, const wchar_t *b)
{
    while (*a && *b) {
        if (preview_ascii_lower(*a++) != preview_ascii_lower(*b++)) return 0;
    }
    return *a == *b;
}
/* GetFinalPathNameByHandleW(VOLUME_NAME_GUID) identities only. Not user paths. */
static size_t preview_volume_root_length(const wchar_t *path)
{
    if (!path || wcslen(path) < 49 || wcsncmp(path, L"\\\\?\\Volume{", 11) ||
        path[47] != L'}' || path[48] != L'\\') return 0;
    for (size_t i = 0; i < 36; ++i) {
        wchar_t c = path[11 + i];
        if (i == 8 || i == 13 || i == 18 || i == 23) {
            if (c != L'-') return 0;
        } else if (!((c >= L'0' && c <= L'9') || (c >= L'a' && c <= L'f') ||
                     (c >= L'A' && c <= L'F'))) return 0;
    }
    return 49;
}
/* Win32 process CWD and this legacy engine's ordinary child-relative paths. */
static int preview_process_path_fits(size_t directory_length, size_t relative_length)
{
    return directory_length < 260 && relative_length < 260 &&
        (!relative_length || directory_length + 1 + relative_length < 260);
}
static int preview_reserved_component(const wchar_t *s, size_t n)
{
    wchar_t word[5]; size_t i = 0;
    while (i < n && s[i] != L'.' && i < 4) {
        word[i] = (wchar_t)preview_ascii_lower(s[i]); ++i;
    }
    word[i] = 0;
    if (i < n && s[i] != L'.') return 0;
    return !wcscmp(word, L"con") || !wcscmp(word, L"prn") ||
        !wcscmp(word, L"aux") || !wcscmp(word, L"nul") ||
        (i == 4 && word[3] >= L'1' && word[3] <= L'9' &&
         ((!wcsncmp(word, L"com", 3)) || (!wcsncmp(word, L"lpt", 3))));
}
static int preview_relative_path(const wchar_t *s, int flat)
{
    const wchar_t *start = s, *component = s;
    if (!s || !*s) return 0;
    for (;;) {
        wchar_t c = *s;
        if (!c || c == L'/') {
            size_t n = (size_t)(s - component);
            if (!n || (n == 1 && *component == L'.') ||
                (n == 2 && component[0] == L'.' && component[1] == L'.') ||
                component[n - 1] == L'.' || component[n - 1] == L' ' ||
                preview_reserved_component(component, n)) return 0;
            if (!c) return (s - start) < 512;
            if (flat) return 0;
            component = s + 1;
        } else if (c < 33 || c > 126 || c == L'\\' || c == L':' || c == L'<' ||
                   c == L'>' || c == L'"' || c == L'|' || c == L'?' || c == L'*') return 0;
        ++s;
    }
}
static int preview_digest_valid(const char *s)
{
    size_t i;
    if (!s || strlen(s) != 64) return 0;
    for (i = 0; i < 64; ++i)
        if (!((s[i] >= '0' && s[i] <= '9') || (s[i] >= 'a' && s[i] <= 'f'))) return 0;
    return 1;
}
static int preview_original_path(const wchar_t *s)
{
    static const wchar_t *const exts[] = {L".dat", L".lvl", L".hdt", L".cdt", L".snd", L".mus", L".pic", L".shp", L".anm"};
    const wchar_t *dot; size_t i;
    if (!preview_relative_path(s, 1) || !(dot = wcsrchr(s, L'.'))) return 0;
    for (i = 0; i < sizeof(exts) / sizeof(exts[0]); ++i)
        if (preview_equal_ci(dot, exts[i])) return 1;
    return 0;
}
static int preview_payload_path(const wchar_t *s, const wchar_t *exe)
{
    if (!preview_relative_path(s, 0)) return 0;
    return !wcscmp(s, exe) || !wcscmp(s, L"bin/SDL2.dll") || !wcscmp(s, L"bin/SDL2_net.dll") ||
        (!wcsncmp(s, L"assets/hd/", 10) && s[10]);
}
static int preview_environment_valid(const PreviewEnv *env, size_t count)
{
    size_t i, j;
    if (!env || count != PREVIEW_REVIEWED_ENV_COUNT) return 0;
    for (i = 0; i < count; ++i) {
        int found = 0;
        if (!env[i].name || !env[i].value) return 0;
        for (j = 0; j < i; ++j)
            if (preview_equal_ci(env[i].name, env[j].name)) return 0;
        for (j = 0; j < PREVIEW_REVIEWED_ENV_COUNT; ++j)
            if (!wcscmp(env[i].name, preview_reviewed_env[j].name) &&
                !wcscmp(env[i].value, preview_reviewed_env[j].value)) { found = 1; break; }
        if (!found) return 0;
    }
    return 1;
}
static int preview_inventory_valid(const PreviewFile *files, size_t count, int originals, const wchar_t *exe)
{
    size_t i, j;
    int game = 0, sdl = 0, net = 0;
    if (!files || !count || count > 4096 || wcscmp(exe, L"bin/opentyrian-level2.exe")) return 0;
    for (i = 0; i < count; ++i) {
        if (!preview_digest_valid(files[i].sha256) || !files[i].size ||
            !(originals ? preview_original_path(files[i].path) : preview_payload_path(files[i].path, exe))) return 0;
        for (j = 0; j < i; ++j) {
            size_t n = wcslen(files[j].path), m = wcslen(files[i].path), k;
            if (preview_equal_ci(files[i].path, files[j].path)) return 0;
            /* A listed file must not also be another file's ancestor. */
            for (k = 0; k < n && k < m; ++k)
                if (preview_ascii_lower(files[i].path[k]) != preview_ascii_lower(files[j].path[k])) break;
            if ((k == n && m > n && files[i].path[n] == L'/') ||
                (k == m && n > m && files[j].path[m] == L'/')) return 0;
        }
        game += !wcscmp(files[i].path, exe);
        sdl += !wcscmp(files[i].path, L"bin/SDL2.dll");
        net += !wcscmp(files[i].path, L"bin/SDL2_net.dll");
    }
    if (!originals) return game == 1 && sdl == 1 && net == 1;
    { static const wchar_t *const required[] = {L"tyrian1.lvl", L"tyrian.hdt", L"tyrian.cdt", L"tyrian.snd", L"voices.snd", L"music.mus", L"palette.dat"};
      for (i = 0; i < sizeof(required) / sizeof(required[0]); ++i) {
          int found = 0;
          for (j = 0; j < count; ++j) if (!wcscmp(files[j].path, required[i])) { found = 1; break; }
          if (!found) return 0;
      }
    }
    return 1;
}
#endif
