  const { f1, f2, fInt, sg, nombreMes, fecha } = window.ipx;
  const fila = () => { const a = dash.data('actual'); return a.status === 'ok' && a.data && a.data.length ? a.data[0] : null; };
  const ui = () => { const u = dash.data('ultimo_indec'); return u.status === 'ok' && u.data && u.data.length ? u.data[0] : null; };
  const cmp = () => { const c = dash.data('comparacion'); return c.status === 'ok' && c.data && c.data.length ? c.data[0] : null; };
  const texto = (name, fn) => dash.draw(name, (el) => { const r = fila(); el.textContent = r ? fn(r) : '—'; });
  texto('mes-nombre', (r) => nombreMes(r.mes));
  texto('est', (r) => f1(r.estimacion));
  texto('bajo', (r) => `${f1(r.rango_bajo)}%`);
  texto('alto', (r) => `${f1(r.rango_alto)}%`);
  texto('fecha-calc', (r) => fecha(r.fecha_calculo));
  texto('dias-super', (r) => (r.dias_supermercados === null ? '—' : fInt(r.dias_supermercados)));
  texto('card-modelo', (r) => `${f2(r.solo_modelo)}%`);
  texto('card-caba', (r) => (r.ipc_caba === null ? 'Sin publicar' : `${f2(r.ipc_caba)}%`));
  texto('card-caba-nota', (r) => (r.ipc_caba === null ? 'Sale unos días antes que INDEC; ese día se incorpora al pronóstico.'
    : r.ajuste_caba ? `Incorporado (70%), corregido ${sg(r.ajuste_caba)} pp: en este mes la Ciudad suele desviarse del país.` : 'Ya incorporado al pronóstico (70%).'));
  texto('card-rem', (r) => (r.rem === null ? 'Sin dato' : `${f1(r.rem)}%`));
  dash.draw('frase-indec', (el) => {
    const r = fila(), u = ui();
    if (!r || !u) { el.textContent = '—'; return; }
    const d = r.estimacion - u.indec;
    el.textContent = Math.abs(d) < 0.05 ? `Similar al último dato de INDEC (${f1(u.indec)}% en ${nombreMes(u.mes)}).`
      : d < 0 ? `Por debajo del último dato de INDEC (${f1(u.indec)}% en ${nombreMes(u.mes)}).`
      : `Por encima del último dato de INDEC (${f1(u.indec)}% en ${nombreMes(u.mes)}).`;
  });
  dash.draw('indec-mes', (el) => { const u = ui(); el.textContent = u ? nombreMes(u.mes) : '—'; });
  dash.draw('indec-val', (el) => { const u = ui(); el.textContent = u ? `${f1(u.indec)}%` : '—'; });
  const delta = (name, key) => dash.draw(name, (el) => {
    const c = cmp(); const v = c ? c[key] : null;
    el.textContent = v === null || v === undefined ? '—' : sg(v);
    el.style.color = v === null || v === undefined || Math.abs(v) < 0.05 ? 'var(--color-fg-muted)' : v > 0 ? 'var(--color-bad)' : 'var(--color-ok)';
  });
  delta('delta-rem', 'vs_rem');
  delta('delta-indec', 'vs_indec');
  const err = (name, m) => dash.draw(name, (el) => { const e = dash.data('error_bt'); const r = e.status === 'ok' ? (e.data || []).find((x) => x.momento === m) : null; el.textContent = r ? f2(r.error) : '—'; });
  err('mae-ini', 'inicio'); err('mae-mit', 'mitad'); err('mae-vis', 'vispera'); err('mae-caba', 'caba');
  dash.draw('rec-total', (el) => { const t = dash.data('rec_total'); el.textContent = t.status === 'ok' && t.data ? fInt(t.data) : '—'; });
  dash.draw('rec-fecha', (el) => { const d = dash.data('rec_ultimo'); el.textContent = d.status === 'ok' && d.data.length ? fecha(d3.max(d.data, (r) => r.fecha)) : '—'; });
  dash.draw('sw-indec', (el) => { el.style.background = 'var(--color-fg)'; });
  dash.draw('sw-vis', (el) => { el.style.background = dash.colors[0]; });
  dash.draw('sw-ini', (el) => { el.style.borderColor = dash.colors[2]; });
  dash.draw('sw-mit', (el) => { el.style.background = dash.colors[1]; });

  // tabla de información del mes
  dash.draw('tab-info', (tb) => {
    const d = dash.data('informacion');
    tb.replaceChildren();
    if (d.status !== 'ok') return;
    const rows = d.data.slice().sort((a, b) => Math.abs(+b.efecto_pp) - Math.abs(+a.efecto_pp));
    for (const r of rows) {
      const tr = document.createElement('tr');
      tr.dataset.key = encodeURIComponent(r.clave);
      const td = (txt, cls) => { const c = document.createElement('td'); if (cls) c.className = cls; c.textContent = txt; tr.appendChild(c); return c; };
      td(r.region); td(r.nombre_componente); td(r.detalle, 'det');
      td(f2(+r.dato), 'num'); td(f2(+r.proyeccion), 'num');
      const c = td('', 'num'); const chip = document.createElement('span');
      const v = +r.efecto_pp; chip.className = `ipx-chip ${Math.abs(v) < 0.005 ? 'flat' : v > 0 ? 'up' : 'down'}`; chip.textContent = sg(v);
      c.appendChild(chip);
      tb.appendChild(tr);
    }
  });
