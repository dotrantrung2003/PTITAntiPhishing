(async function () {
  
  try {
    const data = await new Promise((resolve) => {
      chrome.storage.sync.get({ autoScanEnabled: true }, resolve);
    });
    if (!data.autoScanEnabled) {
      
      return;
    }
  } catch (err) {
    
  }


  await new Promise(r => setTimeout(r, 1500));

  const links = Array.from(document.querySelectorAll('a[href^="http"]:not([href*=\"google.com\"])'));

  const scanLink = async (link) => {
    const url = link.href;
    try {
      const res = await fetch("http://localhost:3000/detectphishing", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!res.ok) throw new Error("Server error");
      const data = await res.json();

      let borderColor = "gray";
      if (data.prediction === 1 && data.probability[0][0] < 0.30) borderColor = "green";
      else if (data.prediction === -1 && data.probability[0][0] >= 0.70) borderColor = "red";
      else borderColor = "orange";

      link.style.outline = `2px solid ${borderColor}`;
      link.style.outlineOffset = "2px";
      link.title =
        data.prediction === -1 && data.probability[0][0] >= 0.7
          ? "Phishing site!"
          : data.prediction === 1 && data.probability[0][0] < 0.3
          ? "Safe site"
          : "Suspicious site!";
    } catch (err) {
      link.style.outline = "2px dashed gray";
      link.style.outlineOffset = "2px";
      link.title = "Scan failed";
    }
  };

  async function scanInBatches(items, batchSize = 10) {
    for (let i = 0; i < items.length; i += batchSize) {
      const batch = items.slice(i, i + batchSize);
      await Promise.all(batch.map(scanLink));
    }
  }

  await scanInBatches(links, 10);
})();