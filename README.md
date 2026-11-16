# Nightfall Blade

Fast-paced 2D pixel-art dark fantasy arcade combat against waves of enemies and
multi-phase bosses with neon weapon upgrades — packaged as a native Windows app.

The game itself is a single self-contained HTML file (`dist/index.html`). The
desktop shell is [Tauri 2](https://tauri.app), which uses the WebView2 runtime
that already ships with Windows 10 and 11 instead of bundling a browser, so the
finished app is around 6–10 MB rather than the ~90 MB an Electron build would
cost.

---

## Download

Grab the latest build from the [Releases](../../releases) page:

| File | What it is |
| --- | --- |
| `Nightfall-Blade-Setup.exe` | Installer. Installs for the current user, adds a Start menu entry and an uninstaller. Pulls in WebView2 automatically if the machine somehow lacks it. |
| `Nightfall-Blade-Portable.exe` | Single executable. No install, runs from anywhere including a USB stick. Needs WebView2 already present, which is the case on any up-to-date Windows 10/11. |

Both are unsigned, so SmartScreen will show "Windows protected your PC" the
first time. Click **More info → Run anyway**. Signing it requires a paid code
signing certificate; see the note at the bottom.

---

## Repository layout

```
.
├── dist/
│   └── index.html              the game, one self-contained file
├── src-tauri/
│   ├── src/main.rs             window setup + fullscreen / hotkey shim
│   ├── capabilities/default.json
│   ├── icons/                  app icon in every size Windows wants
│   ├── tauri.conf.json         window size, bundle settings, app identity
│   ├── Cargo.toml              Rust dependencies and size-tuned release profile
│   └── build.rs
├── tools/
│   └── make_icons.py           regenerates the icons from the game's palette
├── .github/workflows/release.yml
├── .gitignore
├── LICENSE
└── README.md
```

---

## Building it yourself

You do not need to build it locally — pushing a tag makes GitHub build it for
you (see below). But if you want to:

**Prerequisites (Windows):**

1. [Rust](https://rustup.rs) — run `rustup-init.exe`, accept the defaults.
2. [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   with the "Desktop development with C++" workload.
3. WebView2 — already on Windows 11 and current Windows 10.

**Then:**

```bash
cargo install tauri-cli --version "^2" --locked
cargo tauri build
```

Results land in:

- `src-tauri/target/release/bundle/nsis/` — the installer
- `src-tauri/target/release/nightfall-blade.exe` — the portable executable

For a live-reloading dev window: `cargo tauri dev`.

---

## Releasing through GitHub

The workflow in `.github/workflows/release.yml` builds on a Windows runner and
attaches both executables to a GitHub release.

```bash
git tag v1.0.0
git push origin v1.0.0
```

The build takes roughly 5–10 minutes on a cold cache. You can also trigger it
without tagging from the **Actions** tab (**Build Windows app → Run workflow**),
which uploads the executables as a workflow artifact instead of publishing a
release.

When you bump the version, change it in **both** `src-tauri/tauri.conf.json` and
`src-tauri/Cargo.toml` so the tag, the installer and the app's Add/Remove
Programs entry agree.

---

## What the desktop shell adds

- A 1280×760 window matching the game's render resolution, centred, resizable,
  with a 900×540 floor so the HUD never clips.
- **F11** or **Alt+Enter** toggles fullscreen.
- F5, Ctrl+R, Ctrl+F, Ctrl+P and Ctrl +/−/0 are swallowed, so you can't
  accidentally reload or zoom the page mid-run.
- Right-click menu and file drag-and-drop disabled.
- No browser chrome, no address bar.

Your best score is stored by the game in `localStorage`, which WebView2 keeps in
the app's own data folder under `%LOCALAPPDATA%`. It survives restarts and
updates, and is removed if you uninstall.

---

## The icon

`tools/make_icons.py` draws it from scratch using the game's own palette —
`#06070d` void black, `#22d3ee` neon cyan for the blade, `#fbbf24` amber for the
crossguard, `#f43f5e` rose for the grip and pommel, `#e879f9` magenta for the
slash arc — then crushes the art down to a 128px grid so it keeps the pixel
look. Regenerate with:

```bash
python tools/make_icons.py
```

Requires Pillow (`pip install pillow`). The committed icons are already built,
so this is only needed if you want to change the design.

---

## Notes

- **Code signing:** unsigned builds trigger SmartScreen warnings. If that
  matters, buy an OV/EV certificate, add it to the repo as the secrets
  `WINDOWS_CERTIFICATE` and `WINDOWS_CERTIFICATE_PASSWORD`, and set
  `bundle.windows.certificateThumbprint` in `tauri.conf.json`.
- **Size:** the release profile is tuned for a small binary (`opt-level = "s"`,
  LTO, symbol stripping). Most of the remaining size is the 420 KB game file and
  the Tauri runtime.
- **macOS / Linux:** the same source builds for both — add `macos-latest` or
  `ubuntu-22.04` to the workflow matrix and the matching `.icns` icon. Nothing
  in the shell is Windows-specific apart from the bundle targets.

---

## License

MIT — see [LICENSE](LICENSE).
