  const fmtN = d3.formatLocale({ decimal: ',', thousands: '.', grouping: [3], currency: ['$', ''] });
  const f1 = fmtN.format('.1f'), f2 = fmtN.format('.2f'), fInt = fmtN.format(',d');
  const sg = (v, f = f2) => (v > 0.0049 ? '+' : v < -0.0049 ? '−' : '±') + f(Math.abs(v));
  const MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
  const nombreMes = (ym) => { const [y, m] = String(ym).split('-'); return `${MESES[+m - 1]} ${y}`; };
  const mesCorto = (ym) => { const [y, m] = String(ym).split('-'); return `${MESES[+m - 1].slice(0, 3)} ${y.slice(2)}`; };
  const fecha = (s) => { const [y, m, d] = String(s).split('-'); return `${d}/${m}/${y}`; };
  const nn = (v) => (v === null || v === undefined || v === '' ? null : +v);
  window.ipx = { f1, f2, fInt, sg, nombreMes, mesCorto, fecha, nn, MESES };

  dash.calc('actual', {
    inputs: ['pronostico'], title: 'Pronóstico más reciente',
    description: 'Fila del último cálculo para el mes más reciente pronosticado.',
    fn: (pronostico) => {
      if (!pronostico.length) return [];
      const ult = d3.max(pronostico, (r) => r.mes);
      const filas = pronostico.filter((r) => r.mes === ult).sort((a, b) => d3.ascending(a.fecha_calculo, b.fecha_calculo));
      const r = filas[filas.length - 1];
      const n = (v) => (v === null || v === undefined || v === '' ? null : +v);
      return [{ mes: r.mes, fecha_calculo: r.fecha_calculo, estimacion: +r.estimacion, rango_bajo: +r.rango_bajo, rango_alto: +r.rango_alto,
        solo_modelo: +r.solo_modelo, ipc_caba: n(r.ipc_caba), ajuste_caba: n(r.ajuste_caba), rem: n(r.rem), dias_supermercados: n(r.dias_supermercados), momento: r.momento || null }];
    },
  });
  dash.calc('actual_mes', {
    inputs: ['pronostico'], title: 'Pronósticos diarios del mes en curso',
    description: 'Todos los cálculos diarios para el mes más reciente.',
    fn: (pronostico) => {
      if (!pronostico.length) return [];
      const ult = d3.max(pronostico, (r) => r.mes);
      return pronostico.filter((r) => r.mes === ult).map((r) => ({ fecha_calculo: r.fecha_calculo, estimacion: +r.estimacion, rango_bajo: +r.rango_bajo, rango_alto: +r.rango_alto }))
        .sort((a, b) => d3.ascending(a.fecha_calculo, b.fecha_calculo));
    },
  });
  dash.calc('ultimo_indec', {
    inputs: ['backtest'], title: 'Último dato oficial de INDEC',
    fn: (backtest) => {
      if (!backtest.length) return [];
      const r = backtest.slice().sort((a, b) => d3.ascending(a.mes, b.mes)).pop();
      return [{ mes: r.mes, indec: +r.indec }];
    },
  });
  dash.calc('comparacion', {
    inputs: ['actual', 'ultimo_indec'], title: 'Pronóstico comparado con REM y con el último dato de INDEC',
    description: 'Diferencias en puntos porcentuales.',
    fn: (actual, ultimo_indec) => {
      if (!actual || !actual.length) return [];
      const a = actual[0], u = (ultimo_indec || [])[0];
      return [{ vs_rem: a.rem === null ? null : a.estimacion - a.rem, vs_indec: u ? a.estimacion - u.indec : null }];
    },
  });
  dash.calc('error_bt', {
    inputs: ['backtest'], title: 'Error promedio del backtest (últimos 16 meses)',
    description: 'Promedio del error absoluto contra INDEC, en puntos porcentuales.',
    fn: (backtest) => {
      const b = backtest.slice().sort((a, c) => d3.ascending(a.mes, c.mes)).slice(-16);
      const mae = (col) => d3.mean(b.filter((r) => r[col] !== null && r[col] !== ''), (r) => Math.abs(+r[col] - +r.indec));
      return [{ momento: 'inicio', error: mae('inicio_de_mes') }, { momento: 'mitad', error: b.length && 'mitad_de_mes' in b[0] ? mae('mitad_de_mes') : null }, { momento: 'vispera', error: mae('vispera') }, { momento: 'caba', error: mae('ipc_caba') }];
    },
  });
  dash.calc('rec_ultimo', {
    inputs: ['recoleccion'], title: 'Último relevamiento por fuente y cadena',
    description: 'Para cada fuente, su último día con datos.',
    fn: (recoleccion) => {
      if (!recoleccion.length) return [];
      const fuente = (r) => r.fuente || 'Supermercados online';
      const ult = d3.rollup(recoleccion, (v) => d3.max(v, (r) => r.fecha), fuente);
      return recoleccion.filter((r) => r.fecha === ult.get(fuente(r)))
        .map((r) => ({ fuente: fuente(r), cadena: r.cadena, fecha: r.fecha, productos: +r.productos }))
        .sort((a, b) => d3.ascending(a.fuente, b.fuente) || b.productos - a.productos);
    },
  });
  dash.calc('info_rubros', {
    inputs: ['informacion'], title: 'Datos del mes por rubro',
    description: 'Promedio nacional (ponderado por peso) de lo esperado sin datos y con el dato real, y efecto sobre el pronóstico total.',
    fn: (informacion) => {
      if (!informacion.length) return [];
      const rows = informacion.map((r) => ({ ...r, dato: +r.dato, proyeccion: +r.proyeccion, con: nn(r.con) === null ? +r.dato : +r.con,
        efecto_nacional: nn(r.efecto_nacional) || 0, peso: nn(r.peso) || 0 }));
      return d3.groups(rows, (r) => r.componente).map(([componente, g]) => {
        const pw = d3.sum(g, (r) => r.peso) || g.length;
        const prom = (k) => d3.sum(g, (r) => r[k] * (r.peso || 1)) / (d3.sum(g, (r) => r.peso) || g.length);
        return { componente, nombre: g[0].nombre_componente, grupo: g[0].grupo || '', fuentes: [...new Set(g.map((r) => r.fuente))].join(' · '),
          regiones: new Set(g.map((r) => r.region)).size, sin: prom('proyeccion'), con: prom('con'), efecto: d3.sum(g, (r) => r.efecto_nacional),
          peso: pw, detalle: g.map((r) => ({ region: r.region, detalle: r.detalle, fuente: r.fuente, sin: r.proyeccion, con: r.con, efecto: r.efecto_nacional }))
            .sort((a, b) => Math.abs(b.efecto) - Math.abs(a.efecto)) };
      }).sort((a, b) => d3.ascending(a.grupo, b.grupo) || Math.abs(b.efecto) - Math.abs(a.efecto));
    },
  });
  dash.calc('info_total', {
    inputs: ['info_rubros'], title: 'Efecto total de los datos del mes',
    fn: (info_rubros) => [{ efecto: d3.sum(info_rubros || [], (r) => r.efecto), rubros: (info_rubros || []).length }],
  });
  dash.calc('rec_total', {
    inputs: ['rec_ultimo'], title: 'Productos relevados en el último día',
    fn: (rec_ultimo) => d3.sum(rec_ultimo || [], (r) => r.productos),
  });
