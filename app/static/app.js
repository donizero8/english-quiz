const text = document.querySelector('#dialogue');
const button = document.querySelector('#generate');
const counter = document.querySelector('#counter');
const error = document.querySelector('#error');
const result = document.querySelector('#result');
const player = document.querySelector('#player');
const meta = document.querySelector('#meta');

function updateCount() {
  const lines = text.value.split('\n').filter(line => line.trim()).length;
  counter.textContent = `${lines} baris dialog`;
}
text.addEventListener('input', updateCount);

button.addEventListener('click', async () => {
  button.disabled = true;
  button.firstChild.textContent = 'Membuat audio ';
  error.textContent = '';
  result.classList.add('hidden');
  try {
    const response = await fetch('/api/generations', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text: text.value})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Gagal membuat audio.');
    player.src = `${data.audio_url}?v=${Date.now()}`;
    meta.textContent = `${data.lines} baris · Voice A + Voice B`;
    result.classList.remove('hidden');
    await player.play().catch(() => {});
  } catch (err) {
    error.textContent = err.message;
  } finally {
    button.disabled = false;
    button.firstChild.textContent = 'Generate audio ';
  }
});
