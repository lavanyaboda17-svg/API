function toggleRead(el) {
  const parent = el.parentElement;
  const shortText = parent.querySelector('.short-text');
  const fullText = parent.querySelector('.full-text');

  if (fullText.classList.contains('d-none')) {
    fullText.classList.remove('d-none');
    shortText.classList.add('d-none');
    el.textContent = 'Read Less';
  } else {
    fullText.classList.add('d-none');
    shortText.classList.remove('d-none');
    el.textContent = 'Read More';
  }
}

document.addEventListener('DOMContentLoaded', function () {
  const images = document.querySelectorAll('img.lazy-fade');
  images.forEach(function (img) {
    if (img.complete) {
      img.classList.add('loaded');
    } else {
      img.addEventListener('load', function () {
        img.classList.add('loaded');
      });
    }
  });
});