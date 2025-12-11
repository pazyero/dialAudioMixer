const list = document.getElementById("appList");
const refreshBtn = document.getElementById("refresh");

async function getVolume(pid) {
  try {
    const r = await fetch(`http://127.0.0.1:8823/volume?pid=${pid}&delta=0`);
    const data = await r.json();
    if (data.volume !== undefined) {
      return Math.round(data.volume * 100);
    }
  } catch (e) {
    console.error('getVolume error', e);
  }
  return null;
}

async function loadApps() {
  try {
    const r = await fetch("http://127.0.0.1:8823/apps");
    const apps = await r.json();
    list.innerHTML = "";
    for (const a of apps) {
      const li = document.createElement("li");
      const volPercent = await getVolume(a.pid);
      const volStr = volPercent !== null ? volPercent + '%' : '--';
      li.innerHTML = `${a.name} (PID ${a.pid}) - <span id="vol-${a.pid}">` + volStr + `</span> <button data-name="${a.name}">Exclude</button>`;
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
