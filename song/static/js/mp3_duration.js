document.addEventListener("DOMContentLoaded", function () {
  const inputElement = document.getElementById("id_mp3_file");
  const durationElement = document.getElementById("id_duration");

  if (inputElement && durationElement) {
    const audioElement = document.createElement("audio");
    audioElement.controls = true;
    inputElement.parentNode.insertBefore(
      audioElement,
      inputElement.nextSibling
    );

    inputElement.addEventListener("change", function () {
      const file = inputElement.files[0];

      if (file) {
        const objectURL = URL.createObjectURL(file);
        audioElement.src = objectURL;
      }
    });

    audioElement.onloadedmetadata = function () {
      durationElement.value = audioElement.duration;
    };
  }
});
