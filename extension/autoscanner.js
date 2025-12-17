(async function () {
  try {
    const { autoScanEnabled = true } = await new Promise(r =>
      chrome.storage.sync.get({ autoScanEnabled: true }, r)
    );
    if (!autoScanEnabled) return;
  } catch (e) {}

  await new Promise(r => setTimeout(r, 2000));

  const allLinks = document.querySelectorAll('a[href^="http"]:not([href*="google.com"])');

  const markedDomains = new Set();

  function getRootDomain(url) {
    try {
      const hostname = new URL(url).hostname;
      return hostname.replace(/^www\./, '');
    } catch {
      return null;
    }
  }

  const scanLink = async (link) => {
    let url = link.href;
    try {
      const u = new URL(url);
      if (u.searchParams.has('q')) url = u.searchParams.get('q');
    } catch {}

    const domain = getRootDomain(url);
    if (!domain || markedDomains.has(domain)) return;

    if (domain === "youtube.com" || (domain === "tiktok.com")) return;

    const block1 = link.closest(`
      div.g,                    
      div.yuRUbf,
      div[data-hveid],        
      div[data-ved],            
      div[data-snc],
      div[data-sokw],          
      div[data-attrid]        
    `);

    const firstExternalLink = block1.querySelector('a[href^="http"]:not([href*="google.com"])');
    if (!firstExternalLink || firstExternalLink !== link) return;

    markedDomains.add(domain);

    try {
      const res = await fetch("http://localhost:3000/detectphishing", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!res.ok) throw new Error();
      const data = await res.json();

      let borderColor = "gray";
      if (data.prediction === 1 && data.probability[0][0] < 0.30) borderColor = "green";
      else if (data.prediction === -1 && data.probability[0][0] >= 0.70) borderColor = "red";
      else borderColor = "orange";

      link.style.cssText = `
        outline: 2px solid ${borderColor} !important;
        outline-offset: 2px !important;
        border-radius: 4px !important;
        box-shadow: 0 0 6px ${borderColor}aa !important;
      `;

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

  // Chạy tuần tự
  for (const link of allLinks) {
    await scanLink(link);
    await new Promise(r => setTimeout(r, 150));
  }
})();