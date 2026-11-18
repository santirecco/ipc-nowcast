  const { f1: g1, f2: g2, fInt: gInt, nombreMes: nm, mesCorto: mc, fecha: fe } = window.ipx;
  const mix = (pct) => `color-mix(in srgb, ${dash.colors[0]} ${pct}%, var(--color-panel))`;

  // tira de referencias: rango, pronóstico, REM, último INDEC, solo modelo
  dash.draw('strip', (el) => {
    el.replaceChildren();
    const a = dash.data('actual'), u = dash.data('ultimo_indec');
    if (a.status !== 'ok' || !a.data || !a.data.length) { if (a.status === 'error') el.textContent = 'No se pudo cargar'; return; }
    const r = a.data[0], ind = u.status === 'ok' && u.data && u.data.length ? u.data[0] : null;
    const marks = [{ k: 'Solo modelo', v: r.solo_modelo }];
    if (r.rem !== null) marks.push({ k: 'REM', v: r.rem });
    if (ind) marks.push({ k: `INDEC ${mc(ind.mes)}`, v: ind.indec });
    if (r.ipc_caba !== null) marks.push({ k: 'IPC Ciudad', v: r.ipc_caba });
    const vals = [r.rango_bajo, r.rango_alto, ...marks.map((m) => m.v)];
    const W = el.clientWidth || 520, H = 150, pad = 18;
    const lo = Math.floor((d3.min(vals) - 0.25) * 2) / 2, hi = Math.ceil((d3.max(vals) + 0.25) * 2) / 2;
    const x = d3.scaleLinear().domain([lo, hi]).range([pad, W - pad]);
    const yAxis = 92;
    const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img')
      .attr('aria-label', `Pronóstico ${g1(r.estimacion)}% con rango ${g1(r.rango_bajo)}% a ${g1(r.rango_alto)}%, comparado con ${marks.map((m) => `${m.k} ${g1(m.v)}%`).join(', ')}`);
    svg.append('line').attr('x1', pad).attr('x2', W - pad).attr('y1', yAxis).attr('y2', yAxis).style('stroke', 'var(--color-border-line)').style('stroke-width', 6).style('stroke-linecap', 'round');
    svg.append('rect').attr('x', x(r.rango_bajo)).attr('width', x(r.rango_alto) - x(r.rango_bajo)).attr('y', yAxis - 9).attr('height', 18).attr('rx', 9)
      .style('fill', mix(28));
    const ticks = d3.range(lo, hi + 0.001, 0.5);
    svg.selectAll('text.tk').data(ticks).join('text').attr('class', 'tk').attr('x', (t) => x(t)).attr('y', H - 4).attr('text-anchor', 'middle')
      .text((t) => `${g1(t)}%`).style('fill', 'var(--cds-text-secondary)').style('font-size', '11px');
    // marcadores de referencia (abajo, en dos filas si se pisan)
    const sorted = marks.slice().sort((p, q) => p.v - q.v);
    let lastX = -1e9, row = 0;
    for (const m of sorted) {
      const mx = x(m.v);
      row = mx - lastX < 70 ? 1 - row : 0; lastX = mx;
      svg.append('line').attr('x1', mx).attr('x2', mx).attr('y1', yAxis - 12).attr('y2', yAxis + 12 + row * 14).style('stroke', 'var(--color-fg-muted)').style('stroke-width', 1.5);
      svg.append('text').attr('x', mx).attr('y', yAxis + 26 + row * 14).attr('text-anchor', 'middle')
        .text(`${m.k} ${g1(m.v)}`).style('fill', 'var(--color-fg-muted)').style('font-size', '11px');
    }
    // pronóstico (arriba)
    const ex = x(r.estimacion);
    svg.append('circle').attr('cx', ex).attr('cy', yAxis).attr('r', 9).style('fill', dash.colors[0]).style('stroke', 'var(--color-panel)').style('stroke-width', 3);
    svg.append('line').attr('x1', ex).attr('x2', ex).attr('y1', yAxis - 12).attr('y2', 30).style('stroke', dash.colors[0]).style('stroke-width', 1.5);
    const lab = svg.append('text').attr('x', ex).attr('y', 22).attr('text-anchor', 'middle').style('fill', 'var(--color-fg)').style('font-size', '13px').style('font-weight', 600)
      .text(`Pronóstico ${g2(r.estimacion)}%`);
    const bw = lab.node().getComputedTextLength();
    if (bw && ex - bw / 2 < 0) lab.attr('text-anchor', 'start').attr('x', 2);
    if (bw && ex + bw / 2 > W) lab.attr('text-anchor', 'end').attr('x', W - 2);
    svg.append('text').attr('x', x(r.rango_bajo)).attr('y', yAxis - 16).attr('text-anchor', 'middle').text(g1(r.rango_bajo))
      .style('fill', 'var(--cds-text-secondary)').style('font-size', '10px');
    svg.append('text').attr('x', x(r.rango_alto)).attr('y', yAxis - 16).attr('text-anchor', 'middle').text(g1(r.rango_alto))
      .style('fill', 'var(--cds-text-secondary)').style('font-size', '10px');
  });

  // barras de aporte por división
  dash.draw('div', (el) => {
    const d = dash.data('divisiones');
    el.replaceChildren();
    if (d.status !== 'ok') { if (d.status === 'error') el.textContent = 'No se pudo cargar'; return; }
    const filas = d.data.map((r) => ({ ...r, incidencia: +r.incidencia, variacion: +r.variacion })).sort((a, b) => b.incidencia - a.incidencia);
    const max = d3.max(filas, (r) => Math.abs(r.incidencia)) || 1;
    filas.forEach((r, i) => {
      const row = document.createElement('div'); row.className = 'ipx-bar-row';
      const name = document.createElement('div'); name.className = 'ipx-bar-name';
      name.textContent = r.nombre;
      const v = document.createElement('span'); v.className = 'ipx-bar-var'; v.textContent = `${g1(r.variacion)}%`; name.appendChild(v);
      const val = document.createElement('div'); val.className = 'ipx-bar-val'; val.textContent = g2(r.incidencia);
      const track = document.createElement('div'); track.className = 'ipx-bar-track';
      const bar = document.createElement('div'); bar.className = 'ipx-bar';
      bar.style.width = `${(Math.abs(r.incidencia) / max) * 100}%`;
      bar.style.background = r.incidencia < 0 ? 'var(--color-ok)' : i < 3 ? dash.colors[0] : mix(55);
      track.appendChild(bar);
      row.append(name, val, track); el.appendChild(row);
    });
  });

  // mapa de regiones (cuadrícula con la forma aproximada del país)
  const POS = { Noroeste: [1, 1], Noreste: [1, 3], Cuyo: [2, 1], Pampeana: [2, 2], GBA: [2, 3], Patagonia: [3, 1] };
  const escala = () => {
    const d = dash.data('regiones');
    if (d.status !== 'ok' || !d.data.length) return null;
    const vs = d.data.map((r) => +r.variacion);
    return { lo: d3.min(vs), hi: d3.max(vs), rows: d.data };
  };
  dash.draw('mapa', (el) => {
    el.replaceChildren();
    const e = escala();
    if (!e) { const d = dash.data('regiones'); if (d.status === 'error') el.textContent = 'No se pudo cargar'; return; }
    for (const r of e.rows) {
      const p = POS[r.region] || [4, 1];
      const t = document.createElement('div'); t.className = 'ipx-tile';
      t.style.gridRow = String(p[0]); t.style.gridColumn = r.region === 'Patagonia' ? '1 / span 2' : String(p[1]);
      const k = e.hi > e.lo ? (+r.variacion - e.lo) / (e.hi - e.lo) : 0.5;
      t.style.background = mix(Math.round(8 + k * 40));
      const n = document.createElement('span'); n.className = 'ipx-tile-name'; n.textContent = r.region;
      const v = document.createElement('span'); v.className = 'ipx-tile-val'; v.textContent = `${g2(+r.variacion)}%`;
      const w = document.createElement('span'); w.className = 'ipx-tile-w'; w.textContent = `${g1(+r.peso)}% del índice`;
      t.append(n, v, w); el.appendChild(t);
    }
    const nota = document.createElement('div'); nota.className = 'ipx-tile'; nota.style.gridRow = '3'; nota.style.gridColumn = '3';
    nota.style.background = 'transparent'; nota.style.borderStyle = 'dashed';
    const nt = document.createElement('span'); nt.className = 'ipx-tile-name'; nt.textContent = 'GBA y Pampeana suman cerca del 80% del índice nacional.';
    nota.appendChild(nt); el.appendChild(nota);
  });
  dash.draw('esc-min', (el) => { const e = escala(); el.textContent = e ? `${g2(e.lo)}%` : '—'; });
  dash.draw('esc-max', (el) => { const e = escala(); el.textContent = e ? `${g2(e.hi)}%` : '—'; });
  dash.draw('esc-grad', (el) => { el.style.background = `linear-gradient(90deg, ${mix(8)}, ${mix(48)})`; });

  // evolución diaria del pronóstico
  dash.draw('evol', (el) => {
    const d = dash.data('actual_mes'), a = dash.data('actual'), u = dash.data('ultimo_indec');
    el.replaceChildren();
    if (d.status !== 'ok' || !d.data || !d.data.length) { if (d.status === 'error') el.textContent = 'No se pudo cargar'; return; }
    const rows = d.data.map((r) => ({ ...r, t: d3.utcParse('%Y-%m-%d')(r.fecha_calculo) }));
    const rem = a.status === 'ok' && a.data && a.data.length ? a.data[0].rem : null;
    const ind = u.status === 'ok' && u.data && u.data.length ? u.data[0] : null;
    const [y0, m0] = rows[0].fecha_calculo.split('-').map(Number);
    const ini = Date.UTC(y0, m0 - 1, 1), fin = Date.UTC(y0, m0, 15);
    const W = el.clientWidth || 700, H = 240, m = { t: 16, r: 92, b: 26, l: 34 };
    const x = d3.scaleUtc().domain([new Date(ini), new Date(fin)]).range([m.l, W - m.r]);
    const vals = [...rows.flatMap((r) => [r.rango_bajo, r.rango_alto]), rem, ind && ind.indec].filter((v) => v !== null && v !== undefined);
    const y = d3.scaleLinear().domain([Math.max(0, d3.min(vals) - 0.3), d3.max(vals) + 0.3]).nice().range([H - m.b, m.t]);
    const svg = d3.select(el).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img')
      .attr('aria-label', 'Evolución diaria del pronóstico del mes, con su rango probable, el REM y el último dato de INDEC');
    svg.append('g').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(W - m.l - m.r)).tickFormat((v) => g1(v)))
      .call((g) => g.selectAll('.tick text').attr('x', -6));
    svg.append('g').attr('transform', `translate(0,${H - m.b})`).call(d3.axisBottom(x).ticks(W < 520 ? 4 : 7).tickSize(0).tickPadding(8).tickFormat(d3.utcFormat('%d/%m')));
    const ref = (v, label, dash_) => {
      if (v === null || v === undefined) return;
      svg.append('line').attr('x1', m.l).attr('x2', W - m.r).attr('y1', y(v)).attr('y2', y(v)).style('stroke', 'var(--color-fg-muted)').style('stroke-dasharray', dash_).style('opacity', 0.7);
      svg.append('text').attr('x', W - m.r + 6).attr('y', y(v) + 4).text(`${label} ${g1(v)}`).style('fill', 'var(--color-fg-muted)').style('font-size', '11px');
    };
    ref(rem, 'REM', '4 4');
    if (ind) ref(ind.indec, `INDEC ${mc(ind.mes)}`, '1 4');
    svg.append('path').datum(rows).attr('d', d3.area().x((r) => x(r.t)).y0((r) => y(r.rango_bajo)).y1((r) => y(r.rango_alto)))
      .style('fill', mix(25));
    if (rows.length === 1) {
      svg.append('rect').attr('x', x(rows[0].t) - 7).attr('width', 14).attr('y', y(rows[0].rango_alto)).attr('height', y(rows[0].rango_bajo) - y(rows[0].rango_alto)).attr('rx', 7)
        .style('fill', mix(25));
    }
    svg.append('path').datum(rows).attr('d', d3.line().x((r) => x(r.t)).y((r) => y(r.estimacion))).style('fill', 'none').style('stroke', dash.colors[0]).style('stroke-width', 2.5);
    svg.selectAll('circle.pt').data(rows).join('circle').attr('class', 'pt').attr('cx', (r) => x(r.t)).attr('cy', (r) => y(r.estimacion)).attr('r', 4.5)
      .style('fill', dash.colors[0]).style('stroke', 'var(--color-panel)').style('stroke-width', 2);
    const last = rows[rows.length - 1];
    svg.append('text').attr('x', x(last.t) + 10).attr('y', y(last.estimacion) - 10).text(`${g2(last.estimacion)}%`)
      .style('fill', 'var(--color-fg)').style('font-size', '12px').style('font-weight', 600);
    const tip = document.createElement('div'); tip.className = 'ipx-tip'; tip.hidden = true; el.appendChild(tip);
    svg.on('pointermove', (ev) => {
      const [px] = d3.pointer(ev); const r = rows[d3.minIndex(rows, (q) => Math.abs(x(q.t) - px))];
      tip.hidden = false; tip.replaceChildren();
      const b = document.createElement('b'); b.textContent = fe(r.fecha_calculo); tip.appendChild(b);
      tip.appendChild(document.createElement('br'));
      tip.appendChild(document.createTextNode(`Pronóstico ${g2(r.estimacion)}% · rango ${g1(r.rango_bajo)}–${g1(r.rango_alto)}%`));
      const sx = el.clientWidth / W;
      tip.style.left = `${Math.max(0, Math.min(x(r.t) * sx + 12, el.clientWidth - 230))}px`; tip.style.top = `${Math.max(0, y(r.estimacion) * sx - 60)}px`;
    }).on('pointerleave', () => { tip.hidden = true; });
  });

  // backtest: series que se pueden prender y apagar tocando la leyenda
  const BT_SERIES = [
    { k: 'indec', nombre: 'INDEC', det: 'Dato oficial', col: (r) => r.indec, color: 'var(--color-fg)', ancho: 2.2, puntos: true },
    { k: 'vispera', nombre: 'Víspera', det: 'Modelo + IPC Ciudad, con todos los precios del mes', col: (r) => r.vispera, color: () => dash.colors[0], ancho: 2.2 },
    { k: 'fin', nombre: 'Fin de mes', det: 'Modelo con los precios del mes completo, sin IPC Ciudad', col: (r) => r.fin_de_mes, color: () => dash.colors[3] || dash.colors[1], ancho: 1.6, guion: '1 0' },
    { k: 'mitad', nombre: 'Mitad de mes', det: 'Modelo con los precios hasta el día 15', col: (r) => r.mitad_de_mes, color: () => dash.colors[1], ancho: 1.6 },
    { k: 'inicio', nombre: 'Inicio de mes', det: 'Solo la proyección estadística', col: (r) => r.inicio_de_mes, color: () => dash.colors[2], ancho: 1.6, guion: '5 4' },
    { k: 'caba', nombre: 'IPC Ciudad', det: 'IPC de la Ciudad de Buenos Aires, sin modelo', col: (r) => r.ipc_caba, color: 'var(--color-fg-muted)', ancho: 1.4, guion: '2 3' },
  ];
  const btVisibles = new Set(['indec', 'vispera', 'mitad', 'inicio']);
  const colorDe = (s) => (typeof s.color === 'function' ? s.color() : s.color);
  const num = (v) => (v === null || v === undefined || v === '' || Number.isNaN(+v) ? null : +v);

  dash.draw('bt', (el) => {
    const d = dash.data('backtest');
    el.replaceChildren();
    if (d.status !== 'ok' || !d.data.length) { if (d.status === 'error') el.textContent = 'No se pudo cargar'; return; }
    const rows = d.data.map((r) => {
      const o = { mes: r.mes, t: d3.utcParse('%Y-%m')(r.mes) };
      for (const s of BT_SERIES) o[s.k] = num(s.col(r));
      return o;
    }).sort((a, b) => a.t - b.t).slice(-16);
    const series = BT_SERIES.filter((s) => rows.some((r) => r[s.k] !== null));

    const leyenda = document.createElement('div'); leyenda.className = 'ipx-legend ipx-legend-toggles';
    leyenda.setAttribute('role', 'group'); leyenda.setAttribute('aria-label', 'Series del gráfico: tocá para mostrar u ocultar');
    const lienzo = document.createElement('div'); lienzo.className = 'ipx-bt-canvas';
    el.append(leyenda, lienzo);

    const dibujar = () => {
      lienzo.replaceChildren();
      const vis = series.filter((s) => btVisibles.has(s.k));
      const W = el.clientWidth || 700, H = 270, m = { t: 12, r: 14, b: 74, l: 34 }, eh = 40;
      const x = d3.scalePoint().domain(rows.map((r) => r.mes)).range([m.l + 8, W - m.r - 8]);
      const vals = rows.flatMap((r) => (vis.length ? vis : series).map((s) => r[s.k])).filter((v) => v !== null);
      const y = d3.scaleLinear().domain([Math.max(0, d3.min(vals) - 0.3), d3.max(vals) + 0.2]).nice().range([H - m.b, m.t]);
      const svg = d3.select(lienzo).append('svg').attr('width', '100%').attr('viewBox', `0 0 ${W} ${H}`).attr('role', 'img')
        .attr('aria-label', `Inflación mensual de INDEC comparada con el pronóstico del modelo, últimos 16 meses. Series visibles: ${vis.map((s) => s.nombre).join(', ') || 'ninguna'}`);
      svg.append('g').attr('transform', `translate(${m.l},0)`).call(d3.axisLeft(y).ticks(5).tickSize(-(W - m.l - m.r)).tickFormat((v) => g1(v)))
        .call((g) => g.selectAll('.tick text').attr('x', -6));
      // primero las líneas finas, al final INDEC para que quede arriba
      for (const s of vis.slice().reverse()) {
        const ln = d3.line().defined((r) => r[s.k] !== null).x((r) => x(r.mes)).y((r) => y(r[s.k]));
        svg.append('path').datum(rows).attr('d', ln).style('fill', 'none').style('stroke', colorDe(s))
          .style('stroke-width', s.ancho).style('stroke-dasharray', s.guion || null);
        if (s.puntos) svg.selectAll(`circle.p-${s.k}`).data(rows.filter((r) => r[s.k] !== null)).join('circle').attr('class', `p-${s.k}`)
          .attr('cx', (r) => x(r.mes)).attr('cy', (r) => y(r[s.k])).attr('r', 3.2).style('fill', colorDe(s));
      }
      // franja de error: del modelo visible más informado
      const ref = ['vispera', 'fin', 'mitad', 'inicio', 'caba'].map((k) => series.find((s) => s.k === k)).find((s) => s && btVisibles.has(s.k));
      const ey = H - m.b + 22;
      if (ref) {
        const err = (r) => (r[ref.k] === null || r.indec === null ? null : Math.abs(r[ref.k] - r.indec));
        const emax = d3.max(rows, err) || 1;
        const eb = d3.scaleLinear().domain([0, emax]).range([0, eh - 6]);
        svg.append('text').attr('x', m.l).attr('y', ey - 6).text(`Error por mes: ${ref.nombre.toLowerCase()} (pp)`)
          .style('fill', 'var(--cds-text-secondary)').style('font-size', '11px');
        const bwid = Math.max(4, Math.min(18, (W - m.l - m.r) / rows.length - 8));
        svg.selectAll('rect.err').data(rows.filter((r) => err(r) !== null)).join('rect').attr('class', 'err').attr('x', (r) => x(r.mes) - bwid / 2).attr('width', bwid)
          .attr('y', (r) => ey + eh - eb(err(r))).attr('height', (r) => Math.max(1, eb(err(r)))).attr('rx', 2)
          .style('fill', (r) => (err(r) > 0.3 ? 'var(--color-warn)' : mix(55)));
      }
      const step = W < 560 ? 3 : 2;
      svg.selectAll('text.mx').data(rows.filter((_, i) => i % step === (rows.length - 1) % step)).join('text').attr('class', 'mx')
        .attr('x', (r) => x(r.mes)).attr('y', H - 2).attr('text-anchor', 'middle').text((r) => mc(r.mes)).style('fill', 'var(--cds-text-secondary)').style('font-size', '11px');
      if (!vis.length) {
        svg.append('text').attr('x', W / 2).attr('y', (H - m.b) / 2).attr('text-anchor', 'middle').text('Elegí al menos una serie en la leyenda')
          .style('fill', 'var(--cds-text-secondary)').style('font-size', '13px');
      }
      const guia = svg.append('line').attr('y1', m.t).attr('y2', H - 14).style('stroke', 'var(--cds-chart-reference)').style('display', 'none');
      const tip = document.createElement('div'); tip.className = 'ipx-tip'; tip.hidden = true; lienzo.appendChild(tip);
      svg.on('pointermove', (ev) => {
        if (!vis.length) return;
        const [px] = d3.pointer(ev); const r = rows[d3.minIndex(rows, (q) => Math.abs(x(q.mes) - px))];
        guia.attr('x1', x(r.mes)).attr('x2', x(r.mes)).style('display', null);
        tip.hidden = false; tip.replaceChildren();
        const b = document.createElement('b'); b.textContent = nm(r.mes); tip.appendChild(b);
        for (const s of vis) {
          if (r[s.k] === null) continue;
          const nombre = s.nombre;
          const txt = s.k === 'indec' ? `${nombre} ${g1(r.indec)}%` : `${nombre} ${g2(r[s.k])}%` + (r.indec !== null ? ` (error ${g2(Math.abs(r[s.k] - r.indec))})` : '');
          tip.appendChild(document.createElement('br')); tip.appendChild(document.createTextNode(txt));
        }
        const sx = lienzo.clientWidth / W;
        tip.style.left = `${Math.max(0, Math.min(x(r.mes) * sx + 12, lienzo.clientWidth - 280))}px`; tip.style.top = '6px';
      }).on('pointerleave', () => { tip.hidden = true; guia.style('display', 'none'); });
    };

    for (const s of series) {
      const btn = document.createElement('button'); btn.type = 'button'; btn.className = 'ipx-toggle';
      const sw = document.createElement('span'); sw.className = 'ipx-sw';
      if (s.guion && s.guion !== '1 0') { sw.classList.add('ipx-sw-dash'); sw.style.borderColor = colorDe(s); } else sw.style.background = colorDe(s);
      btn.append(sw, document.createTextNode(s.nombre)); btn.title = s.det;
      const pintar = () => { const on = btVisibles.has(s.k); btn.setAttribute('aria-pressed', String(on)); btn.classList.toggle('off', !on); };
      pintar();
      btn.addEventListener('click', () => { if (btVisibles.has(s.k)) btVisibles.delete(s.k); else btVisibles.add(s.k); pintar(); dibujar(); });
      leyenda.appendChild(btn);
    }
    dibujar();
  });

  // cadenas
  dash.draw('cadenas', (el) => {
    const d = dash.data('rec_ultimo');
    el.replaceChildren();
    if (d.status !== 'ok') { if (d.status === 'error') el.textContent = 'No se pudo cargar'; return; }
    const max = d3.max(d.data, (r) => r.productos) || 1;
    let grupo = null;
    for (const r of d.data) {
      if (r.fuente !== grupo) {
        grupo = r.fuente;
        const h = document.createElement('p'); h.className = 'ipx-eyebrow ipx-chain-group';
        h.textContent = `${grupo} · ${fe(r.fecha)}`;
        el.appendChild(h);
      }
      const row = document.createElement('div'); row.className = 'ipx-chain';
      const n = document.createElement('span'); n.textContent = r.cadena.charAt(0).toUpperCase() + r.cadena.slice(1);
      const tr = document.createElement('div'); tr.className = 'ipx-bar-track';
      const b = document.createElement('div'); b.className = 'ipx-bar'; b.style.width = `${(r.productos / max) * 100}%`; b.style.background = mix(60);
      tr.appendChild(b);
      const v = document.createElement('span'); v.className = 'ipx-num'; v.style.textAlign = 'right'; v.textContent = gInt(r.productos);
      row.append(n, tr, v); el.appendChild(row);
    }
  });
