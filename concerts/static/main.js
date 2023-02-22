function auto_grow_textarea(element) {
  if (element.scrollHeight > 65) {
    element.style.height = 65 + "px";
    element.style.height = element.scrollHeight + "px";
  }
}
