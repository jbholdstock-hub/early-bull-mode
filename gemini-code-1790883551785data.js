async function loadMarketData() {
  try {
    const res = await fetch('data.json?v=' + Date.now()); // prevents cache sticking
    const data = await res.json();
    renderDashboard(data);
  } catch (err) {
    console.error('Could not load market data:', err);
  }
}
window.addEventListener('DOMContentLoaded', loadMarketData);