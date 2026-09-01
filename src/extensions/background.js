chrome.webNavigation.onCommitted.addListener((details) => {
  // Evita sub-elementos, solo analiza la pestaña principal
  if (details.frameId === 0) {
    fetch('http://127.0.0.1:61103/analizar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: details.url })
    }).catch(err => console.log("Gandalf Python no está escuchando en el puerto 61103..."));
  }
});
