/**
 * video_lightbox.js — Inline video playback in the carousel
 *
 * Clicking a video slide replaces the poster thumbnail with a
 * <video> element that plays right inside the carousel slide.
 * The carousel pauses on hover (CSS), so the user can watch
 * without the strip moving. Clicking the video or pressing
 * Escape stops playback and restores the poster image.
 */
(function () {
  var slides = document.querySelectorAll('.video-slide[data-video]');
  if (!slides.length) return;

  for (var i = 0; i < slides.length; i++) {
    slides[i].addEventListener('click', handleSlideClick);
  }

  function handleSlideClick(e) {
    e.preventDefault();
    e.stopPropagation();

    var slide = this;

    // If already playing, stop it
    if (slide.classList.contains('playing')) {
      stopVideo(slide);
      return;
    }

    // Stop any other playing video first
    var playing = document.querySelector('.video-slide.playing');
    if (playing) stopVideo(playing);

    var videoSrc = slide.getAttribute('data-video');
    if (!videoSrc) return;

    // Hide poster image and play button, show video
    var img = slide.querySelector('img');
    var playBtn = slide.querySelector('.slide-play');
    var label = slide.querySelector('.slide-label');

    if (img) img.style.display = 'none';
    if (playBtn) playBtn.style.display = 'none';
    if (label) label.style.display = 'none';

    var video = document.createElement('video');
    video.src = videoSrc;
    video.autoplay = true;
    video.controls = true;
    video.playsInline = true;
    video.muted = true;
    video.className = 'inline-video';
    video.style.width = '100%';
    video.style.height = '100%';
    video.style.objectFit = 'cover';
    video.style.display = 'block';
    video.style.position = 'absolute';
    video.style.top = '0';
    video.style.left = '0';
    video.style.zIndex = '5';
    video.style.background = '#000';

    slide.appendChild(video);
    slide.classList.add('playing');

    // When video ends, restore poster
    video.addEventListener('ended', function () {
      stopVideo(slide);
    });

    // Prevent click on video controls from toggling play/stop
    video.addEventListener('click', function (ev) {
      ev.stopPropagation();
    });
  }

  function stopVideo(slide) {
    var video = slide.querySelector('.inline-video');
    if (video) {
      video.pause();
      video.src = '';
      slide.removeChild(video);
    }

    var img = slide.querySelector('img');
    var playBtn = slide.querySelector('.slide-play');
    var label = slide.querySelector('.slide-label');

    if (img) img.style.display = '';
    if (playBtn) playBtn.style.display = '';
    if (label) label.style.display = '';

    slide.classList.remove('playing');
  }

  // Escape key stops any playing video
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' || e.keyCode === 27) {
      var playing = document.querySelector('.video-slide.playing');
      if (playing) stopVideo(playing);
    }
  });
})();
