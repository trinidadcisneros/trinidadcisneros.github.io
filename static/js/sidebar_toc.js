/**
 * Sidebar TOC Generator
 * Auto-generates a sticky table of contents from headings inside the #jnotebook div.
 * Waits for w3-include-html to finish loading the notebook content, then builds the TOC.
 */

(function () {
  'use strict';

  // Configuration
  var NOTEBOOK_SELECTOR = '#jnotebook';
  var SIDEBAR_ID = 'sidebar-toc';
  var CHECK_INTERVAL = 300;  // ms between checks for notebook content
  var MAX_WAIT = 15000;      // max ms to wait for notebook to load
  var SCROLL_OFFSET = 80;    // px offset when clicking a TOC link

  function buildSidebar() {
    var notebook = document.querySelector(NOTEBOOK_SELECTOR);
    if (!notebook) return false;

    // Find all h2 and h3 headings inside the notebook
    var headings = notebook.querySelectorAll('h2, h3');
    if (headings.length === 0) return false;

    // Get or create the sidebar container
    var sidebar = document.getElementById(SIDEBAR_ID);
    if (!sidebar) return false;

    // Build the TOC
    var title = document.createElement('div');
    title.className = 'sidebar-toc-title';
    title.textContent = 'Contents';
    sidebar.appendChild(title);

    var ul = document.createElement('ul');

    for (var i = 0; i < headings.length; i++) {
      var heading = headings[i];
      var text = heading.textContent.replace(/¶/g, '').trim();

      // Skip empty headings or the notebook title if it duplicates the page title
      if (!text || text.length === 0) continue;

      // Allow full text to wrap naturally in the sidebar

      // Ensure heading has an id for linking
      if (!heading.id) {
        // Check if there's an anchor tag just before or inside
        var anchor = heading.querySelector('a[id]');
        if (anchor) {
          heading.id = anchor.id;
        } else {
          // Check previous sibling for anchor
          var prev = heading.previousElementSibling;
          if (prev && prev.tagName === 'A' && prev.id) {
            heading.id = prev.id;
          } else {
            // Generate an id from text
            heading.id = 'toc-' + text.toLowerCase()
              .replace(/[^a-z0-9]+/g, '-')
              .replace(/^-|-$/g, '')
              .substring(0, 50);
          }
        }
      }

      var li = document.createElement('li');
      li.className = 'toc-' + heading.tagName.toLowerCase();

      var a = document.createElement('a');
      a.href = '#' + heading.id;
      a.textContent = text;
      a.setAttribute('data-target', heading.id);

      // Smooth scroll with offset
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var targetId = this.getAttribute('data-target');
        var target = document.getElementById(targetId);
        if (target) {
          var topPos = target.getBoundingClientRect().top + window.pageYOffset - SCROLL_OFFSET;
          window.scrollTo({ top: topPos, behavior: 'smooth' });
        }
      });

      li.appendChild(a);
      ul.appendChild(li);
    }

    sidebar.appendChild(ul);

    // Set up scroll-based highlighting
    setupScrollHighlight(headings);

    return true;
  }

  function setupScrollHighlight(headings) {
    var tocLinks = document.querySelectorAll('#' + SIDEBAR_ID + ' a');
    if (tocLinks.length === 0) return;

    var headingPositions = [];

    function updatePositions() {
      headingPositions = [];
      for (var i = 0; i < headings.length; i++) {
        if (headings[i].id) {
          headingPositions.push({
            id: headings[i].id,
            top: headings[i].getBoundingClientRect().top + window.pageYOffset
          });
        }
      }
    }

    function highlightCurrent() {
      var scrollPos = window.pageYOffset + SCROLL_OFFSET + 20;
      var currentId = '';

      for (var i = 0; i < headingPositions.length; i++) {
        if (headingPositions[i].top <= scrollPos) {
          currentId = headingPositions[i].id;
        }
      }

      for (var j = 0; j < tocLinks.length; j++) {
        var link = tocLinks[j];
        if (link.getAttribute('data-target') === currentId) {
          link.classList.add('toc-active');
          // Scroll the sidebar to keep active item visible
          var sidebar = document.getElementById(SIDEBAR_ID);
          if (sidebar && link.offsetTop > sidebar.scrollTop + sidebar.clientHeight - 40) {
            sidebar.scrollTop = link.offsetTop - sidebar.clientHeight / 2;
          } else if (sidebar && link.offsetTop < sidebar.scrollTop) {
            sidebar.scrollTop = link.offsetTop - 20;
          }
        } else {
          link.classList.remove('toc-active');
        }
      }
    }

    updatePositions();
    highlightCurrent();

    // Throttled scroll listener
    var scrollTimer = null;
    window.addEventListener('scroll', function () {
      if (scrollTimer) return;
      scrollTimer = setTimeout(function () {
        scrollTimer = null;
        highlightCurrent();
      }, 50);
    });

    // Recalculate positions on resize
    window.addEventListener('resize', function () {
      updatePositions();
    });
  }

  // Wait for notebook content to load, then build sidebar
  function waitAndBuild() {
    var elapsed = 0;

    var interval = setInterval(function () {
      elapsed += CHECK_INTERVAL;
      var notebook = document.querySelector(NOTEBOOK_SELECTOR);

      // Check if notebook has content (w3-include-html finished)
      if (notebook && notebook.innerHTML.length > 500 && !notebook.getAttribute('w3-include-html')) {
        clearInterval(interval);
        // Small delay to ensure all content is rendered
        setTimeout(function () {
          buildSidebar();
        }, 200);
        return;
      }

      if (elapsed >= MAX_WAIT) {
        clearInterval(interval);
      }
    }, CHECK_INTERVAL);
  }

  // Start when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', waitAndBuild);
  } else {
    waitAndBuild();
  }
})();
