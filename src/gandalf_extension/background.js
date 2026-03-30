chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        fetch('http://127.0.0.1:5000/analizar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: tab.url })
        })
        .then(response => response.json())
        .then(data => console.log('Gandalf dice:', data))
        .catch(error => console.error('Error conectando con Gandalf:', error));
    }
});