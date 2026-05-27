const historyList = document.getElementById("historyList");
const clearHistoryBtn = document.getElementById("clearHistoryBtn");
const simulateSuspiciousBtn = document.getElementById("simulateSuspiciousBtn");
const simulateNormalBtn = document.getElementById("simulateNormalBtn");
const captureBtn = document.getElementById("captureBtn");
const toggleAlarmBtn = document.getElementById("toggleAlarmBtn");

const movementsToday = document.getElementById("movementsToday");
const alarmsToday = document.getElementById("alarmsToday");
const lastDetection = document.getElementById("lastDetection");
const lockStatus = document.getElementById("lockStatus");
const videoTime = document.getElementById("videoTime");

const generalStatus = document.getElementById("generalStatus");
const mainMessage = document.getElementById("mainMessage");
const mainDescription = document.getElementById("mainDescription");
const stateIcon = document.getElementById("stateIcon");
const stateTitle = document.getElementById("stateTitle");
const stateText = document.getElementById("stateText");
const detectionBox = document.getElementById("detectionBox");

const alertBox = document.getElementById("alertBox");
const riskLevel = document.getElementById("riskLevel");
const lastAction = document.getElementById("lastAction");
const systemResponse = document.getElementById("systemResponse");
const alarmDeviceState = document.getElementById("alarmDeviceState");
const evidenceGrid = document.getElementById("evidenceGrid");

let movementCount = 12;
let alarmCount = 1;
let alarmActive = false;

const history = [
  {
    icon: "🚶",
    title: "Movimiento normal detectado",
    detail: "Actividad registrada en entrada principal. No se activó alarma.",
    time: "08:42"
  },
  {
    icon: "🚨",
    title: "Actividad sospechosa revisada",
    detail: "La cámara detectó presencia fuera del horario habitual. Se activó bloqueo preventivo.",
    time: "07:15"
  },
  {
    icon: "🔓",
    title: "Acceso autorizado",
    detail: "Ingreso validado correctamente por el sistema local.",
    time: "06:40"
  },
  {
    icon: "📷",
    title: "Captura de evidencia",
    detail: "Imagen almacenada localmente para revisión del cliente.",
    time: "06:38"
  }
];

function currentTime() {
  return new Date().toLocaleTimeString("es-CO", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit"
  });
}

function shortTime() {
  return new Date().toLocaleTimeString("es-CO", {
    hour: "2-digit",
    minute: "2-digit"
  });
}

function updateClock() {
  videoTime.textContent = currentTime();
}

setInterval(updateClock, 1000);
updateClock();

function renderHistory() {
  historyList.innerHTML = "";

  if (history.length === 0) {
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
    return;
  }

  history.forEach((item) => {
    const element = document.createElement("div");
    element.className = "history-item";
    element.innerHTML = `
      <div class="history-icon">${item.icon}</div>
      <div>
        <strong>${item.title}</strong>
        <p>${item.detail}</p>
      </div>
      <span class="history-time">${item.time}</span>
    `;
    historyList.appendChild(element);
  });
}

function addHistory(icon, title, detail) {
  const time = shortTime();
  history.unshift({ icon, title, detail, time });
  lastDetection.textContent = time;
  renderHistory();
}

function setSafeMode() {
  alarmActive = false;
  generalStatus.className = "status-pill safe";
  generalStatus.innerHTML = "<span></span>Sistema protegido";

  mainMessage.textContent = "Todo está bajo control";
  mainDescription.textContent = "No se han detectado actividades sospechosas recientes. El sistema continúa monitoreando la cámara, sensores y cerradura.";

  stateIcon.textContent = "✅";
  stateTitle.textContent = "Seguro";
  stateText.textContent = "Cámara, sensores y alarma funcionando correctamente.";

  alertBox.className = "alert-box";
  alertBox.innerHTML = `
    <div class="alert-icon">🟢</div>
    <div>
      <strong>No hay una alarma activa</strong>
      <p>El sistema está monitoreando normalmente.</p>
    </div>
  `;

  riskLevel.textContent = "Bajo";
  lastAction.textContent = "Registro local";
  systemResponse.textContent = "Monitoreo activo";
  alarmDeviceState.textContent = "En espera";
  alarmDeviceState.className = "badge warning";
  detectionBox.classList.remove("show");
}

function setAlertMode() {
  alarmActive = true;
  generalStatus.className = "status-pill alert";
  generalStatus.innerHTML = "<span></span>Alerta activa";

  mainMessage.textContent = "Actividad sospechosa detectada";
  mainDescription.textContent = "La cámara identificó movimiento inusual. El sistema activó bloqueo preventivo, registró evidencia y notificó la alerta.";

  stateIcon.textContent = "🚨";
  stateTitle.textContent = "Alerta";
  stateText.textContent = "Se recomienda revisar el historial y la evidencia capturada.";

  alertBox.className = "alert-box active";
  alertBox.innerHTML = `
    <div class="alert-icon">🔴</div>
    <div>
      <strong>Alarma activa por posible intrusión</strong>
      <p>Movimiento sospechoso detectado por cámara en la entrada principal.</p>
    </div>
  `;

  riskLevel.textContent = "Alto";
  lastAction.textContent = "Bloqueo preventivo";
  systemResponse.textContent = "Alarma activada";
  alarmDeviceState.textContent = "Activa";
  alarmDeviceState.className = "badge danger";
  detectionBox.classList.add("show");
}

simulateSuspiciousBtn.addEventListener("click", () => {
  movementCount++;
  alarmCount++;

  movementsToday.textContent = movementCount;
  alarmsToday.textContent = alarmCount;
  lockStatus.textContent = "Bloqueada";

  addHistory(
    "🚨",
    "Actividad sospechosa detectada",
    "La cámara detectó movimiento inusual. Se activó alarma, bloqueo preventivo y registro de evidencia."
  );

  setAlertMode();

  setTimeout(() => {
    detectionBox.classList.remove("show");
  }, 5000);
});

simulateNormalBtn.addEventListener("click", () => {
  movementCount++;
  movementsToday.textContent = movementCount;

  addHistory(
    "🚶",
    "Movimiento normal detectado",
    "Actividad registrada sin señales de riesgo. El sistema mantuvo el monitoreo activo."
  );

  setSafeMode();
});

captureBtn.addEventListener("click", () => {
  const time = shortTime();

  addHistory(
    "📷",
    "Captura de evidencia guardada",
    "El cliente generó una captura manual desde el streaming de la cámara."
  );

  const card = document.createElement("div");
  card.className = "evidence-card";
  card.innerHTML = `
    <div>📷</div>
    <strong>Captura manual</strong>
    <p>Guardada desde cámara · ${time}</p>
  `;
  evidenceGrid.prepend(card);
});

toggleAlarmBtn.addEventListener("click", () => {
  if (alarmActive) {
    setSafeMode();
    addHistory("🟢", "Alarma desactivada", "El cliente desactivó la alarma manualmente desde el panel.");
    return;
  }

  alarmCount++;
  alarmsToday.textContent = alarmCount;
  addHistory("🚨", "Alarma manual activada", "El cliente activó la alarma desde el panel de monitoreo.");
  setAlertMode();
});

clearHistoryBtn.addEventListener("click", () => {
  history.length = 0;
  renderHistory();
});

renderHistory();

new Chart(document.getElementById("activityChart"), {
  type: "line",
  data: {
    labels: ["6 AM", "7 AM", "8 AM", "9 AM", "10 AM", "11 AM", "12 PM"],
    datasets: [
      {
        label: "Movimientos",
        data: [1, 3, 4, 2, 1, 0, 1],
        tension: 0.4,
        fill: true,
        borderColor: "#2563eb",
        backgroundColor: "rgba(37, 99, 235, 0.12)",
        pointBackgroundColor: "#2563eb",
        pointRadius: 5
      },
      {
        label: "Alarmas",
        data: [0, 1, 0, 0, 0, 0, 0],
        tension: 0.4,
        fill: true,
        borderColor: "#dc2626",
        backgroundColor: "rgba(220, 38, 38, 0.10)",
        pointBackgroundColor: "#dc2626",
        pointRadius: 5
      }
    ]
  },
  options: {
    responsive: true,
    plugins: {
      legend: {
        labels: {
          usePointStyle: true,
          font: {
            family: "Inter",
            weight: "700"
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        grid: {
          color: "#eef2f7"
        }
      },
      x: {
        grid: {
          display: false
        }
      }
    }
  }
});