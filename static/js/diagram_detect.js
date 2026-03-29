/**
 * Diagram Block Detector
 * Scans <pre> blocks inside the embedded notebook and adds the class
 * 'diagram-block' to any that contain box-drawing characters (decision
 * trees, flow diagrams). This lets CSS style them differently from
 * regular code blocks.
 *
 * Runs after w3-include-html finishes loading the notebook content.
 */

(function () {
  'use strict';

  // Box-drawing characters used in the ASCII decision trees
  var DIAGRAM_CHARS = /[┌┐└┘├┤┬┴┼─│▼▶►]/;

  function tagDiagramBlocks() {
    var notebook = document.querySelector('#jnotebook');
    if (!notebook) return false;

    var pres = notebook.querySelectorAll('pre');
    if (pres.length === 0) return false;

    var tagged = 0;
    for (var i = 0; i < pres.length; i++) {
      var pre = pres[i];

      // Skip syntax-highlighted SQL blocks (inside .highlight div)
      if (pre.parentElement && pre.parentElement.classList.contains('highlight')) {
        continue;
      }

      // Check if the content contains box-drawing characters
      var text = pre.textContent || '';
      if (DIAGRAM_CHARS.test(text)) {
        pre.classList.add('diagram-block');
        tagged++;
      }
    }

    return tagged > 0;
  }

  // Wait for notebook content to load, then tag diagrams
  var CHECK_INTERVAL = 300;
  var MAX_WAIT = 15000;
  var elapsed = 0;

  var interval = setInterval(function () {
    elapsed += CHECK_INTERVAL;
    var notebook = document.querySelector('#jnotebook');

    if (notebook && notebook.innerHTML.length > 500 && !notebook.getAttribute('w3-include-html')) {
      clearInterval(interval);
      setTimeout(function () {
        tagDiagramBlocks();
      }, 300);
      return;
    }

    if (elapsed >= MAX_WAIT) {
      clearInterval(interval);
    }
  }, CHECK_INTERVAL);
})();
