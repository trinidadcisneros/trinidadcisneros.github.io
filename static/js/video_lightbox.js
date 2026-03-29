/**
 * video_lightbox.js
 *
 * Handles click-to-play for video slides in the carousel.
 * Clicking a .video-slide opens a full-screen lightbox overlay
 * with the video playing. Click the overlay or the X to close.
 *
 * Each video slide needs a data-video attribute pointing to the
 * video source file, e.g.:
 *   <div class="carousel-slide video-slide" data-video="static/images/reel/muay_thai.MP4">
 */
(function () {
  // Attach click listeners to all video slides
  var slides = document.querySelectorAll('.video-slide[data-video]');
  if (!slides.length) return;

  for (var i = 0; i < slides.length; i++) {
    slides[i].addEventListener('click', openLightbox);
  }

  function openLightbox(e) {
    e.preventDefault();
    e.stopPropagation();

    var videoSrc = this.getAttribute('data-video');
    if (!videoSrc) return;

    // Pause carousel animation while lightbox is open
    var track = document.querySelector('.carousel-track');
    var savedAnimation = '';
    if (track) {
      savedAnimation = track.style.animationPlayState;
      track.style.animationPlayState = 'paused';
    }

    // Create overlay
    var overlay = document.createElement('div');
    overlay.className = 'video-lightbox';

    // Close button
    var closeBtn = document.createElement('span');
    closeBtn.className = 'video-lightbox-close';
    closeBtn.innerHTML = '&times;';
    overlay.appendChild(closeBtn);

    // Video element
    var video = document.createElement('video');
    video.src = videoSrc;
    video.controls = true;
    video.autoplay = true;
    video.playsInline = true;
    video.style.outline = 'none';
    overlay.appendChild(video);

    document.body.appendChild(overlay);

    // Prevent body scroll while lightbox is open
    document.body.style.overflow = 'hidden';

    // Close handlers
    function closeLightbox() {
      video.pause();
      video.src = '';
      document.body.removeChild(overlay);
      document.body.style.overflow = '';
      if (track) {
        track.style.animationPlayState = savedAnimation || '';
      }
    }

    closeBtn.addEventListener('click', function (ev) {
      ev.stopPropagation();
      closeLightbox();
    });

    overlay.addEventListener('click', function (ev) {
      // Only close if clicking the overlay background, not the video
      if (ev.target === overlay) {
        closeLightbox();
      }
    });

    // Close on Escape key
    function onKeyDown(ev) {
      if (ev.key === 'Escape' || ev.keyCode === 27) {
        closeLightbox();
        document.removeEventListener('keydown', onKeyDown);
      }
    }
    document.addEventListener('keydown', onKeyDown);
  }
})();
