// Light/dark toggle. An inline head script applies the stored choice pre-paint;
// this wires the toggle button and persists the choice.
(function () {
  var root = document.documentElement;

  function current() {
    var attr = root.getAttribute('data-theme');
    if (attr) return attr;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches
      ? 'light' : 'dark';
  }

  document.querySelectorAll('.theme-toggle').forEach(function (btn) {
    btn.onclick = function () {
      var next = current() === 'light' ? 'dark' : 'light';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) { /* private mode */ }
    };
  });
})();
