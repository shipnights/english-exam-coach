// Live word count and a count-up timer for the writing page. No dependencies.
(function () {
  var form = document.getElementById("write-form");
  if (!form) return;

  var box = document.getElementById("response_text");
  var words = document.getElementById("wordcount");
  var timer = document.getElementById("timer");
  var seconds = document.getElementById("seconds_used");
  var minWords = parseInt(form.dataset.minWords, 10);
  var maxWords = form.dataset.maxWords ? parseInt(form.dataset.maxWords, 10) : null;
  var limit = parseInt(form.dataset.minutes, 10) * 60;
  var started = Date.now();

  function countWords(text) {
    var found = text.match(/[A-Za-z]+(?:['’][A-Za-z]+)*/g);
    return found ? found.length : 0;
  }

  function updateWords() {
    var n = countWords(box.value);
    words.textContent = n + (n === 1 ? " word" : " words");
    var off = n < minWords || (maxWords !== null && n > maxWords);
    words.classList.toggle("off", off && n > 0);
  }

  function tick() {
    var elapsed = Math.floor((Date.now() - started) / 1000);
    var m = Math.floor(elapsed / 60);
    var s = elapsed % 60;
    timer.textContent = m + ":" + (s < 10 ? "0" : "") + s;
    timer.classList.toggle("off", elapsed > limit);
    seconds.value = elapsed;
  }

  box.addEventListener("input", updateWords);
  form.addEventListener("submit", tick);
  updateWords();
  tick();
  setInterval(tick, 1000);
})();
