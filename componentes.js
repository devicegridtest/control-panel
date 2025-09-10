// componentes.js - Precios de cripto: robusto, con reintentos, sin bloqueos
// v1.1 - Optimizado para DeviceGrid v8.0 PRO

// Lista de criptomonedas a monitorear
const coins = [
  { id: "bitcoin", cgId: "bitcoin", symbol: "BTC" },
  { id: "ethereum", cgId: "ethereum", symbol: "ETH" },
  { id: "dogecoin", cgId: "dogecoin", symbol: "DOGE" },
  { id: "solana", cgId: "solana", symbol: "SOL" },
  { id: "litecoin", cgId: "litecoin", symbol: "LTC" },
  { id: "ripple", cgId: "ripple", symbol: "XRP" },
  { id: "nexa", cgId: "nexacoin", symbol: "NEXA" },
  { id: "nodle", cgId: "nodle-network", symbol: "NODL" }
];

// Almacena el último cambio para detectar variaciones
const lastChange = {};

// URL de la API de CoinGecko
const COINGECKO_URL = `https://api.coingecko.com/api/v3/simple/price?ids=${coins.map(c => c.cgId).join(",")}&vs_currencies=usd&include_24hr_change=true`;

// Control de errores y reintentos
let fetchFailures = 0;
const MAX_FAILURES = 5;
const BASE_RETRY_DELAY = 30_000; // 30 segundos
let retryTimeout = null;
let isFetching = false; // Evita múltiples solicitudes simultáneas

// Función principal: obtener precios
async function fetchPrices() {
  if (isFetching) {
    console.debug("🟡 fetchPrices ya en ejecución, omitiendo nueva llamada...");
    return;
  }

  isFetching = true;

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10_000); // 10s timeout

    const res = await fetch(COINGECKO_URL, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'DeviceGrid-Control-Panel/v8.0 (contact@devicegridtest.org)'
      },
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }

    const data = await res.json();
    fetchFailures = 0; // Reiniciar contador en éxito

    coins.forEach(({ id, cgId }) => {
      const elements = document.querySelectorAll(`#${id}`);
      
      if (!elements.length) {
        console.warn(`⚠️ No se encontró elemento con ID: ${id}`);
        return;
      }
      if (!data[cgId]) {
        console.warn(`⚠️ No hay datos para: ${id}`);
        elements.forEach(el => {
          el.querySelector(".price")?.textContent = "N/A";
          el.querySelector(".change")?.textContent = "0%";
          el.querySelector(".arrow")?.replaceWith(createErrorArrow());
        });
        return;
      }

      const price = data[cgId].usd?.toFixed(4);
      const change = data[cgId].usd_24h_change?.toFixed(2);

      // 🔼🔽 Determinar flecha y color
      let arrowSymbol, arrowColor;
      if (change > 0) {
        arrowSymbol = "▲";
        arrowColor = "text-green-400";
      } else if (change < 0) {
        arrowSymbol = "▼";
        arrowColor = "text-red-400";
      } else {
        arrowSymbol = "─";
        arrowColor = "text-gray-400";
      }

      // 🎯 Actualizar todos los elementos (scroll infinito)
      elements.forEach(el => {
        const priceEl = el.querySelector(".price");
        const changeEl = el.querySelector(".change");
        const arrowEl = el.querySelector(".arrow");

        if (priceEl) priceEl.textContent = price ? `$${price}` : "N/A";
        if (changeEl) changeEl.textContent = change ? `${change}%` : "0%";

        if (arrowEl) {
          arrowEl.textContent = arrowSymbol;
          arrowEl.className = "arrow font-bold"; // reset
          arrowEl.classList.add(arrowColor);

          // 💥 Efecto de resaltado si cambió el valor
          const key = `${id}-${cgId}`;
          const prev = lastChange[key];
          if (prev !== undefined && prev !== change) {
            el.classList.add("highlight-change");
            setTimeout(() => el.classList.remove("highlight-change"), 800);
          }
          lastChange[key] = change;
        }
      });
    });

    console.log("✅ Precios actualizados correctamente");

  } catch (err) {
    fetchFailures++;

    if (err.name === 'AbortError') {
      console.warn("⚠️ Timeout al conectar con CoinGecko (10s)");
    } else if (err.message.includes('429')) {
      console.error("❌ Too Many Requests - Rate limit alcanzado");
    } else if (err.message.includes('Failed to fetch')) {
      console.error("🌐 No hay conexión a internet o bloqueo de red");
    } else {
      console.error(`❌ Error desconocido (intentos: ${fetchFailures}):`, err.message);
    }

    // 🔄 Reintento exponencial (max 5 min)
    const delay = Math.min(BASE_RETRY_DELAY * Math.pow(2, fetchFailures), 5 * 60 * 1000);
    console.log(`🔁 Reintentando en ${Math.round(delay / 1000)} segundos...`);

    if (retryTimeout) clearTimeout(retryTimeout);
    retryTimeout = setTimeout(() => {
      isFetching = false;
      fetchPrices();
    }, delay);

  } finally {
    isFetching = false;
  }
}

// ✅ Crear flecha de error
function createErrorArrow() {
  const span = document.createElement('span');
  span.className = 'arrow text-yellow-400 font-bold';
  span.textContent = '⚠️';
  return span;
}

// 🌈 Inyectar estilos para animación de cambio
const style = document.createElement('style');
style.textContent = `
  .highlight-change {
    animation: highlightChange 0.8s ease-out;
  }
  @keyframes highlightChange {
    0% { background-color: rgba(34, 197, 94, 0.1); }
    50% { background-color: rgba(34, 197, 94, 0.3); }
    100% { background-color: transparent; }
  }
  .highlight-change .arrow.text-red-400 ~ * {
    animation: highlightChangeRed 0.8s ease-out;
  }
  @keyframes highlightChangeRed {
    0% { background-color: rgba(239, 68, 68, 0.1); }
    50% { background-color: rgba(239, 68, 68, 0.3); }
    100% { background-color: transparent; }
  }
`;
document.head.appendChild(style);

// 👇 Iniciar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  console.log("🚀 Iniciando componente de precios de cripto...");

  // Primera carga
  fetchPrices();

  // Actualización periódica (solo si no hay errores persistentes)
  window.cryptoInterval = setInterval(() => {
    if (fetchFailures < MAX_FAILURES) {
      fetchPrices();
    } else {
      console.log("🟡 Demasiados errores. Esperando recuperación automática...");
    }
  }, 30_000); // Cada 30 segundos

  // Recuperación manual (opcional)
  window.retryCryptoFetch = () => {
    if (fetchFailures > 0) {
      console.log("🔁 Reintento manual activado...");
      fetchPrices();
    }
  };
});

// 🧹 Limpieza al cerrar
window.addEventListener('beforeunload', () => {
  if (window.cryptoInterval) clearInterval(window.cryptoInterval);
  if (retryTimeout) clearTimeout(retryTimeout);
  console.log("🧹 Recursos de precios de cripto limpiados.");
});