  const { f1, f2, fInt, sg, nombreMes, fecha } = window.ipx;
  const fila = () => { const a = dash.data('actual'); return a.status === 'ok' && a.data && a.data.length ? a.data[0] : null; };
  const ui = () => { const u = dash.data('ultimo_indec'); return u.status === 'ok' && u.data && u.data.length ? u.data[0] : null; };
  const cmp = () => { const c = dash.data('comparacion'); return c.status === 'ok' && c.data && c.data.length ? c.data[0] : null; };
  const texto = (name, fn) => dash.draw(name, (el) => { const r = fila(); el.textContent = r ? fn(r) : '—'; });
  // color de acento del tablero (en el tablero online viene del diseño elegido)
  { const raiz = document.querySelector('.ipx'); const c0 = String(dash.colors[0] || ''); if (raiz && c0 && !c0.includes('--c0')) raiz.style.setProperty('--c0', c0); }
  const MOMENTOS = {
    inicio_de_mes: 'Inicio de mes: todavía solo con la historia',
    mitad_de_mes: 'Mitad de mes: ya usa precios reales del mes',
    fin_de_mes: 'Fin de mes: con los precios del mes completo',
    vispera_con_caba: 'Víspera: ya salió el IPC de la Ciudad',
  };
  texto('mes-nombre', (r) => nombreMes(r.mes));
  texto('est', (r) => f1(r.estimacion));
  texto('bajo', (r) => `${f1(r.rango_bajo)}%`);
  texto('alto', (r) => `${f1(r.rango_alto)}%`);
  texto('fecha-calc', (r) => fecha(r.fecha_calculo));
  texto('momento', (r) => MOMENTOS[r.momento] || (r.ipc_caba !== null ? MOMENTOS.vispera_con_caba : 'Pronóstico del mes en curso'));
  texto('card-modelo', (r) => `${f2(r.solo_modelo)}%`);
  texto('card-caba', (r) => (r.ipc_caba === null ? 'Todavía no salió' : `${f2(r.ipc_caba)}%`));
  texto('card-caba-nota', (r) => (r.ipc_caba === null ? 'Se publica unos días antes que INDEC y ese día se suma al pronóstico: es el dato que más lo afina.'
    : r.ajuste_caba ? `Ya está en el pronóstico, corregido ${sg(r.ajuste_caba)} pp porque este mes la Ciudad suele desviarse del país.` : 'Ya está en el pronóstico, combinado con el modelo propio en la proporción que mejor anduvo en la historia (hoy, mitad y mitad).'));
  texto('card-rem', (r) => (r.rem === null ? 'Sin dato' : `${f1(r.rem)}%`));
  dash.draw('frase-indec', (el) => {
    const r = fila(), u = ui();
    if (!r || !u) { el.textContent = ''; return; }
    const d = r.estimacion - u.indec;
    el.textContent = Math.abs(d) < 0.05 ? `Parecido a ${nombreMes(u.mes)} (${f1(u.indec)}%).`
      : d < 0 ? `Sería menos que en ${nombreMes(u.mes)} (${f1(u.indec)}%).`
      : `Sería más que en ${nombreMes(u.mes)} (${f1(u.indec)}%).`;
  });
  dash.draw('indec-mes', (el) => { const u = ui(); el.textContent = u ? nombreMes(u.mes) : '—'; });
  dash.draw('indec-val', (el) => { const u = ui(); el.textContent = u ? `${f1(u.indec)}%` : '—'; });
  const delta = (name, key) => dash.draw(name, (el) => {
    const c = cmp(); const v = c ? c[key] : null;
    el.textContent = v === null || v === undefined ? '—' : Math.abs(v) < 0.05 ? 'prácticamente igual' : `${f2(Math.abs(v))} pp ${v > 0 ? 'por encima' : 'por debajo'}`;
    el.style.color = v === null || v === undefined || Math.abs(v) < 0.05 ? 'var(--color-fg-muted)' : v > 0 ? 'var(--color-bad)' : 'var(--color-ok)';
  });
  delta('delta-rem', 'vs_rem');
  delta('delta-indec', 'vs_indec');
  const err = (name, m) => dash.draw(name, (el) => { const e = dash.data('error_bt'); const r = e.status === 'ok' ? (e.data || []).find((x) => x.momento === m) : null; el.textContent = r && r.error !== null ? `${f2(r.error)} pp` : '—'; });
  err('mae-ini', 'inicio'); err('mae-mit', 'mitad'); err('mae-fin', 'fin'); err('mae-vis', 'vispera'); err('mae-caba', 'caba');
  dash.draw('rec-total', (el) => { const t = dash.data('rec_total'); el.textContent = t.status === 'ok' && t.data ? fInt(t.data) : '—'; });

  // ---------------------------------------------------------------- datos del mes
  const FUENTE = (f) => ({ 'calendario de regulados': 'Aumento anunciado', 'arrastre del mes anterior': 'Arrastre del mes anterior',
    'supermercados online': 'Supermercados online' }[f] || f.charAt(0).toUpperCase() + f.slice(1));
  const el_ = (tag, cls, txt) => { const e = document.createElement(tag); if (cls) e.className = cls; if (txt !== undefined) e.textContent = txt; return e; };
  const chipEfecto = (v) => el_('span', `ipx-chip ${Math.abs(v) < 0.005 ? 'flat' : v > 0 ? 'up' : 'down'}`, Math.abs(v) < 0.005 ? '0,00' : sg(v, f2));

  dash.draw('info-resumen', (el) => {
    el.replaceChildren();
    const t = dash.data('info_total'), r = fila();
    if (t.status !== 'ok' || !t.data || !t.data.length || !r) return;
    const tot = t.data[0];
    if (!tot.rubros) { el.appendChild(el_('p', 'ipx-muted', 'Todavía no hay datos del mes: el pronóstico es solo el modelo estadístico.')); return; }
    const a = el_('div', 'ipx-sum-item');
    a.append(el_('span', 'ipx-label', 'Sin datos del mes'), el_('span', 'ipx-sum-val', `${f2(r.solo_modelo)}%`));
    const flecha = el_('div', 'ipx-sum-arrow');
    flecha.append(el_('span', 'ipx-sum-arrow-line'), chipEfecto(tot.efecto), el_('span', 'ipx-hint', `${tot.rubros} rubros con datos reales`));
    const b = el_('div', 'ipx-sum-item');
    b.append(el_('span', 'ipx-label', r.ipc_caba === null ? 'Con los datos del mes' : 'Con los datos del mes (antes de sumar la Ciudad)'),
      el_('span', 'ipx-sum-val', `${f2(r.solo_modelo + tot.efecto)}%`));
    el.append(a, flecha, b);
  });

  dash.draw('info-rubros', (el) => {
    const d = dash.data('info_rubros');
    el.replaceChildren();
    if (d.status !== 'ok') { if (d.status === 'error') el.textContent = 'No se pudo cargar'; return; }
    const max = d3.max(d.data, (r) => Math.abs(r.efecto)) || 0.01;
    const cab = el_('div', 'ipx-info-row ipx-info-cab');
    cab.append(el_('span', null, 'Rubro y fuente'), el_('span', 'num', 'Sin datos'), el_('span', 'num', 'Con el dato real'), el_('span', 'num', 'Efecto en el total'));
    let grupo = null;
    for (const r of d.data) {
      if (r.grupo !== grupo) {
        grupo = r.grupo;
        el.appendChild(el_('p', 'ipx-info-grupo', grupo));
        el.appendChild(cab.cloneNode(true));
      }
      const det = el_('details', 'ipx-info-item');
      const sum = el_('summary', 'ipx-info-row');
      const nom = el_('span', 'ipx-info-nom');
      nom.append(el_('b', null, r.nombre), el_('small', null, `${[...new Set(r.fuentes.split(' · ').map(FUENTE))].join(' · ')} · ${r.regiones === 6 ? 'todo el país' : `${r.regiones} ${r.regiones === 1 ? 'región' : 'regiones'}`}`));
      const sin = el_('span', 'num ipx-info-sin', `${f2(r.sin)}%`);
      const con = el_('span', 'num ipx-info-con');
      const flecha = r.con - r.sin > 0.005 ? '▲' : r.con - r.sin < -0.005 ? '▼' : '';
      con.append(el_('span', `ipx-arrow ${flecha === '▲' ? 'up' : 'down'}`, flecha), document.createTextNode(` ${f2(r.con)}%`));
      const ef = el_('span', 'ipx-info-ef');
      const track = el_('span', 'ipx-div-track'); const bar = el_('span', `ipx-div-bar ${r.efecto >= 0 ? 'up' : 'down'}`);
      const w = Math.max(2, (Math.abs(r.efecto) / max) * 50);
      bar.style.width = `${w}%`; bar.style.left = r.efecto >= 0 ? '50%' : `${50 - w}%`;
      track.appendChild(bar);
      ef.append(track, chipEfecto(r.efecto));
      sum.append(nom, sin, con, ef);
      det.appendChild(sum);
      const tabla = el_('div', 'ipx-info-det');
      for (const x of r.detalle) {
        const fr = el_('div', 'ipx-info-det-row');
        const izq = el_('span', 'ipx-info-det-txt');
        izq.append(el_('b', null, x.region), el_('small', null, `${FUENTE(x.fuente)}: ${x.detalle}`));
        fr.append(izq, el_('span', 'num', `${f2(x.sin)}%`), el_('span', 'num', `${f2(x.con)}%`), el_('span', 'num ipx-info-det-ef', Math.abs(x.efecto) < 0.005 ? '0,00' : sg(x.efecto, f2)));
        tabla.appendChild(fr);
      }
      det.appendChild(tabla);
      el.appendChild(det);
    }
  });

  // estado de las fuentes
  dash.draw('fuentes-tabla', (el) => {
    const d = dash.data('fuentes');
    el.replaceChildren();
    if (d.status !== 'ok') { if (d.status === 'error') el.textContent = 'No se pudo cargar'; return; }
    for (const r of d.data) {
      const fila = el_('div', 'ipx-fuente');
      const izq = el_('span', 'ipx-fuente-nom'); izq.append(el_('b', null, r.fuente), el_('small', null, r.que_aporta));
      const ym = r.ultimo_dato ? r.ultimo_dato.slice(0, 7) : null;
      const cuando = !r.ultimo_dato ? '' : r.fuente === 'Calendario de tarifas' ? `cargado hasta ${nombreMes(ym)}`
        : String(r.frecuencia).startsWith('mensual') ? `dato de ${nombreMes(ym)}` : `último: ${fecha(r.ultimo_dato)}`;
      const fe_ = el_('span', 'ipx-fuente-fecha', cuando ? `${cuando} · ${r.frecuencia}` : r.frecuencia);
      const est = el_('span', `ipx-chip ${r.estado === 'al día' ? 'down' : 'up'}`, r.estado);
      fila.append(izq, fe_, est); el.appendChild(fila);
    }
  });
