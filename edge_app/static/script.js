const historyList = document.getElementById("historyList");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");
const captureBtn = document.getElementById("captureBtn");
const toggleAlarmBtn = document.getElementById("toggleAlarmBtn");
const heroAlarmBtn = document.getElementById("heroAlarmBtn");
const resetMovementBtn = document.getElementById("resetMovementBtn");

const movementsToday = document.getElementById("movementsToday");
const alarmsToday = document.getElementById("alarmsToday");
const lastDetection = document.getElementById("lastDetection");
const lastDetectionText = document.getElementById("lastDetectionText");

const generalStatus = document.getElementById("generalStatus");
const generalStatusText = document.getElementById("generalStatusText");
const mainMessage = document.getElementById("mainMessage");
const mainDescription = document.getElementById("mainDescription");
const stateIcon = document.getElementById("stateIcon");
const stateTitle = document.getElementById("stateTitle");
const stateText = document.getElementById("stateText");

const detectionBox = document.getElementById("detectionBox");
const movementDetail = document.getElementById("movementDetail");
const alertBox = document.getElementById("alertBox");
const alertIcon = document.getElementById("alertIcon");
const alertTitle = document.getElementById("alertTitle");
const alertText = document.getElementById("alertText");

const riskLevel = document.getElementById("riskLevel");
const lastAction = document.getElementById("lastAction");
const systemResponse = document.getElementById("systemResponse");

const cameraStatus = document.getElementById("cameraStatus");
const sensorStatus = document.getElementById("sensorStatus");
const alarmDeviceState = document.getElementById("alarmDeviceState");
const lockStatus = document.getElementById("lockStatus");
const lockDeviceStatus = document.getElementById("lockDeviceStatus");

const evidenceGrid = document.getElementById("evidenceGrid");
const cameraStream = document.getElementById("cameraStream");

let alarmActive = false;
let streamConfigured = false;
let activityChart = null;

function currentTime() {
  return new Date().toLocaleTimeString("es-CO", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  });
}

function parseFecha(fecha) {
  if (!fecha) return null;

  const normalized = String(fecha).replace(" ", "T");
  const date = new Date(normalized);

  if (Number.isNaN(date.getTime())) return null;
  return date;
}

function shortTime(fecha) {
  const date = parseFecha(fecha);
  if (!date) return "--:--";

  return date.toLocaleTimeString("es-CO", {
    hour: "2-digit",
    minute: "2-digit"
  });
}

function isToday(fecha) {
  const date = parseFecha(fecha);
  if (!date) return false;

  const today = new Date();

  return (
    date.getFullYear() === today.getFullYear() &&
    date.getMonth() === today.getMonth() &&
    date.getDate() === today.getDate()
  );
}

function setBadge(el, text, type) {
  if (!el) return;

  el.textContent = text;
  el.className = `badge ${type}`;
}

function setStatusPill(isAlert) {
  if (!generalStatus) return;

  generalStatus.className = isAlert ? "status-pill alert" : "status-pill safe";

  if (generalStatusText) {
    generalStatusText.textContent = isAlert ? "Alerta activa" : "Sistema protegido";
  }
}

function setAlarmButtons(isActive) {
  const text = isActive ? "Apagar alarma" : "Activar alarma manual";

  if (toggleAlarmBtn) {
    toggleAlarmBtn.textContent = text;
  }

  if (heroAlarmBtn) {
    heroAlarmBtn.textContent = isActive ? "Apagar alarma" : "Activar alarma";
  }
}

function updateClock() {
  const videoTime = document.getElementById("videoTime");

  if (videoTime) {
    videoTime.textContent = currentTime();
  }
}

function updateActivityChart(eventos) {
  const canvas = document.getElementById("activityChart");
  if (!canvas || typeof Chart === "undefined") return;

  const hours = Array.from({ length: 24 }, (_, index) => index);
  const counts = hours.map(() => 0);

  eventos.forEach((ev) => {
    if (!["entrada", "sensor", "puerta", "movimiento"].includes(ev.tipo)) return;

    const date = parseFecha(ev.fecha);
    if (!date || !isToday(ev.fecha)) return;

    counts[date.getHours()] += 1;
  });

  const labels = hours.map((hour) => `${String(hour).padStart(2, "0")}:00`);

  if (!activityChart) {
    activityChart = new Chart(canvas, {
      type: "bar",
      data: {
        labels,
        datasets: [{
          label: "Movimientos",
          data: counts,
          backgroundColor: "#2563eb",
          borderRadius: 8
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0
            }
          }
        }
      }
    });

    return;
  }

  activityChart.data.datasets[0].data = counts;
  activityChart.update();
}

async function fetchEstado() {
  try {
    const res = await fetch("/api/estado");
    const data = await res.json();

    const alarmaOn = data.alarma === "ON";
    const movimiento = Boolean(data.movimiento_detectado);

    alarmActive = alarmaOn;

    setStatusPill(alarmaOn || movimiento);
    setAlarmButtons(alarmaOn);

    if (mainMessage) {
      mainMessage.textContent = alarmaOn
        ? "Alarma activa"
        : movimiento
          ? "Movimiento detectado"
          : "Todo está bajo control";
    }

    if (mainDescription) {
      mainDescription.textContent = alarmaOn
        ? "El sistema activó la alerta. Revisa la cámara, historial y evidencias recientes."
        : movimiento
          ? data.ultimo_movimiento || "La cámara detectó actividad en la entrada principal."
          : "No se han detectado actividades sospechosas recientes. El sistema continúa monitoreando la cámara, sensores y cerradura.";
    }

    if (stateIcon) {
      stateIcon.textContent = alarmaOn ? "🚨" : movimiento ? "⚠️" : "✅";
    }

    if (stateTitle) {
      stateTitle.textContent = alarmaOn ? "Alerta" : movimiento ? "Movimiento" : "Seguro";
    }

    if (stateText) {
      stateText.textContent = alarmaOn
        ? "Se recomienda revisar el historial y la evidencia capturada."
        : movimiento
          ? "Actividad detectada en la cámara principal."
          : "Cámara, sensores y alarma funcionando correctamente.";
    }

    if (detectionBox) {
      detectionBox.classList.toggle("show", movimiento);
    }

    if (movementDetail) {
      const percent = data.porcentaje_movimiento ?? 0;
      movementDetail.textContent = `${data.ultimo_movimiento || "Sin movimiento"} (${percent}%)`;
    }

    if (alertBox) {
      alertBox.classList.toggle("active", alarmaOn || movimiento);
    }

    if (alertIcon) {
      alertIcon.textContent = alarmaOn ? "🚨" : movimiento ? "🟡" : "🟢";
    }

    if (alertTitle) {
      alertTitle.textContent = alarmaOn
        ? "Alarma activa"
        : movimiento
          ? "Movimiento detectado"
          : "No hay una alarma activa";
    }

    if (alertText) {
      alertText.textContent = alarmaOn
        ? "El sistema está en modo alerta."
        : movimiento
          ? data.ultimo_movimiento || "Se detectó actividad reciente en la entrada."
          : "El sistema está monitoreando normalmente.";
    }

    if (riskLevel) {
      riskLevel.textContent = alarmaOn ? "Alto" : movimiento ? "Medio" : "Bajo";
    }

    if (lastAction) {
      lastAction.textContent = movimiento
        ? "Registro de movimiento"
        : data.ultimo_evento || "Registro local";
    }

    if (systemResponse) {
      systemResponse.textContent = alarmaOn
        ? "Alarma activada"
        : movimiento
          ? "Evidencia registrada"
          : "Monitoreo activo";
    }

    setBadge(
      cameraStatus,
      data.camara && !String(data.camara).toLowerCase().includes("error") ? "Activa" : "Sin datos",
      data.camara && !String(data.camara).toLowerCase().includes("error") ? "ok" : "warning"
    );

    setBadge(sensorStatus, "Activo", "ok");
    setBadge(alarmDeviceState, alarmaOn ? "Activa" : "En espera", alarmaOn ? "danger" : "warning");

    if (lockStatus) lockStatus.textContent = alarmaOn ? "Bloqueada" : "Bloqueada";
    setBadge(lockDeviceStatus, "Bloqueada", "danger");

    if (cameraStream && data.stream_url && !streamConfigured) {
      cameraStream.src = data.stream_url;
      streamConfigured = true;
    }
  } catch (error) {
    console.error("Error consultando estado:", error);

    setBadge(cameraStatus, "Error", "danger");
  }
}

async function fetchEventos() {
  try {
    const res = await fetch("/api/eventos");
    const eventos = await res.json();

    if (!historyList) return;

    historyList.innerHTML = "";

    let movimientos = 0;
    let alarmas = 0;
    let ultimaHora = "--:--";
    let ultimaDescripcion = "Sin movimiento registrado";

    const evidencias = [];

    eventos.forEach((ev) => {
      const esMovimiento = ["entrada", "sensor", "puerta", "movimiento"].includes(ev.tipo);
      const esAlarma = ev.tipo === "alarma" || ev.resultado === "ON";

      if (isToday(ev.fecha) && esMovimiento) {
        movimientos += 1;

        if (ultimaHora === "--:--") {
          ultimaHora = shortTime(ev.fecha);
          ultimaDescripcion = ev.descripcion || "Movimiento registrado";
        }
      }

      if (isToday(ev.fecha) && esAlarma) {
        alarmas += 1;
      }

      if (ev.imagen) {
        evidencias.push(ev);
      }

      const item = document.createElement("div");
      item.className = "history-item";

      const icon = esAlarma ? "🚨" : esMovimiento ? "⚠️" : "✅";

      item.innerHTML = `
        <div class="history-icon">${icon}</div>
        <div>
          <strong>${String(ev.tipo || "evento").toUpperCase()}</strong>
          <p>${ev.descripcion || "Evento registrado"}</p>
          ${ev.resultado ? `<p>${ev.resultado}</p>` : ""}
        </div>
        <span class="history-time">${shortTime(ev.fecha)}</span>
      `;

      historyList.appendChild(item);
    });

    if (eventos.length === 0) {
      historyList.innerHTML = `
        <div class="history-item">
          <div class="history-icon">📭</div>
          <div>
            <strong>Sin historial</strong>
            <p>No hay movimientos registrados por el momento.</p>
          </div>
          <span class="history-time">--:--</span>
        </div>
      `;
    }

    if (movementsToday) movementsToday.textContent = movimientos;
    if (alarmsToday) alarmsToday.textContent = alarmas;
    if (lastDetection) lastDetection.textContent = ultimaHora;
    if (lastDetectionText) lastDetectionText.textContent = ultimaDescripcion;

    renderEvidencias(evidencias.slice(0, 6));
    updateActivityChart(eventos);
  } catch (error) {
    console.error("Error consultando eventos:", error);
  }
}

function renderEvidencias(evidencias) {
  if (!evidenceGrid) return;

  evidenceGrid.innerHTML = "";

  if (evidencias.length === 0) {
    evidenceGrid.innerHTML = `
      <article class="evidence-card">
        <div>📷</div>
        <strong>Sin capturas</strong>
        <p>No hay evidencias recientes.</p>
      </article>
    `;
    return;
  }

  evidencias.forEach((ev) => {
    const card = document.createElement("article");
    card.className = "evidence-card";

    card.innerHTML = `
      <div>
        <img src="${ev.imagen}" alt="Evidencia capturada" style="width:100%;height:100%;object-fit:cover;border-radius:16px;">
      </div>
      <strong>${shortTime(ev.fecha)}</strong>
      <p>${ev.descripcion || "Captura registrada"}</p>
    `;

    evidenceGrid.appendChild(card);
  });
}

async function toggleAlarm() {
  try {
    if (alarmActive) {
      await fetch("/api/alarma/off");
      alarmActive = false;
    } else {
      await fetch("/api/alarma/on");
      alarmActive = true;
    }

    await fetchEstado();
    await fetchEventos();
  } catch (error) {
    console.error("Error cambiando alarma:", error);
  }
}

async function resetMovement() {
  try {
    await fetch("/api/movimiento/reset");
    await fetchEstado();
  } catch (error) {
    console.error("Error reiniciando movimiento:", error);
  }
}

function clearHistoryView() {
  if (!historyList) return;

  historyList.innerHTML = `
    <div class="history-item">
      <div class="history-icon">📭</div>
      <div>
        <strong>Vista limpia</strong>
        <p>Se limpió la vista local. La base de datos conserva los eventos.</p>
      </div>
      <span class="history-time">${currentTime()}</span>
    </div>
  `;
}

if (toggleAlarmBtn) toggleAlarmBtn.addEventListener("click", toggleAlarm);
if (heroAlarmBtn) heroAlarmBtn.addEventListener("click", toggleAlarm);
if (resetMovementBtn) resetMovementBtn.addEventListener("click", resetMovement);
if (captureBtn) captureBtn.addEventListener("click", fetchEventos);
if (clearHistoryBtn) clearHistoryBtn.addEventListener("click", clearHistoryView);

updateClock();
setInterval(updateClock, 1000);

fetchEstado();
fetchEventos();

setInterval(fetchEstado, 1000);
setInterval(fetchEventos, 3000);