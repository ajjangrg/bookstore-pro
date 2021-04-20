var modal = document.getElementById("are-you-sure-modal");

if (modal) {
  var btn = document.getElementById("deleteButton");
  var span = document.getElementsByClassName("modal-close")[0];
  let urlToGo = "";

  // Show Modal
  btn.onclick = function () {
    modal.style.display = "block";
    urlToGo = this.getAttribute("data-url");
  };

  // Close Button

  span.onclick = function () {
    onClose();
  };

  // Modal Buttons
  var cancelButton = document.getElementById("cancel-button");
  var acceptButton = document.getElementById("accept-button");

  // Cancel Button
  cancelButton.onclick = function () {
    onClose();
  };

  // Accept BUtton
  // Get the url and redirect
  acceptButton.onclick = function () {
    let url = getLink();

    window.location.href = url;
  };

  window.onclick = function (event) {
    if (event.target == modal) {
      onClose();
    }
  };

  function onClose() {
    modal.style.display = "none";
  }

  function getLink() {
    let base_url = window.location.origin;

    let url = base_url + "/" + urlToGo;

    return url;
  }
}
