// Copied from <skills>/manim-video/template on __DATE__.
// Animation timer for manim-slides decks, added to every deck by add_clip_timer.py.
// A ring in the bottom-right corner fills while the current slide's clip plays, dims while
// the clip is paused (Space), and becomes a check once the clip has ended, so the presenter
// can see when the next click is safe. T hides or shows it.
(function () {
  const RADIUS = 13;
  const CIRCUMFERENCE = 2 * Math.PI * RADIUS;
  const style = document.createElement("style");
  style.textContent = `
    #clip-timer {
      position: fixed; right: 18px; bottom: 16px; width: 34px; height: 34px;
      z-index: 50; pointer-events: none; transition: opacity 0.3s;
    }
    #clip-timer.hidden { opacity: 0; }
    #clip-timer circle { transition: fill 0.25s, stroke 0.25s, opacity 0.25s; }
    #clip-timer .disk { fill: rgba(255, 255, 255, 0.9); stroke: #d9d9d9; stroke-width: 1; }
    #clip-timer .track { fill: none; stroke: #e4e4e4; stroke-width: 3; }
    #clip-timer .bar {
      fill: none; stroke: #6b6b6b; stroke-width: 3; stroke-linecap: round;
      transform: rotate(-90deg); transform-origin: 17px 17px;
    }
    #clip-timer .check {
      fill: none; stroke: #ffffff; stroke-width: 2.6; stroke-linecap: round;
      stroke-linejoin: round; opacity: 0; transition: opacity 0.25s;
    }
    #clip-timer.paused .bar { opacity: 0.4; }
    #clip-timer.done .disk { fill: #6b6b6b; stroke: #6b6b6b; }
    #clip-timer.done .track, #clip-timer.done .bar { opacity: 0; }
    #clip-timer.done .check { opacity: 1; }
  `;
  document.head.appendChild(style);

  const timer = document.createElement("div");
  timer.id = "clip-timer";
  timer.innerHTML = `
    <svg width="34" height="34" viewBox="0 0 34 34" aria-hidden="true">
      <circle class="disk" cx="17" cy="17" r="16"></circle>
      <circle class="track" cx="17" cy="17" r="${RADIUS}"></circle>
      <circle class="bar" cx="17" cy="17" r="${RADIUS}"
        stroke-dasharray="${CIRCUMFERENCE}" stroke-dashoffset="${CIRCUMFERENCE}"></circle>
      <path class="check" d="M11 17.5 L15.2 21.5 L23 13"></path>
    </svg>`;
  document.body.appendChild(timer);
  const bar = timer.querySelector(".bar");

  function currentClip() {
    const slide = Reveal.getCurrentSlide();
    const background = slide && slide.slideBackgroundContentElement;
    return background ? background.querySelector("video") : null;
  }

  function update() {
    const clip = currentClip();
    let fraction = 0;
    let state = "playing";
    if (clip && clip.duration > 0) {
      fraction = Math.min(clip.currentTime / clip.duration, 1);
      if (clip.ended || fraction >= 0.999) {
        state = "done";
      } else if (clip.paused && clip.currentTime > 0) {
        state = "paused";
      }
    }
    timer.classList.toggle("done", state === "done");
    timer.classList.toggle("paused", state === "paused");
    bar.setAttribute("stroke-dashoffset", String(CIRCUMFERENCE * (1 - fraction)));
    timer.dataset.state = state;
    timer.dataset.fraction = fraction.toFixed(3);
    requestAnimationFrame(update);
  }

  function start() {
    Reveal.addKeyBinding(
      { keyCode: 84, key: "T", description: "Show or hide the animation timer" },
      () => timer.classList.toggle("hidden"),
    );
    requestAnimationFrame(update);
  }

  if (Reveal.isReady()) {
    start();
  } else {
    Reveal.on("ready", start);
  }
})();
