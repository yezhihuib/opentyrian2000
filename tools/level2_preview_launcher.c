/* Native, per-launch isolated Windows x64 level-2 preview bootstrap.
 * Compile against a generated, embedded manifest. See the contract in
 * docs/level2-preview-native-launcher.md. No shell, scripting runtime, network,
 * downloaded code, security-policy changes, imported profiles or synthetic input.
 */
#ifndef UNICODE
#define UNICODE
#endif
#ifndef _UNICODE
#define _UNICODE
#endif
#ifndef _WIN32_WINNT
#define _WIN32_WINNT 0x0601
#endif
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <bcrypt.h>
#include <shlobj.h>
#include <shellapi.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <wchar.h>
#include "level2_preview_launcher_policy.h"
#ifndef PREVIEW_MANIFEST_HEADER
#error Supply PREVIEW_MANIFEST_HEADER containing the verified payload inventory
#endif
#include PREVIEW_MANIFEST_HEADER
#ifndef PREVIEW_SOURCE_COMMIT
#define PREVIEW_SOURCE_COMMIT L"not supplied (see bundle build receipt)"
#endif

#define PATH_CAP 32768
#define SESSION_NAME_CHARS 49
#define ARRAY_COUNT(a) (sizeof(a) / sizeof((a)[0]))
typedef struct { wchar_t *path; HANDLE handle; } LockedPath;
typedef struct {
    wchar_t error[2048];
    wchar_t *root, *data, *session;
    wchar_t *root_identity, *data_identity, *process_session;
    LockedPath *locks;
    size_t lock_count, lock_capacity;
    BCRYPT_ALG_HANDLE sha;
    HANDLE journal, out, err, input;
    int check_only, scale;
} App;

static int failure(App *app, const wchar_t *format, ...)
{
    va_list args;
    va_start(args, format);
    vswprintf(app->error, ARRAY_COUNT(app->error), format, args);
    va_end(args);
    app->error[ARRAY_COUNT(app->error) - 1] = 0;
    return 0;
}
static int win_failure(App *app, const wchar_t *action, const wchar_t *path)
{
    DWORD code = GetLastError();
    wchar_t detail[512] = L"";
    FormatMessageW(FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
                   NULL, code, 0, detail, ARRAY_COUNT(detail), NULL);
    return failure(app, L"%ls failed (Windows error %lu).\n%ls\n%ls", action, code, path, detail);
}
static void *allocate(App *app, size_t bytes)
{
    void *p = calloc(1, bytes);
    if (!p) failure(app, L"Not enough memory. No game was started.");
    return p;
}
static wchar_t *duplicate(App *app, const wchar_t *s)
{
    size_t n = wcslen(s) + 1;
    wchar_t *p = allocate(app, n * sizeof(*p));
    if (p) memcpy(p, s, n * sizeof(*p));
    return p;
}
static wchar_t *join_path(App *app, const wchar_t *root, const wchar_t *relative)
{
    size_t n = wcslen(root), m = wcslen(relative), i;
    wchar_t *p;
    if (n + m + 2 >= PATH_CAP) {
        failure(app, L"A file path is too long. Move the bundle or data to a shorter folder.");
        return NULL;
    }
    p = allocate(app, (n + m + 2) * sizeof(*p));
    if (!p) return NULL;
    memcpy(p, root, n * sizeof(*p));
    if (n && p[n - 1] != L'\\') p[n++] = L'\\';
    for (i = 0; i <= m; ++i) p[n + i] = relative[i] == L'/' ? L'\\' : relative[i];
    return p;
}
static int local_absolute(const wchar_t *path)
{
    return path && ((path[0] >= L'A' && path[0] <= L'Z') ||
                    (path[0] >= L'a' && path[0] <= L'z')) &&
        path[1] == L':' && (path[2] == L'\\' || path[2] == L'/');
}
static int require_local_volume(App *app, const wchar_t *root)
{
    UINT type = GetDriveTypeW(root);
    if (type != DRIVE_FIXED && type != DRIVE_REMOVABLE && type != DRIVE_CDROM && type != DRIVE_RAMDISK)
        return failure(app, L"Only local disk volumes are accepted. Network shares, mapped network drives and unknown volume types are refused.\n%ls", root);
    return 1;
}
static wchar_t *absolute_root(App *app, const wchar_t *input)
{
    wchar_t *full, *result;
    DWORD n;
    const wchar_t *p = input, *part;
    if (!wcsncmp(p, L"\\\\?\\", 4)) p += 4;
    if (!local_absolute(p)) {
        failure(app, L"Use an absolute local drive folder, such as C:\\Games\\Tyrian2000. Network and device paths are not accepted.");
        return NULL;
    }
    { wchar_t drive_root[] = {p[0], L':', L'\\', 0};
      if (!require_local_volume(app, drive_root)) return NULL;
    }
    /* Refuse ADS, DOS device syntax and explicit traversal before normalizing. */
    part = p + 3;
    for (const wchar_t *q = part;; ++q) {
        if (*q == L':' || *q == L'?' || *q == L'*' || *q == L'"' || *q == L'|' ||
            *q == L'<' || *q == L'>' || (*q && *q < 32)) {
            failure(app, L"Unsupported path syntax in the selected folder."); return NULL;
        }
        if (!*q || *q == L'\\' || *q == L'/') {
            size_t len = (size_t)(q - part);
            if ((len == 1 && part[0] == L'.') || (len == 2 && part[0] == L'.' && part[1] == L'.') ||
                (len && (part[len - 1] == L'.' || part[len - 1] == L' ')) ||
                (len && preview_reserved_component(part, len))) {
                failure(app, L"Folder paths may not contain traversal, reserved device names or trailing dots/spaces."); return NULL;
            }
            if (!*q) break;
            part = q + 1;
        }
    }
    full = allocate(app, PATH_CAP * sizeof(*full));
    if (!full) return NULL;
    n = GetFullPathNameW(p, PATH_CAP - 4, full, NULL);
    if (!n || n >= PATH_CAP - 4 || !local_absolute(full)) {
        free(full); failure(app, L"Unable to resolve the selected local folder."); return NULL;
    }
    while (n > 3 && full[n - 1] == L'\\') full[--n] = 0;
    result = allocate(app, (n + 5) * sizeof(*result));
    if (result) { wcscpy(result, L"\\\\?\\"); wcscat(result, full); }
    free(full);
    return result;
}
static int is_ancestor(const wchar_t *a, const wchar_t *b)
{
    size_t n = wcslen(a);
    return n && wcslen(b) >= n &&
        CompareStringOrdinal(a, (int)n, b, (int)n, TRUE) == CSTR_EQUAL &&
        (!b[n] || a[n - 1] == L'\\' || b[n] == L'\\');
}
static HANDLE find_lock(App *app, const wchar_t *path)
{
    for (size_t i = 0; i < app->lock_count; ++i)
        if (!_wcsicmp(path, app->locks[i].path)) return app->locks[i].handle;
    return INVALID_HANDLE_VALUE;
}
static int remember_lock(App *app, const wchar_t *path, HANDLE handle)
{
    if (app->lock_count == app->lock_capacity) {
        size_t cap = app->lock_capacity ? app->lock_capacity * 2 : 128;
        LockedPath *next = realloc(app->locks, cap * sizeof(*next));
        if (!next) { CloseHandle(handle); return failure(app, L"Not enough memory to guard verified input files."); }
        app->locks = next; app->lock_capacity = cap;
    }
    app->locks[app->lock_count].path = duplicate(app, path);
    if (!app->locks[app->lock_count].path) { CloseHandle(handle); return 0; }
    app->locks[app->lock_count++].handle = handle;
    return 1;
}
static HANDLE lock_one(App *app, const wchar_t *path, int directory)
{
    BY_HANDLE_FILE_INFORMATION info;
    HANDLE h = find_lock(app, path);
    if (h != INVALID_HANDLE_VALUE) return h;
    h = CreateFileW(path, directory ? FILE_READ_ATTRIBUTES : GENERIC_READ,
                    directory ? FILE_SHARE_READ | FILE_SHARE_WRITE : FILE_SHARE_READ,
                    NULL, OPEN_EXISTING,
                    FILE_FLAG_OPEN_REPARSE_POINT | (directory ? FILE_FLAG_BACKUP_SEMANTICS : FILE_FLAG_SEQUENTIAL_SCAN), NULL);
    if (h == INVALID_HANDLE_VALUE) { win_failure(app, L"Opening verified input", path); return h; }
    if (!GetFileInformationByHandle(h, &info) || GetFileType(h) != FILE_TYPE_DISK ||
        (info.dwFileAttributes & FILE_ATTRIBUTE_REPARSE_POINT) ||
        !!(info.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) != !!directory) {
        CloseHandle(h); failure(app, L"Refusing a reparse point, symlink or unexpected file type:\n%ls", path); return INVALID_HANDLE_VALUE;
    }
    if (!remember_lock(app, path, h)) return INVALID_HANDLE_VALUE;
    return h;
}
static int guard_parents(App *app, const wchar_t *path, int include_last)
{
    wchar_t *copy = duplicate(app, path);
    int ok = 1;
    size_t root_length;
    if (!copy) return 0;
    root_length = preview_volume_root_length(copy);
    if (!root_length && wcslen(copy) >= 7 && !wcsncmp(copy, L"\\\\?\\", 4) && local_absolute(copy + 4)) root_length = 7;
    if (!root_length) {
        free(copy); return failure(app, L"Internal path is not an absolute local drive or volume-identity path.");
    }
    for (size_t i = root_length;; ++i) {
        wchar_t c = copy[i];
        if (i == root_length || c == L'\\' || (!c && include_last)) {
            copy[i] = 0;
            if (lock_one(app, copy, 1) == INVALID_HANDLE_VALUE) ok = 0;
            copy[i] = c;
        }
        if (!c || !ok) break;
    }
    free(copy);
    return ok;
}
/* Resolve aliases through the locked object, not GetFullPathNameW strings.
 * All subsequent reads/writes use this volume-GUID path, avoiding drive remaps.
 */
static wchar_t *directory_identity(App *app, const wchar_t *path)
{
    wchar_t *identity = NULL, *again = NULL, root[50];
    HANDLE selected, canonical;
    BY_HANDLE_FILE_INFORMATION a, b;
    DWORD n;
    if (!guard_parents(app, path, 1)) return NULL;
    selected = find_lock(app, path);
    identity = allocate(app, PATH_CAP * sizeof(*identity));
    again = allocate(app, PATH_CAP * sizeof(*again));
    if (!identity || !again) goto failed;
    n = GetFinalPathNameByHandleW(selected, identity, PATH_CAP, FILE_NAME_NORMALIZED | VOLUME_NAME_GUID);
    if (!n || n >= PATH_CAP) { win_failure(app, L"Resolving the locked directory's local volume identity", path); goto failed; }
    if (!preview_volume_root_length(identity)) { failure(app, L"The folder does not resolve to a supported local volume identity.\n%ls", path); goto failed; }
    while (n > 49 && identity[n - 1] == L'\\') identity[--n] = 0;
    memcpy(root, identity, 49 * sizeof(*root)); root[49] = 0;
    if (!require_local_volume(app, root) || !guard_parents(app, identity, 1)) goto failed;
    canonical = find_lock(app, identity);
    if (!GetFileInformationByHandle(selected, &a) || !GetFileInformationByHandle(canonical, &b) ||
        a.dwVolumeSerialNumber != b.dwVolumeSerialNumber || a.nFileIndexHigh != b.nFileIndexHigh || a.nFileIndexLow != b.nFileIndexLow) {
        failure(app, L"A folder identity changed while being verified. Nothing will be launched.\n%ls", path); goto failed;
    }
    n = GetFinalPathNameByHandleW(selected, again, PATH_CAP, FILE_NAME_NORMALIZED | VOLUME_NAME_GUID);
    if (!n || n >= PATH_CAP) { win_failure(app, L"Rechecking the locked directory identity", path); goto failed; }
    while (n > 49 && again[n - 1] == L'\\') again[--n] = 0;
    if (CompareStringOrdinal(identity, -1, again, -1, TRUE) != CSTR_EQUAL) {
        failure(app, L"A folder path changed while being verified. Nothing will be launched.\n%ls", path); goto failed;
    }
    free(again); return identity;
 failed:
    free(identity); free(again); return NULL;
}
/* CreateProcess CWD must be an ordinary DOS path, not a verbatim/GUID path.
 * Retain GUID paths for file I/O and compare the DOS projection to locked IDs.
 */
static wchar_t *process_directory(App *app, const wchar_t *identity)
{
    wchar_t *dos = NULL, *extended = NULL, *resolved = NULL;
    wchar_t volume[49], drive[3], drive_target[PATH_CAP], volume_target[PATH_CAP];
    HANDLE directory = find_lock(app, identity);
    DWORD n;
    int ok = 0;
    if (directory == INVALID_HANDLE_VALUE || !preview_volume_root_length(identity)) {
        failure(app, L"The process directory has no locked local volume identity."); return NULL;
    }
    dos = allocate(app, PATH_CAP * sizeof(*dos));
    if (!dos) return NULL;
    n = GetFinalPathNameByHandleW(directory, dos, PATH_CAP, FILE_NAME_NORMALIZED | VOLUME_NAME_DOS);
    if (!n || n >= PATH_CAP || wcsncmp(dos, L"\\\\?\\", 4) || !local_absolute(dos + 4)) {
        failure(app, L"The locked folder has no supported ordinary drive-letter path. Move the extracted bundle to a normal local drive folder."); goto done;
    }
    memmove(dos, dos + 4, (wcslen(dos + 4) + 1) * sizeof(*dos));
    n = (DWORD)wcslen(dos);
    while (n > 3 && dos[n - 1] == L'\\') dos[--n] = 0;
    if (!preview_process_path_fits(n, 0)) {
        failure(app, L"The process folder exceeds Windows' supported path length. Move the extracted bundle closer to the drive root."); goto done;
    }
    /* A direct volume mount only: a SUBST/device-prefix alias is not a usable
     * final process path. The normal physical drive projection may still work. */
    drive[0] = dos[0]; drive[1] = L':'; drive[2] = 0;
    memcpy(volume, identity + 4, 44 * sizeof(*volume)); volume[44] = 0;
    if (!QueryDosDeviceW(drive, drive_target, PATH_CAP) ||
        !QueryDosDeviceW(volume, volume_target, PATH_CAP) ||
        CompareStringOrdinal(drive_target, -1, volume_target, -1, TRUE) != CSTR_EQUAL) {
        failure(app, L"The game process path must map directly to its verified local volume. Use a normal local drive folder rather than a drive alias."); goto done;
    }
    extended = absolute_root(app, dos);
    if (!extended || !(resolved = directory_identity(app, extended))) goto done;
    if (CompareStringOrdinal(identity, -1, resolved, -1, TRUE) != CSTR_EQUAL) {
        failure(app, L"The ordinary process path does not identify the locked session directory. Nothing will be launched."); goto done;
    }
    ok = 1;
 done:
    free(extended); free(resolved);
    if (!ok) { free(dos); dos = NULL; }
    return dos;
}
static int session_paths_fit(App *app, size_t directory_length)
{
    if (!preview_process_path_fits(directory_length, 0)) goto too_long;
    for (size_t i = 0; i < PREVIEW_PAYLOAD_COUNT; ++i)
        if (!preview_process_path_fits(directory_length, wcslen(preview_payload[i].path))) goto too_long;
    for (size_t i = 0; i < PREVIEW_ORIGINAL_COUNT; ++i)
        if (!preview_process_path_fits(directory_length, 5 + wcslen(preview_original[i].path))) goto too_long;
    if (!preview_process_path_fits(directory_length, wcslen(L"opentyrian.cfg"))) goto too_long;
    return 1;
 too_long:
    return failure(app, L"The new session or a child asset path would exceed Windows' supported path length. Move the extracted bundle to a shorter local folder, such as C:\\Games\\Level2.");
}
static int preflight_process_paths(App *app)
{
    wchar_t *root = process_directory(app, app->root_identity);
    size_t n;
    int ok;
    if (!root) return 0;
    n = wcslen(root);
    /* Include sessions\, the exact timestamp/random basename, and separators.
     * This check occurs before even the sessions container can be created. */
    n += (root[n - 1] == L'\\' ? 0 : 1) + wcslen(L"sessions") + 1 + SESSION_NAME_CHARS;
    ok = session_paths_fit(app, n);
    free(root); return ok;
}
static int validate_locations(App *app)
{
    wchar_t *sessions = join_path(app, app->root_identity, L"sessions");
    wchar_t *existing = NULL;
    DWORD attributes;
    int ok = 0;
    if (!sessions) return 0;
    /* These are handle-derived, long-name volume-GUID identities, never aliases. */
    if (is_ancestor(app->data_identity, app->root_identity) ||
        is_ancestor(app->data_identity, sessions) || is_ancestor(sessions, app->data_identity)) {
        failure(app, L"Extract the bundle into a fresh folder OUTSIDE the original data folder. Original data must also be outside the bundle's sessions tree. Nothing will be written into original data."); goto done;
    }
    attributes = GetFileAttributesW(sessions);
    if (attributes != INVALID_FILE_ATTRIBUTES) {
        existing = directory_identity(app, sessions);
        if (!existing) goto done;
        if (CompareStringOrdinal(existing, -1, sessions, -1, TRUE) != CSTR_EQUAL ||
            is_ancestor(app->data_identity, existing) || is_ancestor(existing, app->data_identity)) {
            failure(app, L"The existing sessions folder has an unexpected physical identity or overlaps original data."); goto done;
        }
    } else {
        DWORD code = GetLastError();
        if (code != ERROR_FILE_NOT_FOUND && code != ERROR_PATH_NOT_FOUND) {
            win_failure(app, L"Checking the isolated sessions location", sessions); goto done;
        }
    }
    ok = 1;
 done:
    free(existing); free(sessions); return ok;
}
static int digest_handle(App *app, HANDLE file, char hex[65], unsigned long long *size)
{
    BCRYPT_HASH_HANDLE hash = NULL;
    DWORD object_bytes = 0, returned = 0, got;
    unsigned char digest[32], buffer[65536], *object = NULL;
    LARGE_INTEGER zero, length;
    int ok = 0;
    zero.QuadPart = 0;
    if (!GetFileSizeEx(file, &length) || length.QuadPart < 0 ||
        !SetFilePointerEx(file, zero, NULL, FILE_BEGIN)) return win_failure(app, L"Reading file metadata", L"");
    *size = (unsigned long long)length.QuadPart;
    if (BCryptGetProperty(app->sha, BCRYPT_OBJECT_LENGTH, (PUCHAR)&object_bytes, sizeof(object_bytes), &returned, 0) < 0 ||
        !(object = allocate(app, object_bytes)) ||
        BCryptCreateHash(app->sha, &hash, object, object_bytes, NULL, 0, 0) < 0) goto done;
    for (;;) {
        if (!ReadFile(file, buffer, sizeof(buffer), &got, NULL)) { win_failure(app, L"Reading pinned file", L""); goto done; }
        if (!got) break;
        if (BCryptHashData(hash, buffer, got, 0) < 0) goto done;
    }
    if (BCryptFinishHash(hash, digest, sizeof(digest), 0) < 0) goto done;
    for (size_t i = 0; i < sizeof(digest); ++i) {
        static const char alphabet[] = "0123456789abcdef";
        hex[i * 2] = alphabet[digest[i] >> 4]; hex[i * 2 + 1] = alphabet[digest[i] & 15];
    }
    hex[64] = 0; ok = 1;
 done:
    if (hash) BCryptDestroyHash(hash);
    free(object);
    if (!ok && !*app->error) failure(app, L"Windows SHA-256 verification failed.");
    return ok;
}
static int verify_file(App *app, const wchar_t *path, const PreviewFile *entry)
{
    HANDLE file;
    char hash[65];
    unsigned long long bytes;
    LARGE_INTEGER actual_size;
    if (!guard_parents(app, path, 0)) return 0;
    file = lock_one(app, path, 0);
    if (file == INVALID_HANDLE_VALUE) return 0;
    if (!GetFileSizeEx(file, &actual_size)) return win_failure(app, L"Reading pinned input size", path);
    if (actual_size.QuadPart < 0 || (unsigned long long)actual_size.QuadPart != entry->size)
        return failure(app, L"An input has the wrong byte count. Nothing will be launched.\n%ls", path);
    if (!digest_handle(app, file, hash, &bytes)) return 0;
    if (bytes != entry->size || strcmp(hash, entry->sha256))
        return failure(app, L"An input is missing, changed or from a different data edition. Nothing will be launched.\n%ls", path);
    return 1;
}
static int verify_inventory(App *app, const wchar_t *root, const PreviewFile *files, size_t count)
{
    for (size_t i = 0; i < count; ++i) {
        wchar_t *path = join_path(app, root, files[i].path);
        int ok = path && verify_file(app, path, &files[i]);
        free(path);
        if (!ok) return 0;
    }
    return 1;
}
static int make_directory(App *app, const wchar_t *path, int fresh)
{
    if (!guard_parents(app, path, 0)) return 0;
    if (!CreateDirectoryW(path, NULL) && (fresh || GetLastError() != ERROR_ALREADY_EXISTS))
        return win_failure(app, L"Creating an isolated session directory", path);
    return lock_one(app, path, 1) != INVALID_HANDLE_VALUE;
}
static int make_payload_parents(App *app, const wchar_t *root, const wchar_t *relative)
{
    wchar_t *copy = duplicate(app, relative);
    if (!copy) return 0;
    for (size_t i = 0; copy[i]; ++i) if (copy[i] == L'/') {
        wchar_t *path;
        int ok;
        copy[i] = 0; path = join_path(app, root, copy); copy[i] = L'/';
        ok = path && make_directory(app, path, 0); free(path);
        if (!ok) { free(copy); return 0; }
    }
    free(copy); return 1;
}
static HANDLE zone_stream(App *app, const wchar_t *path, int *absent)
{
    size_t n = wcslen(path);
    wchar_t *stream = allocate(app, (n + 18) * sizeof(*stream));
    HANDLE h;
    *absent = 0;
    if (!stream) return INVALID_HANDLE_VALUE;
    wcscpy(stream, path); wcscat(stream, L":Zone.Identifier");
    h = CreateFileW(stream, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_FLAG_OPEN_REPARSE_POINT, NULL);
    if (h == INVALID_HANDLE_VALUE) {
        DWORD code = GetLastError();
        if (code == ERROR_FILE_NOT_FOUND || code == ERROR_PATH_NOT_FOUND) *absent = 1;
        else win_failure(app, L"Checking the preserved download security marker", path);
    }
    free(stream); return h;
}
static int copy_verified(App *app, const wchar_t *source, const wchar_t *target, const PreviewFile *entry)
{
    HANDLE source_zone, target_zone = INVALID_HANDLE_VALUE;
    int no_source, no_target, ok = 0;
    char a[65], b[65];
    unsigned long long asize, bsize;
    source_zone = zone_stream(app, source, &no_source);
    if (source_zone == INVALID_HANDLE_VALUE && !no_source) return 0;
    if (!CopyFileW(source, target, TRUE)) { win_failure(app, L"Copying a pinned input without replacement", target); goto done; }
    if (!verify_file(app, target, entry)) goto done;
    target_zone = zone_stream(app, target, &no_target);
    if (target_zone == INVALID_HANDLE_VALUE && !no_target) goto done;
    if (no_source != no_target) { failure(app, L"The destination did not preserve the download security marker. Use a local NTFS folder.\n%ls", target); goto done; }
    if (!no_source && (!digest_handle(app, source_zone, a, &asize) || !digest_handle(app, target_zone, b, &bsize))) goto done;
    if (!no_source && (asize != bsize || strcmp(a, b))) { failure(app, L"The copied download security marker differs. Nothing will be launched.\n%ls", target); goto done; }
    ok = 1;
 done:
    if (source_zone != INVALID_HANDLE_VALUE) CloseHandle(source_zone);
    if (target_zone != INVALID_HANDLE_VALUE) CloseHandle(target_zone);
    return ok;
}
static int copy_inventory(App *app, const wchar_t *from, const wchar_t *to, const PreviewFile *files, size_t count)
{
    for (size_t i = 0; i < count; ++i) {
        wchar_t *source = join_path(app, from, files[i].path), *target = join_path(app, to, files[i].path);
        int ok = source && target && make_payload_parents(app, to, files[i].path) && copy_verified(app, source, target, &files[i]);
        free(source); free(target);
        if (!ok) return 0;
    }
    return 1;
}
static int write_bytes(App *app, HANDLE file, const void *data, size_t bytes)
{
    const unsigned char *p = data;
    while (bytes) {
        DWORD sent = 0, n = bytes > 1048576 ? 1048576 : (DWORD)bytes;
        if (!WriteFile(file, p, n, &sent, NULL) || !sent) return win_failure(app, L"Writing session evidence", app->session ? app->session : L"");
        p += sent; bytes -= sent;
    }
    return 1;
}
static int write_wide(App *app, HANDLE file, const wchar_t *text)
{
    int n = WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, text, -1, NULL, 0, NULL, NULL), ok;
    char *raw;
    if (!n || !(raw = allocate(app, (size_t)n))) return 0;
    WideCharToMultiByte(CP_UTF8, WC_ERR_INVALID_CHARS, text, -1, raw, n, NULL, NULL);
    ok = write_bytes(app, file, raw, (size_t)n - 1); free(raw); return ok;
}
static int journalf(App *app, const wchar_t *format, ...)
{
    wchar_t line[4096];
    va_list args;
    va_start(args, format); vswprintf(line, ARRAY_COUNT(line), format, args); va_end(args);
    line[ARRAY_COUNT(line) - 1] = 0;
    return write_wide(app, app->journal, line);
}
static HANDLE new_file(App *app, const wchar_t *name, int inherit)
{
    wchar_t *path = join_path(app, app->session, name);
    SECURITY_ATTRIBUTES sa = {sizeof(sa), NULL, inherit};
    HANDLE h;
    if (!path) return INVALID_HANDLE_VALUE;
    h = CreateFileW(path, GENERIC_WRITE, FILE_SHARE_READ, &sa, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, NULL);
    if (h == INVALID_HANDLE_VALUE) win_failure(app, L"Creating a new session file", path);
    free(path); return h;
}
static int fresh_session(App *app)
{
    wchar_t *sessions = join_path(app, app->root_identity, L"sessions"), *sessions_identity = NULL;
    SYSTEMTIME now;
    int ok = 0;
    if (!sessions) return 0;
    if (!validate_locations(app) || !preflight_process_paths(app) || !make_directory(app, sessions, 0)) goto done;
    sessions_identity = directory_identity(app, sessions);
    if (!sessions_identity) goto done;
    if (CompareStringOrdinal(sessions, -1, sessions_identity, -1, TRUE) != CSTR_EQUAL ||
        is_ancestor(app->data_identity, sessions_identity) || is_ancestor(sessions_identity, app->data_identity)) {
        failure(app, L"Session container identity mismatch or original-data overlap."); goto done;
    }
    for (int attempt = 0; attempt < 16; ++attempt) {
        unsigned char random[16];
        wchar_t name[96], suffix[33];
        if (BCryptGenRandom(NULL, random, sizeof(random), BCRYPT_USE_SYSTEM_PREFERRED_RNG) < 0) {
            failure(app, L"Windows could not generate a fresh random session identity."); goto done;
        }
        for (int j = 0; j < 16; ++j) swprintf(suffix + j * 2, 3, L"%02x", random[j]);
        GetSystemTime(&now);
        swprintf(name, ARRAY_COUNT(name), L"%04u%02u%02uT%02u%02u%02uZ-%ls", now.wYear, now.wMonth, now.wDay, now.wHour, now.wMinute, now.wSecond, suffix);
        if (wcslen(name) != SESSION_NAME_CHARS) { failure(app, L"Unexpected session identity length. Nothing will be copied."); goto done; }
        app->session = join_path(app, sessions, name);
        if (!app->session) goto done;
        if (CreateDirectoryW(app->session, NULL)) {
            if (lock_one(app, app->session, 1) == INVALID_HANDLE_VALUE) goto done;
            ok = 1; break;
        }
        if (GetLastError() != ERROR_ALREADY_EXISTS) { win_failure(app, L"Creating a fresh session", app->session); goto done; }
        free(app->session); app->session = NULL;
    }
    if (!ok) { failure(app, L"Could not allocate a unique new session. Existing sessions are never reused."); goto done; }
    { static const wchar_t *const dirs[] = {L"data", L"tmp", L"profile"};
      for (size_t i = 0; i < ARRAY_COUNT(dirs); ++i) {
          wchar_t *path = join_path(app, app->session, dirs[i]);
          ok = path && make_directory(app, path, 1); free(path);
          if (!ok) goto done;
      }
    }
 done:
    free(sessions_identity); free(sessions); return ok;
}
static int prepare_session(App *app)
{
    wchar_t *data;
    HANDLE config;
    char text[256];
    int ok;
    if (!fresh_session(app)) return 0;
    app->process_session = process_directory(app, app->session);
    if (!app->process_session || !session_paths_fit(app, wcslen(app->process_session))) return 0;
    app->journal = new_file(app, L"launcher.log", 0);
    if (app->journal == INVALID_HANDLE_VALUE) return 0;
    if (!journalf(app, L"OpenTyrian isolated direct level-2 preview\r\nBundle: %ls\r\nSource commit: %ls\r\nPackage: %ls\r\nOriginal data (read only): %ls\r\nSession: %ls\r\nScale: %dx, windowed\r\nState: PREPARING, no game started\r\n", PREVIEW_BUNDLE_ID, PREVIEW_SOURCE_COMMIT, app->root, app->data, app->session, app->scale)) return 0;
    for (size_t i = 0; i < PREVIEW_PAYLOAD_COUNT; ++i)
        if (!journalf(app, L"Payload: %ls | %hs | %llu bytes\r\n", preview_payload[i].path, preview_payload[i].sha256, preview_payload[i].size)) return 0;
    for (size_t i = 0; i < PREVIEW_ORIGINAL_COUNT; ++i)
        if (!journalf(app, L"Original: %ls | %hs | %llu bytes\r\n", preview_original[i].path, preview_original[i].sha256, preview_original[i].size)) return 0;
    if (!copy_inventory(app, app->root_identity, app->session, preview_payload, PREVIEW_PAYLOAD_COUNT)) return 0;
    data = join_path(app, app->session, L"data");
    ok = data && copy_inventory(app, app->data_identity, data, preview_original, PREVIEW_ORIGINAL_COUNT);
    free(data); if (!ok) return 0;
    config = new_file(app, L"opentyrian.cfg", 0);
    if (config == INVALID_HANDLE_VALUE) return 0;
    snprintf(text, sizeof(text), "section 'video'\n    item 'fullscreen' '-1'\n    item 'scaler' '%dx'\n    item 'scaling_mode' 'Integer'\n", app->scale);
    ok = write_bytes(app, config, text, strlen(text)); CloseHandle(config);
    return ok;
}
static int env_compare(const void *a, const void *b)
{
    return _wcsicmp(*(const wchar_t *const *)a, *(const wchar_t *const *)b);
}
static int add_env(App *app, wchar_t **entries, size_t *count, const wchar_t *name, const wchar_t *value)
{
    size_t n = wcslen(name) + wcslen(value) + 2;
    wchar_t *line = allocate(app, n * sizeof(*line));
    if (!line) return 0;
    swprintf(line, n, L"%ls=%ls", name, value); entries[(*count)++] = line;
    return 1;
}
static wchar_t *child_environment(App *app)
{
    wchar_t windows[PATH_CAP], system[PATH_CAP], drive[3], *tmp = NULL, *profile = NULL, *block = NULL;
    wchar_t *entries[PREVIEW_REVIEWED_ENV_COUNT + 16];
    size_t count = 0, total = 1, cursor = 0;
    UINT n = GetWindowsDirectoryW(windows, ARRAY_COUNT(windows));
    if (!n || n >= ARRAY_COUNT(windows) || !local_absolute(windows)) { failure(app, L"Could not obtain the Windows system folder."); goto done; }
    n = GetSystemDirectoryW(system, ARRAY_COUNT(system));
    if (!n || n >= ARRAY_COUNT(system) || !local_absolute(system)) { failure(app, L"Could not obtain the Windows system DLL folder."); goto done; }
    drive[0] = windows[0]; drive[1] = L':'; drive[2] = 0;
    tmp = join_path(app, app->process_session, L"tmp"); profile = join_path(app, app->process_session, L"profile");
    if (!tmp || !profile) goto done;
#define ADD_ENV(name, value) do { if (!add_env(app, entries, &count, name, value)) goto done; } while (0)
    ADD_ENV(L"SystemRoot", windows); ADD_ENV(L"WINDIR", windows); ADD_ENV(L"SystemDrive", drive);
    ADD_ENV(L"PATH", system); ADD_ENV(L"TEMP", tmp); ADD_ENV(L"TMP", tmp);
    ADD_ENV(L"USERPROFILE", profile); ADD_ENV(L"APPDATA", profile); ADD_ENV(L"LOCALAPPDATA", profile);
    for (size_t i = 0; i < PREVIEW_ENV_COUNT; ++i) ADD_ENV(preview_env[i].name, preview_env[i].value);
#undef ADD_ENV
    qsort(entries, count, sizeof(*entries), env_compare);
    for (size_t i = 0; i < count; ++i) total += wcslen(entries[i]) + 1;
    if (total >= 32767) { failure(app, L"The isolated child environment is too large."); goto done; }
    block = allocate(app, total * sizeof(*block));
    if (!block) goto done;
    for (size_t i = 0; i < count; ++i) {
        size_t len = wcslen(entries[i]) + 1;
        memcpy(block + cursor, entries[i], len * sizeof(*block)); cursor += len;
    }
    block[cursor] = 0;
 done:
    for (size_t i = 0; i < count; ++i) free(entries[i]);
    free(tmp); free(profile); return block;
}
static int run_game(App *app, DWORD *exit_code)
{
    wchar_t *exe = NULL, *environment = NULL, *command = NULL, *checked_directory = NULL;
    STARTUPINFOEXW startup;
    PROCESS_INFORMATION process;
    SIZE_T attribute_bytes = 0;
    HANDLE inherited[3];
    SECURITY_ATTRIBUTES sa = {sizeof(sa), NULL, TRUE};
    int ok = 0, attributes_initialized = 0;
    memset(&startup, 0, sizeof(startup)); memset(&process, 0, sizeof(process));
    exe = join_path(app, app->process_session, PREVIEW_GAME_EXE);
    if (!exe || !(environment = child_environment(app))) goto done;
    command = allocate(app, (wcslen(exe) + 160) * sizeof(*command));
    if (!command) goto done;
    swprintf(command, wcslen(exe) + 160, L"\"%ls\" --data=data --level2-preview=asteroid2-v1 --no-xmas --no-joystick", exe);
    app->out = new_file(app, L"stdout.log", 1); app->err = new_file(app, L"stderr.log", 1);
    app->input = CreateFileW(L"NUL", GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE, &sa, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (app->out == INVALID_HANDLE_VALUE || app->err == INVALID_HANDLE_VALUE || app->input == INVALID_HANDLE_VALUE) {
        if (!*app->error) win_failure(app, L"Creating child log handles", app->session);
        goto done;
    }
    inherited[0] = app->out; inherited[1] = app->err; inherited[2] = app->input;
    InitializeProcThreadAttributeList(NULL, 1, 0, &attribute_bytes);
    startup.lpAttributeList = allocate(app, attribute_bytes);
    if (!startup.lpAttributeList) goto done;
    if (!InitializeProcThreadAttributeList(startup.lpAttributeList, 1, 0, &attribute_bytes)) { win_failure(app, L"Initializing exact child handle inheritance", L""); goto done; }
    attributes_initialized = 1;
    if (!UpdateProcThreadAttribute(startup.lpAttributeList, 0, PROC_THREAD_ATTRIBUTE_HANDLE_LIST,
                                   inherited, sizeof(inherited), NULL, NULL)) { win_failure(app, L"Restricting child handle inheritance", L""); goto done; }
    startup.StartupInfo.cb = sizeof(startup); startup.StartupInfo.dwFlags = STARTF_USESTDHANDLES;
    startup.StartupInfo.hStdInput = app->input; startup.StartupInfo.hStdOutput = app->out; startup.StartupInfo.hStdError = app->err;
    if (!journalf(app, L"Command: %ls\r\nWorking directory: %ls\r\nState: VERIFIED, launching once\r\n", command, app->process_session)) goto done;
    for (size_t i = 0; i < PREVIEW_ENV_COUNT; ++i)
        if (!journalf(app, L"HD control: %ls=%ls\r\n", preview_env[i].name, preview_env[i].value)) goto done;
    if (!FlushFileBuffers(app->journal)) { win_failure(app, L"Flushing pre-launch evidence", app->session); goto done; }
    /* Recheck the ordinary DOS projection immediately before CreateProcessW. */
    checked_directory = process_directory(app, app->session);
    if (!checked_directory) goto done;
    if (CompareStringOrdinal(checked_directory, -1, app->process_session, -1, TRUE) != CSTR_EQUAL) {
        failure(app, L"The process directory projection changed. Nothing will be launched."); goto done;
    }
    if (!CreateProcessW(exe, command, NULL, NULL, TRUE,
                        EXTENDED_STARTUPINFO_PRESENT | CREATE_UNICODE_ENVIRONMENT,
                        environment, app->process_session, &startup.StartupInfo, &process)) {
        win_failure(app, L"Starting the verified game (no security warnings will be bypassed)", exe); goto done;
    }
    CloseHandle(process.hThread); process.hThread = NULL;
    /* This is a normal native game session. Never timeout, send input or kill it. */
    if (WaitForSingleObject(process.hProcess, INFINITE) != WAIT_OBJECT_0 ||
        !GetExitCodeProcess(process.hProcess, exit_code)) {
        win_failure(app, L"Waiting for the game to exit normally", app->session); goto done;
    }
    ok = journalf(app, L"State: EXITED\r\nGame exit code: %lu\r\nSession retained; next launch creates a different session.\r\n", *exit_code);
 done:
    if (process.hThread) CloseHandle(process.hThread);
    if (process.hProcess) CloseHandle(process.hProcess);
    if (attributes_initialized) DeleteProcThreadAttributeList(startup.lpAttributeList);
    free(startup.lpAttributeList); free(exe); free(environment); free(command); free(checked_directory);
    return ok;
}
static wchar_t *choose_original_data(App *app, int *cancelled)
{
    BROWSEINFOW browse;
    PIDLIST_ABSOLUTE choice;
    wchar_t path[MAX_PATH];
    wchar_t *result = NULL;
    HRESULT com = CoInitializeEx(NULL, COINIT_APARTMENTTHREADED);
    memset(&browse, 0, sizeof(browse));
    browse.lpszTitle = L"Select your existing original Tyrian2000 data folder. Only verified game assets will be copied. Saves and settings are never imported.";
    browse.ulFlags = BIF_RETURNONLYFSDIRS | BIF_NEWDIALOGSTYLE | BIF_NONEWFOLDERBUTTON;
    if (FAILED(com)) { failure(app, L"Could not open the normal Windows folder picker. Use --data=C:\\path\\to\\Tyrian2000 instead."); return NULL; }
    choice = SHBrowseForFolderW(&browse);
    if (!choice) *cancelled = 1;
    else {
        if (SHGetPathFromIDListW(choice, path)) result = absolute_root(app, path);
        else failure(app, L"Select a local folder, or use --data with its full local path.");
        CoTaskMemFree(choice);
    }
    CoUninitialize(); return result;
}
static void display_message(App *app, const wchar_t *text, int error)
{
    HANDLE h = GetStdHandle(error ? STD_ERROR_HANDLE : STD_OUTPUT_HANDLE);
    if (h && h != INVALID_HANDLE_VALUE) {
        DWORD mode, written;
        if (GetConsoleMode(h, &mode)) WriteConsoleW(h, text, (DWORD)wcslen(text), &written, NULL);
        else { wchar_t saved[ARRAY_COUNT(app->error)]; wcscpy(saved, app->error); write_wide(app, h, text); wcscpy(app->error, saved); }
    }
    if (!app->check_only) MessageBoxW(NULL, text, L"OpenTyrian level-2 preview", MB_OK | (error ? MB_ICONERROR : MB_ICONINFORMATION));
}
static void cleanup(App *app)
{
    HANDLE handles[] = {app->journal, app->out, app->err, app->input};
    for (size_t i = 0; i < ARRAY_COUNT(handles); ++i)
        if (handles[i] && handles[i] != INVALID_HANDLE_VALUE) CloseHandle(handles[i]);
    for (size_t i = 0; i < app->lock_count; ++i) { CloseHandle(app->locks[i].handle); free(app->locks[i].path); }
    if (app->sha) BCryptCloseAlgorithmProvider(app->sha, 0);
    free(app->locks); free(app->root); free(app->data); free(app->session);
    free(app->root_identity); free(app->data_identity); free(app->process_session); free(app);
}
int WINAPI wWinMain(HINSTANCE instance, HINSTANCE previous, PWSTR unused_command, int show)
{
    App *app = calloc(1, sizeof(*app));
    wchar_t **argv = NULL, *module = NULL, *data_arg = NULL;
    int argc = 0, status = 2, cancelled = 0, scale_seen = 0, help = 0;
    DWORD exit_code = 0;
    (void)instance; (void)previous; (void)unused_command; (void)show;
    if (!app) return 2;
    app->scale = 4;
    app->journal = app->out = app->err = app->input = INVALID_HANDLE_VALUE;
    argv = CommandLineToArgvW(GetCommandLineW(), &argc);
    if (!argv) { win_failure(app, L"Reading launch options", L""); goto done; }
    /* Discover read-only mode before reporting even malformed options. */
    for (int i = 1; i < argc; ++i) if (!wcscmp(argv[i], L"--check-only")) app->check_only = 1;
    for (int i = 1; i < argc; ++i) {
        if (!wcscmp(argv[i], L"--check-only")) continue;
        if (!wcscmp(argv[i], L"--help")) { help = 1; continue; }
        if (!wcsncmp(argv[i], L"--data=", 7) && argv[i][7] && !data_arg) { data_arg = argv[i] + 7; continue; }
        if ((!wcscmp(argv[i], L"--scale=2") || !wcscmp(argv[i], L"--scale=4")) && !scale_seen) {
            app->scale = argv[i][8] - L'0'; scale_seen = 1; continue;
        }
        failure(app, L"Unknown or repeated option: %ls\nUse --data=FULL_LOCAL_FOLDER, --scale=2 (or 4), --check-only, or --help.", argv[i]); goto done;
    }
    if (help) {
        display_message(app, L"Double-click to choose your original Tyrian2000 data and play one native level-2 session.\n\nOptions: --data=FULL_LOCAL_FOLDER --scale=2 (default 4) --check-only\n\nCheck-only requires --data and makes no session, logs or game process. Every actual launch creates a new sessions folder entry. Earlier sessions and original data are never changed.\n", 0);
        status = 0; goto done;
    }
    if (!preview_inventory_valid(preview_payload, PREVIEW_PAYLOAD_COUNT, 0, PREVIEW_GAME_EXE) ||
        !preview_inventory_valid(preview_original, PREVIEW_ORIGINAL_COUNT, 1, PREVIEW_GAME_EXE) ||
        !preview_environment_valid(preview_env, PREVIEW_ENV_COUNT)) {
        failure(app, L"The compiled bundle manifest is invalid or does not match the reviewed level-2 contract."); goto done;
    }
    module = allocate(app, PATH_CAP * sizeof(*module));
    if (!module) goto done;
    { DWORD n = GetModuleFileNameW(NULL, module, PATH_CAP); wchar_t *slash;
      if (!n || n >= PATH_CAP || !(slash = wcsrchr(module, L'\\'))) { failure(app, L"Could not determine this launcher's package folder."); goto done; }
      wchar_t *self = absolute_root(app, module);
      int regular = self && guard_parents(app, self, 0) && lock_one(app, self, 0) != INVALID_HANDLE_VALUE;
      free(self); if (!regular) goto done;
      if (slash == module + 2 || (slash == module + 6 && !wcsncmp(module, L"\\\\?\\", 4))) slash[1] = 0;
      else *slash = 0;
      app->root = absolute_root(app, module);
    }
    if (!app->root || !(app->root_identity = directory_identity(app, app->root))) goto done;
    /* Process-local loader hygiene only; does not change user/system policy. */
    if (!SetDllDirectoryW(L"")) { win_failure(app, L"Excluding the caller's working folder from DLL search", L""); goto done; }
    if (BCryptOpenAlgorithmProvider(&app->sha, BCRYPT_SHA256_ALGORITHM, NULL, 0) < 0) { failure(app, L"Windows SHA-256 is unavailable. Nothing will be launched."); goto done; }
    if (!verify_inventory(app, app->root_identity, preview_payload, PREVIEW_PAYLOAD_COUNT)) goto done;
    if (data_arg) app->data = absolute_root(app, data_arg);
    else if (app->check_only) { failure(app, L"--check-only requires --data=FULL_LOCAL_FOLDER. No folder will be created."); goto done; }
    else app->data = choose_original_data(app, &cancelled);
    if (cancelled) { status = 0; goto done; }
    if (!app->data || !(app->data_identity = directory_identity(app, app->data)) ||
        !validate_locations(app) || !preflight_process_paths(app) ||
        !verify_inventory(app, app->data_identity, preview_original, PREVIEW_ORIGINAL_COUNT)) goto done;
    if (app->check_only) {
        display_message(app, L"CHECK_ONLY_OK: embedded payload hashes and required original data verified. No session, log or game process was created.\r\n", 0);
        status = 0; goto done;
    }
    if (!prepare_session(app) || !run_game(app, &exit_code)) goto done;
    if (exit_code != 0) { failure(app, L"The game exited with code %lu. Its session and logs are preserved at:\n%ls", exit_code, app->session); status = 3; goto done; }
    status = 0;
 done:
    if (status && *app->error) {
        wchar_t saved[ARRAY_COUNT(app->error)]; wcscpy(saved, app->error);
        if (app->journal != INVALID_HANDLE_VALUE) journalf(app, L"State: FAILED\r\n%ls\r\n", saved);
        display_message(app, saved, 1);
    }
    if (argv) LocalFree(argv);
    free(module); cleanup(app); return status;
}
