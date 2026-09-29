// ComicCraft Frontend Interactions

document.addEventListener("DOMContentLoaded", function () {
  const comicForm = document.getElementById("comic-form");
  const loadingOverlay = document.getElementById("loading-overlay");
  const loadingStatus = document.getElementById("loading-status");

  if (comicForm && loadingOverlay) {
    comicForm.addEventListener("submit", function () {
      loadingOverlay.style.display = "flex";

      const stages = [
        "Crafting 5-panel storyline outline with Gemini Flash...",
        "Writing dialogues and narration with Gemini 1.5 Pro...",
        "Creating comic illustrations for each panel...",
        "Structuring panel layout and compiling final comic..."
      ];

      let currentStage = 0;
      const interval = setInterval(() => {
        currentStage++;
        if (currentStage < stages.length && loadingStatus) {
          loadingStatus.textContent = stages[currentStage];
        } else {
          clearInterval(interval);
        }
      }, 3500);
    });
  }

  // Handle PDF Download action on preview page
  const downloadBtn = document.getElementById("download-pdf-btn");
  if (downloadBtn) {
    downloadBtn.addEventListener("click", function (e) {
      const pdfUrl = this.getAttribute("data-pdf-url");
      if (pdfUrl) {
        // Trigger browser download in hidden iframe/anchor
        const downloadLink = document.createElement("a");
        downloadLink.href = pdfUrl;
        downloadLink.download = pdfUrl.split("/").pop() || "comic.pdf";
        document.body.appendChild(downloadLink);
        downloadLink.click();
        document.body.removeChild(downloadLink);

        // Redirect user to Export Success page after a short delay
        setTimeout(() => {
          window.location.href = `/export-success?pdf_path=${encodeURIComponent(pdfUrl)}`;
        }, 800);
      }
    });
  }
});
