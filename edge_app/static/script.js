const historyList = document.getElementById("historyList");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");
const captureBtn = document.getElementById("captureBtn");
const toggleAlarmBtn = document.getElementById("toggleAlarmBtn");

const movementsToday = document.getElementById("movementsToday");
const alarmsToday = document.getElementById("alarmsToday");
const lastDetection = document.getElementById("lastDetection");

const generalStatus = document.getElementById("generalStatus");
const mainMessage = document.getElementById("mainMessage");
const mainDescription = document.getElementById("mainDescription");
const stateIcon = document.getElementById("stateIcon");
const stateTitle = document.getElementById("stateTitle");
const stateText = document.getElementById("stateText");

let alarmActive = false;

// Funciones de tiempo
function currentTime() {
  return new Date().toLocaleTimeString("es-CO", {hour: "2-digit", minute: "2-digit", second: "2-digit"});
}
function shortTime(fecha) {
  const d = new Date(fecha);
  return d.toLocaleTimeString("es-CO", {hour: "2-digit", minute: "2-digit"});
}

// Actualiza reloj de la cámara
setInterval(() => {
  const videoTime = document.getElementById("videoTime");
  if(videoTime) videoTime.textContent = currentTime();
}, 1000);

// --- Funciones de actualización ---
async function fetchEstado() {
  const res = await fetch("/api/estado");
  const data = await res.json();

  generalStatus.textContent = data.alarma === "ON" ? "Alerta activa" : "Sistema protegido";
  generalStatus.className = data.alarma === "ON" ? "status-pill alert" : "status-pill safe";

  stateIcon.textContent = data.alarma === "ON" ? "🚨" : "✅";
  stateTitle.textContent = data.alarma === "ON" ? "Alerta" : "Seguro";
  stateText.textContent = data.alarma === "ON"
    ? "Se recomienda revisar el historial y la evidencia capturada."
    : "Cámara, sensores y alarma funcionando correctamente.";

  // Actualiza streaming
  const cameraStream = document.getElementById("cameraStream");
  if(cameraStream) cameraStream.src = data.stream_url;
}

async function fetchEventos() {
  const res = await fetch("/api/eventos");
  const eventos = await res.json();

  historyList.innerHTML = "";
  let movimientos = 0;
  let alarmas = 0;
  let ultimaHora = "--:--";

  if(eventos.length === 0){
    historyList.innerHTML = `<div class="history-item">
        <div class="history-icon">📭</div>
        <div><strong>Sin historial</strong><p>No hay movimientos registrados por el momento.</p></div>
        <span class="history-time">--:--</span>
      </div>`;
  }

  eventos.forEach(ev => {
    if(ev.tipo === "entrada" || ev.tipo === "sensor" || ev.tipo === "puerta") {
      movimientos++;
      ultimaHora = shortTime(ev.fecha);
    }
    if(ev.tipo === "alarma") alarmas++;

    const div = document.createElement("div");
    div.className = "history-item";
    div.innerHTML = `
      <div class="history-icon">${ev.tipo === "alarma" ? "🚨" : "✅"}</div>
      <div><strong>${ev.tipo.toUpperCase()}</strong>: ${ev.descripcion}</div>
      <span class="history-time">${shortTime(ev.fecha)}</span>
    `;
    if(ev.imagen){
      const img = document.createElement("img");
      img.src = ev.imagen;
      img.style.maxWidth = "200px";
      div.appendChild(img);
    }
    historyList.appendChild(div);
  });

  movementsToday.textContent = movimientos;
  alarmsToday.textContent = alarmas;
  lastDetection.textContent = ultimaHora;
}

// --- Botones ---
async function toggleAlarm() {
  if(alarmActive){
    await fetch("/api/alarma/off");
    alarmActive = false;
  } else {
    await fetch("/api/alarma/on");
    alarmActive = true;
  }
  await fetchEstado();
  await fetchEventos();
}

toggleAlarmBtn.addEventListener("click", toggleAlarm);
captureBtn.addEventListener("click", fetchEventos);
clearHistoryBtn.addEventListener("click", () => historyList.innerHTML = "");

// --- Auto actualización ---
setInterval(() => {
  fetchEstado();
  fetchEventos();
}, 2000);

fetchEstado();
fetchEventos();