/**
 * video_lightbox.js — Inline video playback in the carousel
 *
 * Uses event delegation on the carousel section so it works
 * regardless of when the DOM loads. Clicking a video slide
 * swaps the poster for a <video> that plays in-place.
 */
document.addEventListener('DOMContentLoaded', function () {

  var carousel = document.querySelector('.carousel-section');
  if (!carousel) return;

  carousel.addEventListener('click', function (e) {
    // Walk up from click target to find the .video-slide
    var slide = e.target.closest('.video-slide[data-video]');
    if (!slide) return;

    e.preventDefault();
    e.stopPropagation();

    // If already playing, stop it
    if (slide.classList.contains('playing')) {
      stopVideo(slide);
      return;
    }

    // Stop any other playing video first
    var playing = carousel.querySelector('.video-slide.playing');
    if (playing) stopVideo(playing);

    var videoSrc = slide.getAttribute('data-video');
    if (!videoSrc) return;

    // Hide poster image, play button, and label
    var img = slide.querySelector('img');
    var playBtn = slide.querySelector('.slide-play');
    var label = slide.querySelector('.slide-label');

    if (img) img.style.display = 'none';
    if (playBtn) playBtn.style.display = 'none';
    if (label) label.style.display = 'none';

    // Create video element inside the slide
    var video = document.createElement('video');
    video.src = videoSrc;
    video.autoplay = true;
    video.controls = true;
    video.playsInline = true;
    video.muted = true;
    video.className = 'inline-video';
    video.style.cssText = 'width:100%;height:100%;object-fit:cover;display:block;position:absolute;top:0;left:0;z-index:5;background:#000;';

    slide.appendChild(video);
    slide.classList.add('playing');

    // When video ends, restore poster
    video.addEventListener('ended', function () {
      stopVideo(slide);
    });

    // Let clicks on the video controls work normally
    video.addEventListener('click', function (ev) {
      ev.stopPropagation();
    });
  });

  function stopVideo(slide) {
    var video = slide.querySelector('.inline-video');
    if (video) {
      video.pause();
      video.removeAttribute('src');
      video.load();
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
      var playing = carousel.querySelector('.video-slide.playing');
      if (playing) stopVideo(playing);
    }
  });

});
