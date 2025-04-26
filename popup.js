chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const url = tabs[0].url;
    console.log('Popup loaded for URL:', url);
    document.getElementById('urlDisplay').textContent = url;
    document.getElementById('processing').textContent = 'Fetching...';
  
    fetch(`http://localhost:8000/summarize?url=${encodeURIComponent(url)}`)
      .then(res => res.json())
      .then(data => {
        console.log('Received data:', data);
        if (typeof marked === 'undefined') {
          console.error('marked.js is not loaded. Check that marked.min.js is in the extension root and referenced correctly.');
        }
        document.getElementById('processing').textContent = 'Done';
        const html = marked.parse ? marked.parse(data.markdown) : 'Error rendering markdown';
        document.getElementById('output').innerHTML = html;
      })
      .catch(err => {
        console.error('Fetch error:', err);
        document.getElementById('processing').textContent = 'Error';
        document.getElementById('output').textContent = err;
      });
  });