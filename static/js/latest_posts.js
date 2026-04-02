/**
 * latest_posts.js
 *
 * Reads /static/data/posts.json, sorts by date descending,
 * takes the latest 10, and renders them as scrollable cards
 * inside the element with id="latest-posts-track".
 *
 * To add a new post: just append an entry to posts.json.
 * The landing page picks it up automatically.
 */
(function () {
  var container = document.getElementById('latest-posts-track');
  if (!container) return;

  // Format ISO date to readable form: "March 29, 2026"
  var months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  function formatDate(isoStr) {
    var parts = isoStr.split('-');
    var y = parts[0], m = parseInt(parts[1], 10), d = parseInt(parts[2], 10);
    return months[m - 1] + ' ' + d + ', ' + y;
  }

  fetch('/static/data/posts.json?v=' + Date.now())
    .then(function (res) { return res.json(); })
    .then(function (posts) {
      // Sort by date descending
      posts.sort(function (a, b) {
        return b.date.localeCompare(a.date);
      });

      // Take latest 10 (or fewer if less exist)
      var latest = posts.slice(0, 10);

      // Build cards
      var html = '';
      for (var i = 0; i < latest.length; i++) {
        var p = latest[i];
        html += '<div class="content-card">'
          + '<div class="card-category ' + p.categoryClass + '">' + p.category.toUpperCase() + '</div>'
          + '<div class="card-date">' + formatDate(p.date) + '</div>'
          + '<h3><a href="' + p.url + '">' + p.title + '</a></h3>'
          + '<p class="card-desc">' + p.desc + '</p>'
          + '</div>';
      }

      container.innerHTML = html;
    })
    .catch(function (err) {
      console.error('Failed to load posts.json:', err);
    });
})();
