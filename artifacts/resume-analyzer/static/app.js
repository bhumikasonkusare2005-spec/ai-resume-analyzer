document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.querySelector("#resume");
  const fileLabel = document.querySelector("#file-label");
  const fileClear = document.querySelector("#file-clear");
  const dropzone = document.querySelector(".dropzone");
  const textArea = document.querySelector("#job_description");
  const count = document.querySelector("#character-count");
  const sampleButton = document.querySelector("#sample-job");

  const updateFile = () => {
    const file = fileInput?.files?.[0];
    if (!file || !fileLabel) return;
    fileLabel.textContent = file.name;
    dropzone?.classList.add("has-file");
    if (fileClear) fileClear.hidden = false;
  };

  fileInput?.addEventListener("change", updateFile);
  fileClear?.addEventListener("click", () => {
    if (!fileInput) return;
    fileInput.value = "";
    if (fileLabel) fileLabel.textContent = "Drop your PDF here";
    dropzone?.classList.remove("has-file");
    fileClear.hidden = true;
  });
  fileClear?.addEventListener("keydown", (event) => {
    if (event.key === "Enter" || event.key === " ") fileClear.click();
  });

  ["dragenter", "dragover"].forEach((eventName) => dropzone?.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.add("is-dragging");
  }));
  ["dragleave", "drop"].forEach((eventName) => dropzone?.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropzone.classList.remove("is-dragging");
  }));
  dropzone?.addEventListener("drop", (event) => {
    const files = event.dataTransfer?.files;
    if (files?.length && fileInput) {
      fileInput.files = files;
      updateFile();
    }
  });

  const updateCount = () => {
    if (textArea && count) count.textContent = `${textArea.value.length.toLocaleString()} / 12,000`;
  };
  textArea?.addEventListener("input", updateCount);
  updateCount();

  sampleButton?.addEventListener("click", () => {
    if (!textArea) return;
    textArea.value = "We are looking for a Product Manager to lead product discovery, user research, and roadmap decisions for a growing analytics platform. You will work cross-functionally with design and engineering, use SQL and experimentation to understand customer behavior, and communicate priorities to stakeholders. Experience with agile delivery, Figma, and customer interviews is a plus.";
    textArea.focus();
    updateCount();
  });

  document.querySelector("#print-report")?.addEventListener("click", () => window.print());
  document.querySelector("#copy-summary")?.addEventListener("click", async (event) => {
    const summary = document.querySelector(".score-verdict p")?.textContent || "";
    try {
      await navigator.clipboard.writeText(summary);
      event.currentTarget.innerHTML = "Copied <span>✓</span>";
      setTimeout(() => { event.currentTarget.innerHTML = "Copy summary <span>↗</span>"; }, 1800);
    } catch {
      event.currentTarget.textContent = "Copy unavailable";
    }
  });
});