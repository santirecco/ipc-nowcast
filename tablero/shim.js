// Versión mínima del entorno del tablero para el HTML descargable: datos embebidos, cálculos y dibujos.
(function () {
  const datos = window.IPX_DATOS || {};
  const calcs = {};
  const resultados = {};
  const dibujos = [];
  const estado = (data) => ({ status: 'ok', data, message: null, refreshing: false, truncated: false, meta: null });
  window.dash = {
    colors: ['var(--c0)', 'var(--c1)', 'var(--c2)', 'var(--c3)'],
    data(id) {
      if (id in datos) return estado(datos[id]);
      if (id in calcs) {
        if (!(id in resultados)) {
          const c = calcs[id];
          resultados[id] = c.fn(...c.inputs.map((i) => window.dash.data(i).data));
        }
        return estado(resultados[id]);
      }
      return { status: 'missing', data: [], message: `Sin datos: ${id}` };
    },
    calc(id, def) { calcs[id] = def; },
    loader() {},
    onData(fn) { fn(); },
    draw(name, fn) { dibujos.push([name, fn]); },
    params() { return {}; }, setParams() {}, resetParams() {}, setLink() {}, refresh() {},
  };
  const dibujar = () => {
    for (const [name, fn] of dibujos) {
      document.querySelectorAll(`[data-draw="${name}"]`).forEach((el) => {
        try { (typeof fn === 'function' ? fn : fn.update || (() => {}))(el); } catch (e) { console.error(name, e); }
      });
    }
  };
  window.addEventListener('DOMContentLoaded', dibujar);
  let t; window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(dibujar, 150); });
})();
