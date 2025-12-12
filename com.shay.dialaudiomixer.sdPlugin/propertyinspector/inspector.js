const list = document.getElementById("appList");
const refreshBtn = document.getElementById("refresh");

async function loadApps() {
  try {
    const r = await fetch("http://127.0.0.1:8823/apps");
    const apps = await r.json();
    list.innerHTML = "";
    for (const a of apps) {
      const li = document.createElement("li");
      const volume = Math.round(a.volume * 100);
      li.innerHTML = `${a.name} - <span id="vol-${a.name}">` +  volume + '%' + `</span> <button data-name="${a.name}">Exclude</button>`;
      list.appendChild(li);
    }
  } catch (e) {
    console.error('loadApps error', e);
    list.innerHTML = '<li>Error loading apps</li>';
  }
}

refreshBtn.onclick = loadApps;

// Auto-refresh every 3 seconds
setInterval(loadApps, 3000);
loadApps();

list.onclick = async (e) => {
  if (e.target.tagName === "BUTTON") {
    const name = e.target.dataset.name;
    await fetch(`http://127.0.0.1:8823/exclude?name=${name}`);
    await loadApps();
  }
};
