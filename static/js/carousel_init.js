/**
 * carousel_init.js
 *
 * Dynamically duplicates carousel slides for a seamless infinite loop
 * and calculates the correct scroll distance based on actual rendered
 * slide widths — works on both desktop and mobile without black gaps.
 */
(function () {
  var track = document.getElementById('carousel-track');
  if (!track) return;

  var origSlides = track.children;
  var count = origSlides.length;
  if (count === 0) return;

  // Clone every original slide and append (creates seamless loop)
  var clones = [];
  for (var i = 0; i < count; i++) {
    clones.push(origSlides[i].cloneNode(true));
  }
  for (var j = 0; j < clones.length; j++) {
    track.appendChild(clones[j]);
  }

  // Wait one frame so the browser has laid out the cloned slides
  requestAnimationFrame(function () {
    // Measure the total width of the first set of original slides
    var totalWidth = 0;
    for (var k = 0; k < count; k++) {
      totalWidth += track.children[k].getBoundingClientRect().width;
    }

    // Remove any existing carousel-scroll keyframes
    var sheets = document.styleSheets;
    for (var s = sheets.length - 1; s >= 0; s--) {
      try {
        var rules = sheets[s].cssRules || sheets[s].rules;
        if (!rules) continue;
        for (var r = rules.length - 1; r >= 0; r--) {
          if (rules[r].type === CSSRule.KEYFRAMES_RULE && rules[r].name === 'carousel-scroll') {
            sheets[s].deleteRule(r);
          }
        }
      } catch (e) {
        // Cross-origin stylesheet — skip
      }
    }

    // Inject new keyframes with the measured distance
    var style = document.createElement('style');
    style.textContent =
      '@keyframes carousel-scroll { ' +
      '0% { transform: translateX(0); } ' +
      '100% { transform: translateX(-' + totalWidth + 'px); } ' +
      '}';
    document.head.appendChild(style);

    // Speed: ~60px per second (adjust multiplier to taste)
    var duration = Math.round(totalWidth / 60);

    // Apply animation
    track.style.animation = 'carousel-scroll ' + duration + 's linear infinite';
  });

  // Recalculate on resize (e.g. rotating phone)
  var resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () {
      var totalWidth = 0;
      for (var k = 0; k < count; k++) {
        totalWidth += track.children[k].getBoundingClientRect().width;
      }

      // Update keyframes
      var existing = document.getElementById('carousel-dynamic-kf');
      if (existing) existing.parentNode.removeChild(existing);

      var style = document.createElement('style');
      style.id = 'carousel-dynamic-kf';
      style.textContent =
        '@keyframes carousel-scroll { ' +
        '0% { transform: translateX(0); } ' +
        '100% { transform: translateX(-' + totalWidth + 'px); } ' +
        '}';
      document.head.appendChild(style);

      var duration = Math.round(totalWidth / 60);
      track.style.animation = 'none';
      // Force reflow
      void track.offsetHeight;
      track.style.animation = 'carousel-scroll ' + duration + 's linear infinite';
    }, 300);
  });
})();
