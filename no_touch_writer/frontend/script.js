window.onload = function () {
  const startBtn = document.getElementById("start");
  const undoBtn = document.getElementById("undo");
  const docDiv = document.getElementById("doc");

  let recognition;
  let isListening = false;

  if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    let lastSpoken = '';

    recognition.onresult = function (event) {
      const result = event.results[event.resultIndex];
      if (result.isFinal) {
        lastSpoken = result[0].transcript.trim();
        fetch("http://localhost:8000/voice", {
          method: "POST",
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: lastSpoken })
        }).then(refreshDoc);

        recognition.stop(); // Let onend handle restart
      }
    };

    recognition.onend = () => {
      if (isListening) {
        setTimeout(() => {
          recognition.start();
        }, 800);
      }
    };

    startBtn.onclick = () => {
      if (isListening) {
        recognition.stop();
        startBtn.innerText = "🎤 Start Listening";
      } else {
        recognition.start();
        startBtn.innerText = "⏹️ Stop Listening";
      }
      isListening = !isListening;
    };
  }

  undoBtn.onclick = () => {
    fetch("http://localhost:8000/undo", {
      method: "POST"
    }).then(refreshDoc);
  };

  function refreshDoc() {
    fetch("http://localhost:8000/doc")
      .then(res => res.json())
      .then(data => {
        docDiv.innerHTML = "";
        data.content.forEach(block => {
          let el;
          if (block.type === "heading") {
            el = document.createElement(`h${block.level || 2}`);
          } else if (block.type === "paragraph") {
            el = document.createElement("p");
          } else if (block.type === "bullet") {
            el = document.createElement("li");
          } else {
            el = document.createElement("div");
          }
          el.innerText = block.content;
          docDiv.appendChild(el);
        });
      });
  }

  refreshDoc();
};