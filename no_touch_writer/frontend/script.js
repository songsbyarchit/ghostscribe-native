window.onload = function () {
  const startBtn = document.getElementById("start");
  const undoBtn = document.getElementById("undo");
  const docDiv = document.getElementById("doc");
  const redoBtn = document.getElementById("redo");
  const clearBtn = document.getElementById("clear");

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

    redoBtn.onclick = () => {
      fetch("http://localhost:8000/redo", {
        method: "POST"
      }).then(refreshDoc);
    };

    clearBtn.onclick = () => {
      if (confirm("Are you sure you want to clear the page?")) {
        fetch("http://localhost:8000/clear", {
          method: "POST"
        }).then(refreshDoc);
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
data.content.forEach((block, index) => {
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
  const lineWrapper = document.createElement("div");
  lineWrapper.className = "line-wrapper";

  const lineNumber = document.createElement("div");
  lineNumber.className = "line-number";
  lineNumber.innerText = index + 1;
  lineNumber.contentEditable = false;

  el.innerText = block.content;

  lineWrapper.appendChild(lineNumber);
  lineWrapper.appendChild(el);
  docDiv.appendChild(lineWrapper);
});
updateLineNumbers();
      });
  }

function updateLineNumbers() {
  const lines = document.querySelectorAll(".line-wrapper");
  lines.forEach((line, index) => {
    const num = line.querySelector(".line-number");
    if (num) num.innerText = index + 1;
  });
}


  refreshDoc();
};