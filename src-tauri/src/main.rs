// Hide the console window in release builds.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{WebviewUrl, WebviewWindowBuilder};

// Injected into the page before the game loads. Adds F11 / Alt+Enter
// fullscreen, blocks the browser shortcuts that would reload or zoom the
// game mid-run, and kills the right-click menu.
const SHELL_SHIM: &str = r#"
(function () {
  function win() {
    var t = window.__TAURI__;
    if (!t || !t.window) return null;
    return t.window.getCurrentWindow ? t.window.getCurrentWindow()
         : (t.window.getCurrent ? t.window.getCurrent() : null);
  }

  window.addEventListener('keydown', function (e) {
    var fullscreen = e.key === 'F11' || (e.key === 'Enter' && e.altKey);
    if (fullscreen) {
      e.preventDefault();
      var w = win();
      if (!w) return;
      Promise.resolve(w.isFullscreen())
        .then(function (on) { return w.setFullscreen(!on); })
        .catch(function () {});
      return;
    }

    // Stop reload / zoom / find from firing while playing.
    var block = e.key === 'F5'
      || ((e.ctrlKey || e.metaKey) && ['r', 'R', 'f', 'F', 'p', 'P', 'g', 'G',
          '+', '-', '=', '0'].indexOf(e.key) !== -1);
    if (block) e.preventDefault();
  }, true);

  window.addEventListener('contextmenu', function (e) { e.preventDefault(); });
  window.addEventListener('dragover', function (e) { e.preventDefault(); });
  window.addEventListener('drop', function (e) { e.preventDefault(); });
})();
"#;

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            WebviewWindowBuilder::new(app, "main", WebviewUrl::App("index.html".into()))
                .title("Nightfall Blade")
                .inner_size(1280.0, 760.0)
                .min_inner_size(900.0, 540.0)
                .resizable(true)
                .center()
                .initialization_script(SHELL_SHIM)
                .build()?;
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("failed to start Nightfall Blade");
}
