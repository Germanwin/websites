# -*- coding: utf-8 -*-
"""Сборка лендинга «Периметр»: генерация векторной графики + вёрстка."""
import math

# ---------------------------------------------------------------- утилиты
def lerp(a, b, t): return a + (b - a) * t


def picket_run(p0, vp, f=340.0, gap=27.0, n=70, h0=250.0, w0=24.0, stop=0.988):
    """Ряд штакетин в перспективе: точка основания, высота, ширина, глубина."""
    out = []
    for i in range(n):
        d = i * gap
        t = d / (d + f)
        if t > stop:
            break
        s = 1.0 - t
        out.append({
            "x": lerp(p0[0], vp[0], t),
            "y": lerp(p0[1], vp[1], t),
            "h": h0 * s,
            "w": max(1.4, w0 * s),
            "t": t,
        })
    return out


# ---------------------------------------------------------------- герой
def hero_art():
    W, H = 1240, 430
    vp = (1235, 196)
    p0 = (-70, 452)
    pk = picket_run(p0, vp, f=240, gap=11.5, n=190, h0=146, w0=15.5)

    s = []
    a = s.append
    a('<svg class="hero-art" viewBox="0 0 %d %d" preserveAspectRatio="xMidYMax slice" '
      'role="img" aria-label="Забор из евроштакетника вдоль участка на рассвете">' % (W, H))

    a('<defs>')
    a('<radialGradient id="sun" cx="0.5" cy="0.5" r="0.5">'
      '<stop offset="0" style="stop-color:var(--sun);stop-opacity:.7"/>'
      '<stop offset="1" style="stop-color:var(--sun);stop-opacity:0"/></radialGradient>')
    a('<linearGradient id="field" x1="0" y1="0" x2="0" y2="1">'
      '<stop offset="0" style="stop-color:var(--field-1)"/>'
      '<stop offset="1" style="stop-color:var(--field-2)"/></linearGradient>')
    a('<linearGradient id="pick" x1="0" y1="0" x2="1" y2="0">'
      '<stop offset="0" style="stop-color:var(--pick-1)"/>'
      '<stop offset=".55" style="stop-color:var(--pick-2)"/>'
      '<stop offset="1" style="stop-color:var(--pick-3)"/></linearGradient>')
    a('<linearGradient id="haze" x1="0" y1="0" x2="0" y2="1">'
      '<stop offset="0" style="stop-color:var(--sky-3);stop-opacity:.75"/>'
      '<stop offset="1" style="stop-color:var(--sky-3);stop-opacity:0"/></linearGradient>')
    a('</defs>')

    # солнце
    a('<circle cx="880" cy="96" r="190" fill="url(#sun)"/>')
    a('<circle cx="880" cy="96" r="34" style="fill:var(--sun)" opacity=".45"/>')

    # дальний лес
    band = []
    for i in range(0, 132):
        x = -20 + i * 10
        hgt = 17 + 11 * math.sin(i * 0.7) + 8 * math.sin(i * 0.23) + 5 * math.sin(i * 1.9)
        band.append((x, 206 - hgt))
    a('<path d="M-20 250 %s L1280 250 Z" style="fill:var(--forest-far)" opacity=".5"/>'
      % " ".join("L%.1f %.1f" % p for p in band))

    band2 = []
    for i in range(0, 96):
        x = -20 + i * 14
        hgt = 13 + 9 * math.sin(i * 0.55 + 1.2) + 6 * math.sin(i * 1.3)
        band2.append((x, 216 - hgt))
    a('<path d="M-20 264 %s L1280 264 Z" style="fill:var(--forest-near)" opacity=".7"/>'
      % " ".join("L%.1f %.1f" % p for p in band2))

    # дом
    a('<g opacity=".9">')
    a('<path d="M452 218 L512 180 L572 218 Z" style="fill:var(--roof)"/>')
    a('<rect x="464" y="216" width="96" height="46" style="fill:var(--house)"/>')
    a('<rect x="482" y="230" width="17" height="17" style="fill:var(--win)"/>')
    a('<rect x="518" y="230" width="17" height="17" style="fill:var(--win)"/>')
    a('<rect x="543" y="188" width="9" height="20" style="fill:var(--roof)"/>')
    a('</g>')

    # поле
    a('<path d="M-20 246 C 300 234, 700 244, 1280 230 L1280 430 L-20 430 Z" fill="url(#field)"/>')
    a('<path d="M-20 246 C 300 234, 700 244, 1280 230" fill="none" style="stroke:var(--field-line-c)" stroke-width="1.2" opacity=".45"/>')
    a('<rect x="-20" y="176" width="1280" height="94" fill="url(#haze)"/>')

    # тень забора
    sh = [(p["x"] - p["h"] * 0.5, p["y"] + p["h"] * 0.09) for p in pk]
    if sh:
        a('<path d="M%.1f %.1f %s L%.1f %.1f Z" style="fill:var(--shadow-c)" opacity=".18"/>'
          % (pk[0]["x"], pk[0]["y"], " ".join("L%.1f %.1f" % q for q in sh), pk[-1]["x"], pk[-1]["y"]))

    # лаги
    for hf in (0.30, 0.78):
        top = " ".join("L%.1f %.1f" % (p["x"], p["y"] - p["h"] * hf) for p in pk)
        bot = " ".join("L%.1f %.1f" % (p["x"], p["y"] - p["h"] * hf + max(1.2, 6 * (1 - p["t"])))
                       for p in reversed(pk))
        a('<path d="M%.1f %.1f %s %s Z" style="fill:var(--pick-3)" opacity=".85"/>'
          % (pk[0]["x"], pk[0]["y"] - pk[0]["h"] * hf, top, bot))

    # столбы
    for i, p in enumerate(pk):
        if i % 12:
            continue
        w, h = p["w"] * 1.45, p["h"] * 1.1
        a('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%.1f" style="fill:var(--post)"/>'
          % (p["x"] - w / 2, p["y"] - h, w, h, min(2.5, w * 0.16)))

    # штакетины
    for p in pk:
        x, y = p["x"] - p["w"] / 2, p["y"] - p["h"]
        a('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" fill="url(#pick)"/>'
          % (x, y, p["w"], p["h"], min(3, p["w"] * 0.22)))
        if p["w"] > 5:
            a('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" style="fill:var(--pick-hi)" opacity=".45"/>'
              % (x + p["w"] * 0.14, y + p["h"] * 0.05, max(0.8, p["w"] * 0.12), p["h"] * 0.9))

    # трава
    a('<path d="M-20 408 C 200 396, 430 416, 700 404 C 940 394, 1120 412, 1280 400 L1280 430 L-20 430 Z" '
      'style="fill:var(--grass)"/>')
    for i in range(70):
        x = -10 + i * 18 + 6 * math.sin(i * 2.3)
        hgt = 7 + 5 * math.sin(i * 1.7)
        a('<path d="M%.1f 424 q %.1f -%.1f %.1f -%.1f" fill="none" style="stroke:var(--grass-2)" '
          'stroke-width="1.8" stroke-linecap="round" opacity=".75"/>'
          % (x, 2 * math.sin(i), hgt * 0.6, 3.5 * math.sin(i * 1.1), hgt))
    a('</svg>')
    return "".join(s)


# ---------------------------------------------------------------- профили материалов
def _frame(inner, label, extra=""):
    return ('<svg class="mat-art" viewBox="0 0 300 168" role="img" aria-label="%s">'
            '<defs>%s</defs>'
            '<rect width="300" height="168" style="fill:var(--art-bg)"/>'
            '%s'
            '<ellipse cx="150" cy="152" rx="132" ry="7" style="fill:var(--shadow-c)" opacity=".16"/>'
            '</svg>') % (label, extra, inner)


def mat_prof():
    g = ('<linearGradient id="pf" x1="0" y1="0" x2="1" y2="0">'
         '<stop offset="0" style="stop-color:var(--pick-2)"/>'
         '<stop offset=".5" style="stop-color:var(--pick-1)"/>'
         '<stop offset="1" style="stop-color:var(--pick-3)"/></linearGradient>')
    p = ['<rect x="26" y="24" width="248" height="126" rx="2" style="fill:var(--pick-2)"/>']
    x = 28
    while x < 272:
        p.append('<rect x="%d" y="24" width="9" height="126" fill="url(#pf)"/>' % x)
        p.append('<rect x="%d" y="24" width="2" height="126" style="fill:var(--pick-hi)" opacity=".5"/>' % (x + 2))
        x += 15
    p.append('<rect x="26" y="20" width="248" height="6" rx="3" style="fill:var(--post)"/>')
    p.append('<rect x="18" y="14" width="14" height="140" rx="3" style="fill:var(--post)"/>')
    p.append('<rect x="268" y="14" width="14" height="140" rx="3" style="fill:var(--post)"/>')
    return _frame("".join(p), "Забор из профнастила", g)


def mat_shtak():
    g = ('<linearGradient id="sh" x1="0" y1="0" x2="1" y2="0">'
         '<stop offset="0" style="stop-color:var(--pick-1)"/>'
         '<stop offset=".6" style="stop-color:var(--pick-2)"/>'
         '<stop offset="1" style="stop-color:var(--pick-3)"/></linearGradient>')
    p = ['<rect x="30" y="52" width="240" height="9" style="fill:var(--pick-3)"/>',
         '<rect x="30" y="112" width="240" height="9" style="fill:var(--pick-3)"/>']
    x = 24
    while x < 274:
        p.append('<rect x="%d" y="18" width="15" height="132" rx="5" fill="url(#sh)"/>' % x)
        p.append('<rect x="%d" y="22" width="3" height="124" style="fill:var(--pick-hi)" opacity=".45"/>' % (x + 3))
        x += 24
    p.append('<rect x="16" y="10" width="14" height="144" rx="3" style="fill:var(--post)"/>')
    p.append('<rect x="270" y="10" width="14" height="144" rx="3" style="fill:var(--post)"/>')
    return _frame("".join(p), "Забор из евроштакетника", g)


def mat_3d():
    p = []
    x = 34
    while x <= 266:
        p.append('<rect x="%d" y="26" width="3" height="124" rx="1.5" style="fill:var(--wire)"/>' % x)
        x += 15
    for y in (34, 58, 82, 106, 130):
        p.append('<rect x="30" y="%d" width="240" height="3" rx="1.5" style="fill:var(--wire)"/>' % y)
    for y in (66, 114):
        p.append('<path d="M30 %d q 120 -13 240 0" fill="none" style="stroke:var(--wire-hi)" stroke-width="5" stroke-linecap="round"/>' % y)
    p.append('<rect x="18" y="14" width="13" height="140" rx="3" style="fill:var(--post)"/>')
    p.append('<rect x="269" y="14" width="13" height="140" rx="3" style="fill:var(--post)"/>')
    return _frame("".join(p), "Забор из 3D-сетки")


def mat_rab():
    p = ['<clipPath id="cr"><rect x="30" y="22" width="240" height="128"/></clipPath>',
         '<g clip-path="url(#cr)">']
    for i in range(-14, 26):
        p.append('<path d="M%d 10 L%d 170" style="stroke:var(--wire)" stroke-width="2.2" opacity=".9"/>'
                 % (30 + i * 18, 30 + i * 18 + 160))
        p.append('<path d="M%d 10 L%d 170" style="stroke:var(--wire)" stroke-width="2.2" opacity=".9"/>'
                 % (30 + i * 18 + 160, 30 + i * 18))
    p.append('</g>')
    p.append('<rect x="30" y="20" width="240" height="4" rx="2" style="fill:var(--wire-hi)"/>')
    p.append('<rect x="18" y="12" width="13" height="142" rx="3" style="fill:var(--post)"/>')
    p.append('<rect x="269" y="12" width="13" height="142" rx="3" style="fill:var(--post)"/>')
    return _frame("".join(p), "Забор из сетки-рабицы")


def mat_jal():
    g = ('<linearGradient id="jl" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0" style="stop-color:var(--pick-1)"/>'
         '<stop offset="1" style="stop-color:var(--pick-3)"/></linearGradient>')
    p = []
    y = 22
    while y < 146:
        p.append('<path d="M28 %d L272 %d L272 %d L28 %d Z" fill="url(#jl)"/>'
                 % (y + 9, y, y + 11, y + 20))
        p.append('<path d="M28 %d L272 %d" fill="none" style="stroke:var(--pick-hi)" stroke-width="1.6" opacity=".5"/>'
                 % (y + 9.5, y + 0.5))
        y += 16
    p.append('<rect x="16" y="12" width="14" height="142" rx="3" style="fill:var(--post)"/>')
    p.append('<rect x="270" y="12" width="14" height="142" rx="3" style="fill:var(--post)"/>')
    return _frame("".join(p), "Забор-жалюзи", g)


# ---------------------------------------------------------------- сцены кейсов
def scene_slope():
    p = ['<svg class="case-art" viewBox="0 0 420 220" role="img" aria-label="Забор на склоне, секции лесенкой">',
         '<rect width="420" height="220" style="fill:var(--art-bg)"/>',
         '<path d="M0 150 C 120 120, 260 178, 420 132 L420 220 L0 220 Z" style="fill:var(--field-2)"/>']
    for i in range(9):
        x = 22 + i * 44
        base = 150 - i * 9
        p.append('<rect x="%d" y="%d" width="38" height="%d" rx="3" style="fill:var(--pick-2)"/>' % (x, base - 76, 76))
        for k in range(4):
            p.append('<rect x="%d" y="%d" width="6" height="%d" rx="2" style="fill:var(--pick-1)"/>'
                     % (x + 3 + k * 9, base - 76, 76))
        p.append('<rect x="%d" y="%d" width="9" height="%d" rx="2" style="fill:var(--post)"/>' % (x + 36, base - 86, 90))
    p.append('<path d="M12 176 L408 128" fill="none" style="stroke:var(--accent)" stroke-width="2" stroke-dasharray="6 6" opacity=".8"/>')
    p.append('<text x="16" y="200" style="fill:var(--ink-2)" font-family="ui-monospace,Menlo,monospace" font-size="12">ПЕРЕПАД 2,4 м</text>')
    p.append('</svg>')
    return "".join(p)


def scene_winter():
    p = ['<svg class="case-art" viewBox="0 0 420 220" role="img" aria-label="Монтаж забора зимой">',
         '<rect width="420" height="220" style="fill:var(--art-bg)"/>',
         '<circle cx="330" cy="58" r="34" style="fill:var(--sun)" opacity=".4"/>']
    p.append('<path d="M0 168 C 130 152, 280 182, 420 160 L420 220 L0 220 Z" style="fill:var(--snow)"/>')
    for i in range(10):
        x = 16 + i * 40
        p.append('<rect x="%d" y="76" width="30" height="94" rx="2" style="fill:var(--pick-2)"/>' % x)
        p.append('<rect x="%d" y="76" width="8" height="94" style="fill:var(--pick-1)"/>' % (x + 4))
        p.append('<rect x="%d" y="70" width="30" height="7" rx="3" style="fill:var(--snow)"/>' % x)
        p.append('<rect x="%d" y="66" width="10" height="106" rx="3" style="fill:var(--post)"/>' % (x + 30))
    for i in range(26):
        p.append('<circle cx="%.0f" cy="%.0f" r="%.1f" style="fill:var(--snow)" opacity=".85"/>'
                 % (14 + (i * 61) % 400, 16 + (i * 37) % 150, 1.6 + (i % 3)))
    p.append('<text x="16" y="204" style="fill:var(--ink-2)" font-family="ui-monospace,Menlo,monospace" font-size="12">−18 °C · ЯМОБУР</text>')
    p.append('</svg>')
    return "".join(p)


def scene_long():
    vp, p0 = (410, 118), (-30, 210)
    pk = picket_run(p0, vp, f=150, gap=13, n=60, h0=104, w0=13)
    p = ['<svg class="case-art" viewBox="0 0 420 220" role="img" aria-label="Периметр посёлка, 640 метров">',
         '<rect width="420" height="220" style="fill:var(--art-bg)"/>',
         '<path d="M0 128 C 140 118, 280 132, 420 116 L420 220 L0 220 Z" style="fill:var(--field-2)"/>']
    for hf in (0.34, 0.8):
        top = " ".join("L%.1f %.1f" % (q["x"], q["y"] - q["h"] * hf) for q in pk)
        bot = " ".join("L%.1f %.1f" % (q["x"], q["y"] - q["h"] * hf + max(1, 4 * (1 - q["t"]))) for q in reversed(pk))
        p.append('<path d="M%.1f %.1f %s %s Z" style="fill:var(--pick-3)"/>'
                 % (pk[0]["x"], pk[0]["y"] - pk[0]["h"] * hf, top, bot))
    for i, q in enumerate(pk):
        p.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="1.5" style="fill:var(--pick-%d)"/>'
                 % (q["x"] - q["w"] / 2, q["y"] - q["h"], q["w"], q["h"], 1 if i % 2 else 2))
    p.append('<text x="16" y="204" style="fill:var(--ink-2)" font-family="ui-monospace,Menlo,monospace" font-size="12">640 м · 3 БРИГАДЫ</text>')
    p.append('</svg>')
    return "".join(p)


# ---------------------------------------------------------------- план участка
def plan_art():
    return '''<svg viewBox="0 0 520 400" role="img" aria-label="Схема участка: периметр 42 на 27 метров, дом, откатные ворота">
<defs><pattern id="gp" width="26" height="26" patternUnits="userSpaceOnUse"><path d="M26 0H0V26" fill="none" style="stroke:var(--line)" stroke-width="1"/></pattern></defs>
<rect width="520" height="400" fill="url(#gp)" opacity=".9"/>
<rect x="70" y="70" width="380" height="250" rx="4" style="fill:var(--brand-soft)" opacity=".7"/>
<rect x="196" y="150" width="140" height="96" rx="3" style="fill:var(--surface-2); stroke:var(--line-2)" stroke-width="1.5"/>
<text x="266" y="203" text-anchor="middle" style="fill:var(--ink-2)" font-family="ui-monospace,Menlo,monospace" font-size="12" letter-spacing="1.5">ДОМ</text>
<path d="M70 320 L70 70 L450 70 L450 320 L318 320 M240 320 L70 320" fill="none" style="stroke:var(--brand)" stroke-width="3.4" stroke-linejoin="round"/>
<path d="M70 320 L70 70 L450 70 L450 320 L318 320 M240 320 L70 320" fill="none" style="stroke:var(--brand)" stroke-width="9" stroke-linecap="round" stroke-dasharray="0 26"/>
<path d="M240 320 L318 320" fill="none" style="stroke:var(--accent)" stroke-width="3.4" stroke-dasharray="7 5"/>
<path d="M246 338 L318 338 M252 333 L246 338 L252 343" fill="none" style="stroke:var(--accent)" stroke-width="1.6" stroke-linecap="round"/>
<text x="352" y="343" style="fill:var(--accent)" font-family="ui-monospace,Menlo,monospace" font-size="11" letter-spacing="1">ВОРОТА 3,8 м</text>
<path d="M70 372 L450 372 M70 366 L70 378 M450 366 L450 378" fill="none" style="stroke:var(--ink-2)" stroke-width="1"/>
<rect x="226" y="361" width="68" height="22" rx="4" style="fill:var(--surface)"/>
<text x="260" y="376" text-anchor="middle" style="fill:var(--ink)" font-family="ui-monospace,Menlo,monospace" font-size="13" font-weight="600">42 м</text>
<path d="M484 70 L484 320 M478 70 L490 70 M478 320 L490 320" fill="none" style="stroke:var(--ink-2)" stroke-width="1"/>
<rect x="468" y="181" width="32" height="28" rx="4" style="fill:var(--surface)"/>
<text x="484" y="200" text-anchor="middle" style="fill:var(--ink)" font-family="ui-monospace,Menlo,monospace" font-size="13" font-weight="600">27</text>
<path d="M28 96 L28 300" fill="none" style="stroke:var(--line-2)" stroke-width="1" stroke-dasharray="4 4"/>
<text x="22" y="204" text-anchor="middle" transform="rotate(-90 22 204)" style="fill:var(--ink-2)" font-family="ui-monospace,Menlo,monospace" font-size="11" letter-spacing="1">УКЛОН 8°</text>
</svg>'''


# ================================================================ СТИЛИ
CSS = r"""
:root{
  /* поверхности и текст */
  --bg:#F7F8F5; --surface:#FFFFFF; --surface-2:#EFF2EC; --surface-3:#E6EBE2;
  --ink:#0E1714; --ink-2:#4F5D57; --ink-3:#77857E;
  --line:#E2E7DE; --line-2:#CCD5C9;
  /* фирменный и акцент */
  --brand:#0F5A3D; --brand-2:#2E9A6B; --brand-soft:#E4F0E9; --brand-ring:rgba(15,90,61,.16);
  --accent:#E0521F; --accent-2:#FF8A3D; --accent-ink:#FFFFFF; --accent-soft:#FCE9DF;
  /* поля ввода — всегда белые */
  --field:#FFFFFF; --field-ink:#0E1714; --field-line:#BFC9BE;
  /* подвал */
  --foot-bg:#0D1613; --foot-ink:#E7EDE8; --foot-ink-2:#8FA098; --foot-line:#22302A;
  /* иллюстрации */
  --sky-1:#C3DAE8; --sky-2:#DFE9E4; --sky-3:#F6E9D6; --sun:#FFCE86;
  --forest-far:#7FA893; --forest-near:#437C64;
  --roof:#33484F; --house:#EAE5DA; --win:#F7C978;
  --field-1:#C2D6AF; --field-2:#9CBE90; --field-line-c:#7FA57B;
  --grass:#84AC72; --grass-2:#6D9762;
  --pick-1:#3F8E69; --pick-2:#2E7355; --pick-3:#1D5440; --pick-hi:#8AC7A5; --post:#173F2E;
  --wire:#6E8078; --wire-hi:#54675E; --snow:#F3F8FA;
  --art-bg:#EDF2EA; --shadow-c:#0E2A20;
  /* геометрия */
  --r-xl:22px; --r-lg:16px; --r-md:11px; --r-sm:7px;
  --sh-1:0 1px 2px rgba(14,42,32,.05), 0 2px 6px rgba(14,42,32,.04);
  --sh-2:0 2px 4px rgba(14,42,32,.05), 0 12px 26px -14px rgba(14,42,32,.28);
  --sh-3:0 4px 8px rgba(14,42,32,.06), 0 28px 60px -28px rgba(14,42,32,.42);
  --maxw:1180px;
  --f-body:system-ui,-apple-system,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
  --f-mono:ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme:dark){ :root:not([data-theme="light"]){
  --bg:#0C110F; --surface:#131A17; --surface-2:#182120; --surface-3:#1F2A27;
  --ink:#E8EEE9; --ink-2:#9AA9A2; --ink-3:#7B8A83;
  --line:#242F2B; --line-2:#35433D;
  --brand:#54C494; --brand-2:#7BD9AF; --brand-soft:#14261F; --brand-ring:rgba(84,196,148,.2);
  --accent:#FF6E38; --accent-2:#FF9C5E; --accent-ink:#1B0A03; --accent-soft:#2B160D;
  --field-line:#3A4842;
  --foot-bg:#080D0B; --foot-ink:#E2E9E4; --foot-ink-2:#7E8F87; --foot-line:#1B2621;
  --sky-1:#16242C; --sky-2:#182420; --sky-3:#232821; --sun:#8A7148;
  --forest-far:#26473A; --forest-near:#1B342B;
  --roof:#1E2A2E; --house:#39423C; --win:#C9A25C;
  --field-1:#2A3D2C; --field-2:#1F2F23; --field-line-c:#38513C;
  --grass:#25382A; --grass-2:#2E4432;
  --pick-1:#2E6F53; --pick-2:#245743; --pick-3:#183E31; --pick-hi:#4E9B78; --post:#122B21;
  --wire:#566159; --wire-hi:#3E4B44; --snow:#2A3538;
  --art-bg:#131B18; --shadow-c:#000000;
  --sh-1:0 1px 2px rgba(0,0,0,.4); --sh-2:0 2px 4px rgba(0,0,0,.45), 0 14px 28px -16px rgba(0,0,0,.8);
  --sh-3:0 4px 10px rgba(0,0,0,.5), 0 30px 60px -30px rgba(0,0,0,.95);
}}
:root[data-theme="dark"]{
  --bg:#0C110F; --surface:#131A17; --surface-2:#182120; --surface-3:#1F2A27;
  --ink:#E8EEE9; --ink-2:#9AA9A2; --ink-3:#7B8A83;
  --line:#242F2B; --line-2:#35433D;
  --brand:#54C494; --brand-2:#7BD9AF; --brand-soft:#14261F; --brand-ring:rgba(84,196,148,.2);
  --accent:#FF6E38; --accent-2:#FF9C5E; --accent-ink:#1B0A03; --accent-soft:#2B160D;
  --field-line:#3A4842;
  --foot-bg:#080D0B; --foot-ink:#E2E9E4; --foot-ink-2:#7E8F87; --foot-line:#1B2621;
  --sky-1:#16242C; --sky-2:#182420; --sky-3:#232821; --sun:#8A7148;
  --forest-far:#26473A; --forest-near:#1B342B;
  --roof:#1E2A2E; --house:#39423C; --win:#C9A25C;
  --field-1:#2A3D2C; --field-2:#1F2F23; --field-line-c:#38513C;
  --grass:#25382A; --grass-2:#2E4432;
  --pick-1:#2E6F53; --pick-2:#245743; --pick-3:#183E31; --pick-hi:#4E9B78; --post:#122B21;
  --wire:#566159; --wire-hi:#3E4B44; --snow:#2A3538;
  --art-bg:#131B18; --shadow-c:#000000;
  --sh-1:0 1px 2px rgba(0,0,0,.4); --sh-2:0 2px 4px rgba(0,0,0,.45), 0 14px 28px -16px rgba(0,0,0,.8);
  --sh-3:0 4px 10px rgba(0,0,0,.5), 0 30px 60px -30px rgba(0,0,0,.95);
}

*{box-sizing:border-box}
body{
  margin:0; background:var(--bg); color:var(--ink);
  font-family:var(--f-body); font-size:17px; line-height:1.62;
  -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
  padding-bottom:76px;
}
@media(min-width:721px){ body{padding-bottom:0} }
svg{max-width:100%; display:block}
h1,h2,h3,h4{margin:0; text-wrap:balance; font-weight:800; line-height:1.08; letter-spacing:-.028em}
h1{font-size:clamp(2.05rem,1.05rem+3.7vw,3.65rem); letter-spacing:-.035em}
h2{font-size:clamp(1.62rem,1.1rem+2.1vw,2.6rem)}
h3{font-size:1.2rem; line-height:1.26; letter-spacing:-.02em}
p{margin:0}
a{color:inherit}
::selection{background:var(--brand-soft); color:var(--ink)}
:focus-visible{outline:2.5px solid var(--accent); outline-offset:3px; border-radius:4px}

.wrap{max-width:var(--maxw); margin:0 auto; padding:0 22px}
.sec{padding:clamp(56px,7vw,110px) 0}
.sec--tint{background:var(--surface-2)}
.sec--tight{padding-top:0}
.center{text-align:center}
.center .chip{justify-content:center}
.center .lead{margin-left:auto; margin-right:auto}

/* ——— заголовки секций ——— */
.chip{
  display:inline-flex; align-items:center; gap:9px; margin-bottom:20px;
  font-family:var(--f-mono); font-size:11.5px; letter-spacing:.13em; text-transform:uppercase;
  color:var(--brand); background:var(--brand-soft); border-radius:99px; padding:7px 14px 7px 11px;
}
.chip::before{content:""; width:6px; height:6px; border-radius:50%; background:var(--brand)}
.lead{color:var(--ink-2); font-size:clamp(1rem,.96rem+.35vw,1.16rem); max-width:64ch; margin-top:18px}
.mono{font-family:var(--f-mono); font-variant-numeric:tabular-nums}
.hl{background:linear-gradient(transparent 74%, color-mix(in srgb, var(--accent) 34%, transparent) 74%); padding:0 .05em}
em.b{font-style:normal; color:var(--brand)}

/* ——— кнопки ——— */
.btn{
  display:inline-flex; align-items:center; justify-content:center; gap:10px; position:relative;
  font:inherit; font-weight:700; letter-spacing:-.012em; cursor:pointer; text-decoration:none;
  padding:17px 30px; min-height:52px; border-radius:var(--r-md); border:1px solid transparent;
  transition:transform .18s cubic-bezier(.2,.7,.3,1), box-shadow .18s ease, background .18s ease, border-color .18s ease;
}
.btn--accent{
  color:var(--accent-ink); background:linear-gradient(170deg,var(--accent-2),var(--accent));
  box-shadow:0 1px 0 rgba(255,255,255,.25) inset, 0 10px 22px -10px var(--accent);
}
.btn--accent:hover{transform:translateY(-2px); box-shadow:0 1px 0 rgba(255,255,255,.3) inset, 0 16px 30px -12px var(--accent)}
.btn--accent:active{transform:translateY(0)}
.btn--ghost{background:var(--surface); color:var(--ink); border-color:var(--line-2)}
.btn--ghost:hover{border-color:var(--brand); color:var(--brand); background:var(--brand-soft)}
.btn--light{background:#fff; color:#0F5A3D}
.btn--light:hover{transform:translateY(-2px); box-shadow:var(--sh-2)}
.btn--lg{padding:20px 36px; min-height:60px; font-size:1.06rem}
.btn--block{width:100%}
.note{font-size:13.5px; color:var(--ink-2); margin-top:12px; line-height:1.45}

/* ——— шапка ——— */
.top{position:sticky; top:0; z-index:50; background:color-mix(in srgb, var(--surface) 82%, transparent); backdrop-filter:saturate(1.6) blur(14px); -webkit-backdrop-filter:saturate(1.6) blur(14px); border-bottom:1px solid transparent; transition:border-color .25s, box-shadow .25s}
.top.stuck{border-bottom-color:var(--line); box-shadow:var(--sh-1)}
.top-in{display:flex; align-items:center; gap:20px; padding:13px 22px; max-width:var(--maxw); margin:0 auto}
.brandmark{display:flex; align-items:center; gap:11px; margin-right:auto; min-width:0; text-decoration:none}
.brandmark .glyph{width:36px; height:36px; border-radius:9px; background:linear-gradient(150deg,var(--brand-2),var(--brand)); display:grid; place-items:center; flex:none; box-shadow:0 4px 10px -4px var(--brand-ring)}
.brandmark b{font-size:1.12rem; font-weight:800; letter-spacing:-.01em; text-transform:uppercase; display:block; line-height:1.1}
.brandmark i{font-style:normal; font-size:11.5px; color:var(--ink-2); line-height:1.2; display:block}
.top .tel{font-family:var(--f-mono); font-weight:600; text-decoration:none; white-space:nowrap; font-size:15px; letter-spacing:-.02em}
.top .tel:hover{color:var(--brand)}
.top .btn{padding:11px 18px; min-height:42px; font-size:14px}
@media(max-width:900px){ .brandmark i{display:none} }
@media(max-width:640px){ .top .btn{display:none} }

/* ——— первый экран ——— */
.hero{position:relative; overflow:hidden; background:linear-gradient(178deg,var(--sky-1) 0%,var(--sky-2) 52%,var(--sky-3) 100%)}
.hero-art{position:absolute; left:0; right:0; bottom:-1px; width:100%; height:clamp(200px,27vw,360px); z-index:1}
.hero-in{position:relative; z-index:2; display:grid; grid-template-columns:1.06fr .94fr; gap:56px;
  align-items:start; padding:clamp(34px,4vw,58px) 22px clamp(190px,22vw,290px); max-width:var(--maxw); margin:0 auto}
@media(max-width:980px){ .hero-in{grid-template-columns:1fr; gap:30px; padding-bottom:clamp(180px,44vw,260px)} }
.hero h1{color:var(--ink)}
.hero .lead{color:var(--ink-2)}
.bullets{list-style:none; margin:28px 0 0; padding:0; display:grid; gap:12px}
.bullets li{position:relative; padding-left:34px; font-size:15.5px; line-height:1.45; color:var(--ink)}
.bullets li::before{
  content:""; position:absolute; left:0; top:1px; width:22px; height:22px; border-radius:7px;
  background:var(--brand); opacity:.14;
}
.bullets li::after{
  content:""; position:absolute; left:6px; top:8px; width:10px; height:5.5px;
  border-left:2px solid var(--brand); border-bottom:2px solid var(--brand); transform:rotate(-45deg);
}
.hero-cta{margin-top:34px; display:flex; flex-wrap:wrap; gap:16px 20px; align-items:center}

/* карточка плана */
.plan{background:var(--surface); border:1px solid var(--line); border-radius:var(--r-xl); box-shadow:var(--sh-3); overflow:hidden}
.plan-head{display:flex; justify-content:space-between; align-items:center; gap:12px; padding:14px 18px; border-bottom:1px solid var(--line); font-family:var(--f-mono); font-size:11px; letter-spacing:.11em; text-transform:uppercase; color:var(--ink-2)}
.plan-head b{color:var(--brand); font-size:12px}
.plan figure{margin:0; padding:12px 14px 4px}
.plan figcaption{padding:6px 18px 18px; font-size:13px; color:var(--ink-2); line-height:1.45}

/* ——— доверие: счётчики ——— */
.stats{display:grid; grid-template-columns:repeat(4,1fr); gap:14px}
@media(max-width:720px){ .stats{grid-template-columns:repeat(2,1fr)} }
.stat{background:var(--surface); border:1px solid var(--line); border-radius:var(--r-lg); padding:22px 20px; box-shadow:var(--sh-1); position:relative; overflow:hidden}
.stat::before{content:""; position:absolute; left:20px; right:20px; top:0; height:3px; border-radius:0 0 3px 3px; background:linear-gradient(90deg,var(--brand-2),var(--brand))}
.stat b{display:block; font-family:var(--f-mono); font-size:clamp(1.5rem,1.1rem+1.5vw,2.15rem); font-weight:700; letter-spacing:-.04em; font-variant-numeric:tabular-nums; line-height:1}
.stat > span{display:block; font-size:13.5px; color:var(--ink-2); margin-top:8px; line-height:1.35}
.stat b span{display:inline; font-size:inherit; color:inherit; margin:0}

/* ——— сетки и карточки ——— */
.grid{display:grid; gap:22px}
.g-2{grid-template-columns:repeat(2,1fr)}
.g-3{grid-template-columns:repeat(3,1fr)}
.g-4{grid-template-columns:repeat(4,1fr)}
@media(max-width:920px){ .g-3,.g-4{grid-template-columns:repeat(2,1fr)} }
@media(max-width:640px){ .g-2,.g-3,.g-4{grid-template-columns:1fr} }
.card{background:var(--surface); border:1px solid var(--line); border-radius:var(--r-lg); padding:28px; box-shadow:var(--sh-1); transition:transform .22s cubic-bezier(.2,.7,.3,1), box-shadow .22s ease, border-color .22s ease}
.card:hover{transform:translateY(-3px); box-shadow:var(--sh-2); border-color:var(--line-2)}
.card h3{margin-bottom:10px}
.card p{color:var(--ink-2); font-size:15px}
.card .tag{display:inline-block; font-family:var(--f-mono); font-size:11px; letter-spacing:.12em; color:var(--brand); background:var(--brand-soft); border-radius:6px; padding:5px 9px; margin-bottom:16px}

/* ——— боли ——— */
.pains{display:grid; gap:12px; margin-top:38px; grid-template-columns:repeat(2,1fr)}
@media(max-width:820px){ .pains{grid-template-columns:1fr} }
.pain{display:grid; grid-template-columns:auto 1fr; gap:16px; align-items:start; background:var(--surface); border:1px solid var(--line); border-left:3px solid var(--accent); border-radius:var(--r-md); padding:20px 22px}
.pain svg{color:var(--accent); flex:none; margin-top:2px}
.pain q{font-size:15.6px; line-height:1.5; quotes:"«" "»"; color:var(--ink)}
.pain.pain--wide{grid-column:1/-1; border-left-color:var(--brand); background:var(--brand-soft)}
.pain.pain--wide svg{color:var(--brand)}

/* ——— выгоды ——— */
.ben{display:grid; grid-template-columns:auto 1fr; gap:18px; align-items:start}
.ben-ic{width:46px; height:46px; flex:none; border-radius:13px; display:grid; place-items:center; color:var(--brand);
  background:linear-gradient(160deg,var(--brand-soft),transparent), var(--surface); border:1px solid var(--line-2); box-shadow:var(--sh-1)}
.ben h3{font-size:1.06rem; margin-bottom:7px}
.ben p{color:var(--ink-2); font-size:14.8px; line-height:1.55}

/* ——— материалы ——— */
.mat{background:var(--surface); border:1px solid var(--line); border-radius:var(--r-lg); overflow:hidden; display:flex; flex-direction:column; box-shadow:var(--sh-1); transition:transform .22s cubic-bezier(.2,.7,.3,1), box-shadow .22s ease}
.mat:hover{transform:translateY(-4px); box-shadow:var(--sh-2)}
.mat-art{width:100%; height:auto; border-bottom:1px solid var(--line); transition:transform .35s cubic-bezier(.2,.7,.3,1)}
.mat:hover .mat-art{transform:scale(1.035)}
.mat-figure{overflow:hidden; margin:0}
.mat-b{padding:22px 24px 26px; display:flex; flex-direction:column; gap:10px; flex:1}
.mat-b h3{font-size:1.1rem}
.mat-b p{color:var(--ink-2); font-size:14.4px; flex:1; line-height:1.5}
.price{display:flex; align-items:baseline; gap:8px; margin-top:4px; padding-top:16px; border-top:1px dashed var(--line-2)}
.price b{font-family:var(--f-mono); font-weight:700; font-size:1.28rem; letter-spacing:-.035em; color:var(--ink); font-variant-numeric:tabular-nums}
.price span{font-size:12px; color:var(--ink-2); line-height:1.25}
.mat--cta{background:linear-gradient(165deg,var(--brand),#0B4630); border-color:transparent; color:#fff; justify-content:center; align-items:flex-start; padding:32px 28px; gap:14px}
@media (prefers-color-scheme:dark){ :root:not([data-theme="light"]) .mat--cta{background:linear-gradient(165deg,var(--brand-2),var(--brand)); color:#062018} }
:root[data-theme="dark"] .mat--cta{background:linear-gradient(165deg,var(--brand-2),var(--brand)); color:#062018}
.mat--cta h3{font-size:1.24rem}
.mat--cta p{font-size:14.6px; opacity:.86}

/* ——— этапы ——— */
.steps{margin-top:42px; position:relative; display:grid; gap:4px}
.step{display:grid; grid-template-columns:auto 1fr auto; gap:22px; align-items:start; padding:22px 0; position:relative}
.step + .step{border-top:1px solid var(--line)}
.step-n{width:44px; height:44px; border-radius:50%; display:grid; place-items:center; flex:none;
  font-family:var(--f-mono); font-size:14px; font-weight:600; color:var(--brand);
  background:var(--surface); border:1.5px solid var(--brand-ring); box-shadow:var(--sh-1)}
.step h3{font-size:1.1rem; margin-bottom:7px}
.step p{color:var(--ink-2); font-size:15px; max-width:62ch}
.when{font-family:var(--f-mono); font-size:12.5px; color:var(--brand); background:var(--brand-soft); padding:7px 12px; border-radius:99px; white-space:nowrap}
@media(max-width:680px){ .step{grid-template-columns:auto 1fr; gap:16px} .when{grid-column:2; margin-top:10px; justify-self:start} }

/* ——— кейсы ——— */
.case{background:var(--surface); border:1px solid var(--line); border-radius:var(--r-lg); overflow:hidden; box-shadow:var(--sh-1); transition:transform .22s cubic-bezier(.2,.7,.3,1), box-shadow .22s}
.case:hover{transform:translateY(-4px); box-shadow:var(--sh-2)}
.case-art{width:100%; height:auto; border-bottom:1px solid var(--line)}
.case-b{padding:24px}
.case-b .kicker{font-family:var(--f-mono); font-size:11px; letter-spacing:.11em; text-transform:uppercase; color:var(--ink-2)}
.case-b h3{font-size:1.08rem; margin:11px 0 9px}
.case-b p{font-size:14.6px; color:var(--ink-2); line-height:1.55}
.case-b .res{margin-top:16px; padding:13px 15px; border-radius:var(--r-sm); background:var(--brand-soft); font-size:14.4px; color:var(--ink)}
.case-b .res b{color:var(--brand)}

/* ——— отзывы ——— */
.rev{background:var(--surface); border:1px solid var(--line); border-radius:var(--r-lg); padding:28px; display:flex; flex-direction:column; gap:16px; box-shadow:var(--sh-1); position:relative}
.rev .stars{display:flex; gap:3px; color:var(--accent)}
.rev p{font-size:15.4px; line-height:1.6}
.rev mark{background:var(--accent-soft); color:var(--ink); padding:1px 4px; border-radius:4px}
.rev footer{margin-top:auto; display:flex; align-items:center; gap:13px; padding-top:18px; border-top:1px solid var(--line)}
.ava{width:42px; height:42px; border-radius:50%; flex:none; display:grid; place-items:center; font-weight:700; font-size:15px; color:var(--brand); background:var(--brand-soft); border:1px solid var(--line-2)}
.rev .who b{display:block; font-size:14.8px}
.rev .who span{display:block; font-size:12.8px; color:var(--ink-2)}

/* ——— гарантии ——— */
.guar{background:var(--surface); border:1px solid var(--line); border-radius:var(--r-lg); padding:26px; box-shadow:var(--sh-1); display:flex; flex-direction:column; gap:12px; transition:transform .22s, box-shadow .22s}
.guar:hover{transform:translateY(-3px); box-shadow:var(--sh-2)}
.guar b.num{font-family:var(--f-mono); font-size:1.9rem; font-weight:700; letter-spacing:-.045em; color:var(--brand); line-height:1}
.guar h3{font-size:1.02rem}
.guar p{font-size:14.4px; color:var(--ink-2); line-height:1.5}

/* ——— FAQ ——— */
.faq{margin-top:38px; background:var(--surface); border:1px solid var(--line); border-radius:var(--r-lg); overflow:hidden; box-shadow:var(--sh-1)}
.faq details + details{border-top:1px solid var(--line)}
.faq summary{cursor:pointer; list-style:none; padding:23px 62px 23px 26px; position:relative; font-weight:700; font-size:1.05rem; letter-spacing:-.018em; transition:background .18s}
.faq summary:hover{background:var(--surface-2)}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{
  content:""; position:absolute; right:24px; top:50%; width:26px; height:26px; margin-top:-13px;
  border-radius:50%; background:var(--brand-soft);
}
.faq summary::before{
  content:"+"; position:absolute; right:32px; top:50%; margin-top:-14px; z-index:1;
  font-family:var(--f-mono); font-size:16px; color:var(--brand); line-height:26px;
}
.faq details[open] summary::before{content:"–"; right:33px}
.faq .ans{padding:0 26px 26px; color:var(--ink-2); max-width:74ch; font-size:15.4px; line-height:1.62}

/* ——— формы ——— */
.field{display:block}
.field span{display:block; font-size:13.4px; color:var(--ink-2); margin-bottom:8px; line-height:1.4}
.field input{
  width:100%; font:inherit; font-family:var(--f-mono); font-size:1.04rem; letter-spacing:-.02em;
  padding:17px 18px; border:1.5px solid var(--field-line); border-radius:var(--r-md);
  background:var(--field); color:var(--field-ink); transition:border-color .18s, box-shadow .18s;
}
.field input:focus{outline:none; border-color:var(--brand); box-shadow:0 0 0 4px var(--brand-ring)}
.field input::placeholder{color:#98A39C}
.consent{display:flex; gap:11px; align-items:flex-start; font-size:12.6px; color:var(--ink-2); margin-top:15px; line-height:1.45; cursor:pointer}
.consent input{margin:2px 0 0; width:17px; height:17px; flex:none; accent-color:var(--brand)}
.err{color:var(--accent); font-size:13.5px; margin-top:11px; display:none; font-weight:600}
.err.on{display:block}

/* ——— цветные панели ——— */
.panel{position:relative; overflow:hidden; border-radius:var(--r-xl); padding:clamp(30px,4vw,52px); color:#fff;
  background:linear-gradient(150deg,#14724D 0%,#0C4732 62%,#0A3A2A 100%); box-shadow:var(--sh-2)}
.panel::after{content:""; position:absolute; inset:0; opacity:.16; pointer-events:none;
  background-image:repeating-linear-gradient(90deg,#fff 0 2px,transparent 2px 16px);
  -webkit-mask-image:linear-gradient(255deg,#000,transparent 62%); mask-image:linear-gradient(255deg,#000,transparent 62%)}
.panel > *{position:relative; z-index:1}
.panel h2{color:#fff}
.panel p{color:rgba(255,255,255,.84)}
.panel .field span{color:rgba(255,255,255,.8)}
.panel .consent{color:rgba(255,255,255,.76)}
.panel .err{color:#FFC9AE}
.panel-grid{display:grid; grid-template-columns:1.1fr .9fr; gap:38px; align-items:center}
@media(max-width:860px){ .panel-grid{grid-template-columns:1fr; gap:26px} }

/* ——— финальный блок ——— */
.final{background:var(--surface); border:1px solid var(--line); border-radius:var(--r-xl); box-shadow:var(--sh-3); padding:clamp(30px,3.8vw,52px); display:grid; grid-template-columns:1.04fr .96fr; gap:44px}
@media(max-width:860px){ .final{grid-template-columns:1fr; gap:28px} }
.gift{margin-top:24px; border-radius:var(--r-md); padding:18px 20px; background:var(--accent-soft); border:1px solid var(--accent); font-size:14.6px; line-height:1.5}
.gift b{display:block; font-size:11.5px; font-family:var(--f-mono); letter-spacing:.12em; text-transform:uppercase; color:var(--accent); margin-bottom:7px}

/* ——— квиз ——— */
.quiz{background:var(--surface); border:1px solid var(--line); border-radius:var(--r-xl); box-shadow:var(--sh-3); overflow:hidden; margin-top:38px}
.qhead{padding:22px 28px 0}
.qmeta{display:flex; justify-content:space-between; align-items:center; font-family:var(--f-mono); font-size:11.5px; letter-spacing:.11em; text-transform:uppercase; color:var(--ink-2)}
.qmeta b{color:var(--brand)}
.qbar{height:6px; background:var(--surface-2); border-radius:99px; margin-top:13px; overflow:hidden}
.qbar i{display:block; height:100%; width:14%; border-radius:99px; background:linear-gradient(90deg,var(--brand-2),var(--brand)); transition:width .45s cubic-bezier(.2,.7,.3,1)}
.qbody{padding:30px 28px 10px; min-height:352px}
@media(max-width:640px){ .qbody{padding:24px 20px 8px; min-height:0} .qhead{padding:18px 20px 0} }
.qstep{display:none}
.qstep.on{display:block; animation:qin .32s cubic-bezier(.2,.7,.3,1)}
@keyframes qin{from{opacity:0; transform:translateY(10px)} to{opacity:1; transform:none}}
.qstep h3{font-size:clamp(1.2rem,1rem+.8vw,1.6rem); margin-bottom:7px}
.qsub{color:var(--ink-2); font-size:14.6px; margin-bottom:22px; max-width:60ch}
.opts{display:grid; grid-template-columns:repeat(2,1fr); gap:11px}
@media(max-width:640px){ .opts{grid-template-columns:1fr} }
.opt{
  font:inherit; text-align:left; cursor:pointer; padding:16px 46px 16px 18px; font-size:15.4px; position:relative;
  background:var(--surface); color:var(--ink); border:1.5px solid var(--line-2); border-radius:var(--r-md);
  transition:border-color .18s, background .18s, transform .18s cubic-bezier(.2,.7,.3,1), box-shadow .18s;
}
.opt::after{
  content:""; position:absolute; right:16px; top:50%; margin-top:-10px; width:20px; height:20px; border-radius:50%;
  border:1.5px solid var(--line-2); transition:border-color .18s, background .18s;
}
.opt:hover{border-color:var(--brand); background:var(--brand-soft); transform:translateY(-2px); box-shadow:var(--sh-1)}
.opt.sel{border-color:var(--brand); background:var(--brand-soft); box-shadow:0 0 0 3px var(--brand-ring)}
.opt.sel::after{border-color:var(--brand); background:var(--brand);
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23fff' stroke-width='3.5' stroke-linecap='round'%3E%3Cpath d='M5 12.5l4.5 4.5L19 7'/%3E%3C/svg%3E");
  background-size:13px; background-repeat:no-repeat; background-position:center}
.opt.wide{grid-column:1/-1}
.opt.soft{color:var(--ink-2)}
.slide-val{font-family:var(--f-mono); font-size:clamp(2.2rem,1.5rem+2.6vw,3.2rem); font-weight:700; letter-spacing:-.05em; color:var(--brand); font-variant-numeric:tabular-nums; line-height:1}
.slide-val small{font-size:.95rem; color:var(--ink-2); font-weight:400; letter-spacing:0; margin-left:6px}
.rng{-webkit-appearance:none; appearance:none; width:100%; height:36px; background:transparent; margin:14px 0 2px; cursor:pointer}
.rng::-webkit-slider-runnable-track{height:8px; border-radius:99px; background:var(--surface-3)}
.rng::-moz-range-track{height:8px; border-radius:99px; background:var(--surface-3)}
.rng::-webkit-slider-thumb{-webkit-appearance:none; width:30px; height:30px; margin-top:-11px; border-radius:50%;
  background:linear-gradient(160deg,var(--brand-2),var(--brand)); border:3px solid var(--surface); box-shadow:var(--sh-2)}
.rng::-moz-range-thumb{width:24px; height:24px; border-radius:50%;
  background:linear-gradient(160deg,var(--brand-2),var(--brand)); border:3px solid var(--surface); box-shadow:var(--sh-2)}
.range-legend{display:flex; justify-content:space-between; font-family:var(--f-mono); font-size:12px; color:var(--ink-2)}
.checks{display:grid; gap:11px}
.check{display:flex; gap:13px; align-items:center; padding:15px 18px; border:1.5px solid var(--line-2); border-radius:var(--r-md); cursor:pointer; font-size:15.4px; transition:border-color .18s, background .18s}
.check:hover{border-color:var(--brand)}
.check input{width:19px; height:19px; accent-color:var(--brand); flex:none}
.check.on{border-color:var(--brand); background:var(--brand-soft)}
.qfoot{display:flex; align-items:center; gap:16px; padding:18px 28px; border-top:1px solid var(--line); background:var(--surface-2)}
@media(max-width:640px){ .qfoot{padding:15px 20px} }
.qback{font:inherit; font-size:14px; background:none; border:0; color:var(--ink-2); cursor:pointer; padding:8px 0; transition:color .18s}
.qback:hover{color:var(--brand)}
.qfoot .mono{margin-left:auto; font-size:11.5px; color:var(--ink-2); letter-spacing:.09em; text-transform:uppercase}
.qdone{display:none; padding:clamp(40px,5vw,68px) 28px; text-align:center}
.qdone.on{display:block; animation:qin .4s ease}
.qdone .tick{width:64px; height:64px; margin:0 auto 22px; border-radius:50%; color:#fff; display:grid; place-items:center;
  background:linear-gradient(160deg,var(--brand-2),var(--brand)); box-shadow:0 12px 26px -12px var(--brand-ring)}
.qdone p{color:var(--ink-2); max-width:54ch; margin:14px auto 0}

/* ——— модалка ——— */
dialog{border:1px solid var(--line); border-radius:var(--r-xl); padding:0; background:var(--surface); color:var(--ink); max-width:430px; width:calc(100% - 40px); box-shadow:var(--sh-3)}
dialog::backdrop{background:rgba(8,20,16,.6); backdrop-filter:blur(3px)}
.mbox{padding:30px; position:relative}
.mbox h3{font-size:1.4rem; margin-bottom:9px}
.mbox > p{color:var(--ink-2); font-size:14.6px; margin-bottom:22px}
.mclose{position:absolute; top:14px; right:16px; background:none; border:0; font-size:26px; line-height:1; color:var(--ink-2); cursor:pointer; border-radius:6px}
.mclose:hover{color:var(--ink)}

/* ——— подвал ——— */
.foot{background:var(--foot-bg); color:var(--foot-ink); padding:64px 0 40px; font-size:14.8px}
.foot .brandmark b{color:var(--foot-ink)}
.foot h4{font-family:var(--f-mono); font-size:11px; letter-spacing:.13em; text-transform:uppercase; color:var(--foot-ink-2); font-weight:400; margin-bottom:14px}
.foot p{color:var(--foot-ink-2); line-height:1.55}
.foot a{text-decoration:none; color:var(--foot-ink); border-bottom:1px solid var(--foot-line); transition:border-color .18s}
.foot a:hover{border-color:var(--foot-ink)}
.foot ul{list-style:none; margin:0; padding:0; display:grid; gap:10px; color:var(--foot-ink-2)}
.legal{margin-top:44px; padding-top:24px; border-top:1px solid var(--foot-line); color:var(--foot-ink-2); font-size:12.4px; display:flex; flex-wrap:wrap; gap:8px 26px}

/* ——— sticky на мобильных ——— */
.sticky{position:fixed; left:0; right:0; bottom:0; z-index:60; display:none; gap:10px; padding:11px 14px calc(11px + env(safe-area-inset-bottom));
  background:color-mix(in srgb, var(--surface) 92%, transparent); backdrop-filter:blur(12px); border-top:1px solid var(--line); box-shadow:0 -8px 24px -16px rgba(14,42,32,.5)}
.sticky .btn{flex:1; padding:14px 10px; min-height:50px; font-size:15px}
@media(max-width:720px){ .sticky{display:flex} }

/* ——— появление ——— */
.js .rv{opacity:0; transform:translateY(18px); transition:opacity .6s cubic-bezier(.2,.7,.3,1), transform .6s cubic-bezier(.2,.7,.3,1)}
.js .rv.in{opacity:1; transform:none}
.rv-2{transition-delay:.08s} .rv-3{transition-delay:.16s} .rv-4{transition-delay:.24s}
@media (prefers-reduced-motion:reduce){
  .rv{opacity:1; transform:none; transition:none}
  .qstep.on,.qdone.on{animation:none}
  .btn,.card,.mat,.case,.guar,.opt{transition:none}
  .mat:hover .mat-art{transform:none}
  html{scroll-behavior:auto}
}
"""


# ================================================================ РАЗМЕТКА
BODY = r"""
<header class="top" id="top">
  <div class="top-in">
    <a class="brandmark" href="#top">
      <span class="glyph" aria-hidden="true">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round">
          <path d="M5 21V6l2.5-3L10 6v15M14 21V6l2.5-3L19 6v15M3 10h18M3 15h18"/>
        </svg>
      </span>
      <span>
        <b>Периметр</b>
        <i>заборы под ключ в Москве и области с 2014 года</i>
      </span>
    </a>
    <a class="tel" href="tel:+74951208419">+7 495 120-84-19</a>
    <button class="btn btn--ghost" type="button" data-callback>Перезвоните мне</button>
  </div>
</header>

<!-- ================= 01. ПЕРВЫЙ ЭКРАН ================= -->
<section class="hero">
  @@HERO@@
  <div class="hero-in">
    <div>
      <h1>Поставим забор под ключ <em class="b" style="white-space:nowrap">за 3 дня</em> и сэкономим <span class="hl">до 47 000 ₽</span> — за счёт собственного цеха профлиста в Дмитрове</h1>
      <p class="lead">Пройдите тест за 1 минуту — узнаете стоимость по вашим параметрам и получите смету в трёх вариантах: эконом, оптимум, премиум.</p>
      <ul class="bullets">
        <li>Цена фиксируется в договоре — за грунт, уклон и погоду вы не доплачиваете</li>
        <li>7 лет гарантии на монтаж и 12 лет на покрытие от сквозной коррозии</li>
        <li>Прораб присылает фото и видео с объекта каждый день в 18:00</li>
        <li>1 843 объекта за 12 лет в Москве и области до 90 км от МКАД</li>
      </ul>
      <div class="hero-cta">
        <button class="btn btn--accent btn--lg" type="button" data-goquiz>
          Рассчитать стоимость забора
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13M12 5l7 7-7 7"/></svg>
        </button>
        <span class="note" style="margin:0">6 вопросов · 1 минута<br>Не звоним, пока вы не оставите номер</span>
      </div>
    </div>

    <!-- ФОТО (в продакшене): репортажный кадр — бригада ставит евроштакетник, ямобур в кадре.
         Пока фото нет — схема расчёта участка. -->
    <div class="plan">
      <div class="plan-head"><span>План участка · расчёт</span><b>42 × 27 м</b></div>
      <figure>@@PLAN@@</figure>
      <figcaption>Так выглядит расчёт после теста: периметр, ворота, уклон и стоимость в трёх вариантах.</figcaption>
    </div>
  </div>
</section>

<!-- ================= ЦИФРЫ ================= -->
<section class="sec" style="padding-top:clamp(34px,4vw,56px); padding-bottom:0">
  <div class="wrap">
    <div class="stats">
      <div class="stat rv"><b><span data-count="12">0</span> лет</b><span>на рынке Москвы и области</span></div>
      <div class="stat rv rv-2"><b><span data-count="1843">0</span></b><span>сданных объектов</span></div>
      <div class="stat rv rv-3"><b><span data-count="9">0</span> бригад</b><span>монтажников в штате</span></div>
      <div class="stat rv rv-4"><b><span data-count="7">0</span> лет</b><span>гарантии на монтаж</span></div>
    </div>
  </div>
</section>

<!-- ================= 02. БОЛЬ ================= -->
<section class="sec">
  <div class="wrap">
    <p class="chip rv">Что обычно происходит</p>
    <h2 class="rv">Забор — та работа, где сюрпризы вылезают уже после предоплаты</h2>
    <div class="pains">
      <div class="pain rv"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 8v5M12 16.5v.5"/><circle cx="12" cy="12" r="9"/></svg><q>По телефону посчитали 180 000, а в договоре появилось 260 000: грунт не тот, доставка отдельно, ворота отдельно</q></div>
      <div class="pain rv rv-2"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 8v5M12 16.5v.5"/><circle cx="12" cy="12" r="9"/></svg><q>Бригада взяла 50% предоплаты, поставила столбы и пропала на две недели. Телефон в сети, трубку не берут</q></div>
      <div class="pain rv"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 8v5M12 16.5v.5"/><circle cx="12" cy="12" r="9"/></svg><q>На склоне секции поставили «на глаз» — линия пошла волной, снизу щели по 15 сантиметров</q></div>
      <div class="pain rv rv-2"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 8v5M12 16.5v.5"/><circle cx="12" cy="12" r="9"/></svg><q>Первая же зима: столбы выдавило из грунта, калитка перестала закрываться</q></div>
      <div class="pain pain--wide rv"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg><q>Так устроен рынок заборов: считает менеджер, ставит случайная бригада, отвечать некому. Мы 12 лет собираем компанию, в которой эта цепочка замкнута на нас</q></div>
    </div>
  </div>
</section>

<!-- ================= 03. РЕШЕНИЕ ================= -->
<section class="sec sec--tint">
  <div class="wrap">
    <p class="chip rv">Как устроен «Периметр»</p>
    <h2 class="rv">Три вещи, из-за которых у нас так не бывает</h2>
    <div class="grid g-3" style="margin-top:40px">
      <div class="card rv"><span class="tag">СВОЙ ЦЕХ</span><h3>Гнём профлист сами</h3><p>Производство в Дмитрове: гибка, покраска, сварка секций. Между заводом металла и вашим участком нет ни одного посредника — это минус 18% к стоимости материала.</p></div>
      <div class="card rv rv-2"><span class="tag">ШТАТ</span><h3>Монтажники в штате, а не на подряде</h3><p>9 бригад оформлены в ООО «Периметр». Пропасть с вашей предоплатой некому: за сроки и качество отвечает юрлицо, а не человек с объявления.</p></div>
      <div class="card rv rv-3"><span class="tag">ДОГОВОР</span><h3>Сначала смета, потом договор</h3><p>Замерщик считает на месте всё: метраж, ворота, калитку, тип грунта, уклон. Цена уходит в договор и после подписания не меняется — ни на рубль.</p></div>
    </div>
  </div>
</section>

<!-- ================= 04. ВЫГОДЫ ================= -->
<section class="sec">
  <div class="wrap">
    <p class="chip rv">Что вы получаете</p>
    <h2 class="rv">Выгода — и за счёт чего она возможна</h2>
    <div class="grid g-2" style="margin-top:44px; gap:36px 52px">
      <div class="ben rv"><div class="ben-ic"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 3v18M7 7h7a3 3 0 010 6H7m0 5h10"/></svg></div><div><h3>Экономия до 47 000 ₽ на заборе 60 метров</h3><p>За счёт того, что профлист гнём в своём цехе и везём своим транспортом — вы не оплачиваете наценку перекупщика и стороннюю логистику.</p></div></div>
      <div class="ben rv rv-2"><div class="ben-ic"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5.2l3.4 2"/></svg></div><div><h3>Монтаж за 3 дня вместо 2–3 недель</h3><p>За счёт 9 бригад в штате и собственной доставки: столбы ставим в первый день, секции и ворота — во второй и третий.</p></div></div>
      <div class="ben rv"><div class="ben-ic"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v13M8 12l4 4 4-4M4 21h16"/></svg></div><div><h3>Столбы не выдавит после первой зимы</h3><p>За счёт бурения ямобуром на 1,5 м — ниже глубины промерзания — с забутовкой щебнем. Забитый кувалдой на 80 см столб выпирает уже к марту.</p></div></div>
      <div class="ben rv rv-2"><div class="ben-ic"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 17l6-6 4 4 8-8M3 21h18"/></svg></div><div><h3>Ровная линия на уклоне до 15°</h3><p>За счёт монтажа секций «лесенкой» с шагом 20 см по нивелиру. Просветы у земли закрываем подпорной планкой — собака не подкопает.</p></div></div>
      <div class="ben rv"><div class="ben-ic"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.2 5.2l2.1 2.1M16.7 16.7l2.1 2.1M18.8 5.2l-2.1 2.1M7.3 16.7l-2.1 2.1"/><circle cx="12" cy="12" r="3.6"/></svg></div><div><h3>Ставим и в −20 °C, не откладывая до мая</h3><p>За счёт ямобура на базе ГАЗона: мёрзлый грунт он проходит так же, как летний. Зимой у нас нет очереди — и цена ниже сезонной.</p></div></div>
      <div class="ben rv rv-2"><div class="ben-ic"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><rect x="3" y="6.5" width="18" height="13" rx="2.5"/><circle cx="12" cy="13" r="3.2"/><path d="M8.5 6.5L10 4h4l1.5 2.5"/></svg></div><div><h3>Видите каждый этап, не приезжая на участок</h3><p>Прораб присылает фото и видео в 18:00 — включая скрытые работы: глубину лунок, бетонирование, узлы креплений. Всё складывается в паспорт объекта.</p></div></div>
    </div>
  </div>
</section>

<!-- ================= 05. КВИЗ ================= -->
<section class="sec sec--tint" id="quiz">
  <div class="wrap">
    <p class="chip rv">Расчёт стоимости</p>
    <h2 class="rv">Узнайте стоимость своего забора за 1 минуту</h2>
    <p class="lead rv">Шесть вопросов — и инженер пришлёт смету в трёх вариантах плюс чек-лист «7 пунктов договора, из-за которых цена вырастает уже на монтаже».</p>

    <div class="quiz rv">
      <div class="qhead">
        <div class="qmeta"><span id="qLabel">Шаг 1 из 7</span><b id="qPct">14%</b></div>
        <div class="qbar"><i id="qFill"></i></div>
      </div>

      <div class="qbody" id="qBody">
        <section class="qstep on" data-step="1">
          <h3>Что будем ограждать?</h3>
          <p class="qsub">Начнём с простого — от этого зависит высота и тип секций.</p>
          <div class="opts" data-single>
            <button class="opt" type="button">Дом в коттеджном посёлке</button>
            <button class="opt" type="button">Дачный участок</button>
            <button class="opt" type="button">Участок без построек</button>
            <button class="opt" type="button">Объект организации, стройплощадка</button>
            <button class="opt wide soft" type="button">Пока не решил — нужна консультация</button>
          </div>
        </section>
        <section class="qstep" data-step="2">
          <h3>Какой материал рассматриваете?</h3>
          <p class="qsub">Если сомневаетесь — выберите последний пункт, инженер подберёт под задачу и бюджет.</p>
          <div class="opts" data-single>
            <button class="opt" type="button">Профнастил</button>
            <button class="opt" type="button">Евроштакетник</button>
            <button class="opt" type="button">3D-сетка</button>
            <button class="opt" type="button">Сетка-рабица</button>
            <button class="opt" type="button">Забор-жалюзи</button>
            <button class="opt soft" type="button">Не знаю — подберите</button>
          </div>
        </section>
        <section class="qstep" data-step="3">
          <h3>Какой примерно периметр участка?</h3>
          <p class="qsub">Двигайте ползунок. Точный метраж замерщик уточнит на месте — сейчас нужна вилка.</p>
          <div class="slide-val"><span id="mVal">60</span><small>погонных метров</small></div>
          <input type="range" class="rng" id="meters" min="20" max="300" step="5" value="60" aria-label="Периметр участка в метрах">
          <div class="range-legend"><span>20 м</span><span>300 м</span></div>
          <label class="check" style="margin-top:20px"><input type="checkbox" id="mUnknown"> Не знаю точно — посчитайте на замере</label>
          <button class="btn btn--accent" type="button" style="margin-top:20px" data-next>Далее</button>
        </section>
        <section class="qstep" data-step="4">
          <h3>Какой рельеф на участке?</h3>
          <p class="qsub">От этого зависит, ставим секции в линию или «лесенкой» по нивелиру.</p>
          <div class="opts" data-single>
            <button class="opt" type="button">Ровный</button>
            <button class="opt" type="button">Небольшой уклон</button>
            <button class="opt" type="button">Сильный перепад, овраг</button>
            <button class="opt soft" type="button">Не знаю</button>
          </div>
        </section>
        <section class="qstep" data-step="5">
          <h3>Когда планируете ставить?</h3>
          <p class="qsub">На ближайшие две недели у нас держится резерв бригад — скажем честно, есть ли окно.</p>
          <div class="opts" data-single>
            <button class="opt" type="button">В ближайшие 2 недели</button>
            <button class="opt" type="button">В этом месяце</button>
            <button class="opt" type="button">Через 1–2 месяца</button>
            <button class="opt soft" type="button">Считаю бюджет на будущее</button>
          </div>
        </section>
        <section class="qstep" data-step="6">
          <h3>Куда отправить смету в трёх вариантах?</h3>
          <p class="qsub">Можно выбрать несколько способов — как вам удобнее.</p>
          <div class="checks">
            <label class="check"><input type="checkbox" value="WhatsApp"> WhatsApp</label>
            <label class="check"><input type="checkbox" value="Telegram"> Telegram</label>
            <label class="check"><input type="checkbox" value="SMS"> SMS</label>
            <label class="check on"><input type="checkbox" value="Консультация по телефону" checked> Бесплатная консультация по телефону — хочу узнать про акции этого месяца</label>
          </div>
          <button class="btn btn--accent" type="button" style="margin-top:20px" data-next>Далее</button>
        </section>
        <section class="qstep" data-step="7">
          <h3>Готово — смета собрана</h3>
          <p class="qsub">Осталось указать номер. Инженер пришлёт три варианта стоимости и чек-лист по договору, а на замер приедет только если вы этого захотите.</p>
          <label class="field">
            <span>Номер, на который отправить смету. За ним закрепляем скидку и чек-лист</span>
            <input type="tel" id="phone" placeholder="+7 900 000-00-00" autocomplete="tel" inputmode="tel">
          </label>
          <label class="consent"><input type="checkbox" id="agree"> Согласен на обработку персональных данных и принимаю <a href="#privacy">условия передачи информации</a></label>
          <p class="err" id="qErr">Проверьте номер: нужно не меньше 10 цифр, и поставьте галочку согласия.</p>
          <button class="btn btn--accent btn--lg btn--block" type="button" style="margin-top:20px" id="qSubmit">Получить смету в 3 вариантах</button>
          <p class="note">Ведущий инженер свяжется в течение 12 минут в рабочее время (пн–сб, 9:00–20:00).</p>
        </section>
      </div>

      <div class="qdone" id="qDone">
        <div class="tick"><svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 12.5l5 5L20 6.5"/></svg></div>
        <h3>Заявка принята</h3>
        <p>Ведущий инженер соберёт три варианта сметы по вашим параметрам и свяжется в течение 12 минут, чтобы уточнить адрес и удобное время замера. Чек-лист по договору придёт тем же сообщением.</p>
      </div>

      <div class="qfoot">
        <button class="qback" type="button" id="qBack" hidden>← Назад</button>
        <span class="mono">1 минута · без звонка до вашего номера</span>
      </div>
    </div>
  </div>
</section>

<!-- ================= 06. МАТЕРИАЛЫ ================= -->
<section class="sec">
  <div class="wrap">
    <p class="chip rv">Материалы и цены</p>
    <h2 class="rv">Пять решений — от бюджетного до «на всю жизнь»</h2>
    <p class="lead rv">Цена за погонный метр под ключ: материал, столбы, лаги, бурение, бетонирование и монтаж. Без «звёздочек».</p>
    <div class="grid g-3" style="margin-top:40px">
      <article class="mat rv"><figure class="mat-figure">@@MAT_PROF@@</figure><div class="mat-b"><h3>Профнастил С20</h3><p>Полностью закрывает участок от глаз и ветра. Полимерное покрытие с двух сторон, срок службы 25+ лет.</p><div class="price"><b>от 1 740 ₽</b><span>погонный метр<br>под ключ</span></div></div></article>
      <article class="mat rv rv-2"><figure class="mat-figure">@@MAT_SHTAK@@</figure><div class="mat-b"><h3>Евроштакетник</h3><p>Самый частый выбор в коттеджных посёлках: выглядит дороже профнастила, продувается, не парусит на ветру.</p><div class="price"><b>от 2 190 ₽</b><span>погонный метр<br>под ключ</span></div></div></article>
      <article class="mat rv rv-3"><figure class="mat-figure">@@MAT_3D@@</figure><div class="mat-b"><h3>3D-сетка</h3><p>Жёсткие сварные панели с рёбрами. Не затеняет посадки, не требует обслуживания, ставится за один день.</p><div class="price"><b>от 1 190 ₽</b><span>погонный метр<br>под ключ</span></div></div></article>
      <article class="mat rv"><figure class="mat-figure">@@MAT_RAB@@</figure><div class="mat-b"><h3>Сетка-рабица</h3><p>Временное или межсоседское ограждение. Оцинковка 2,5 мм, натяжка по тросу — не провисает через год.</p><div class="price"><b>от 690 ₽</b><span>погонный метр<br>под ключ</span></div></div></article>
      <article class="mat rv rv-2"><figure class="mat-figure">@@MAT_JAL@@</figure><div class="mat-b"><h3>Забор-жалюзи</h3><p>Ламели под углом: с улицы участок не просматривается, изнутри свет и воздух проходят. Премиальный вид.</p><div class="price"><b>от 3 480 ₽</b><span>погонный метр<br>под ключ</span></div></div></article>
      <article class="mat mat--cta rv rv-3">
        <h3>Не знаете, что выбрать?</h3>
        <p>Ответьте на 6 вопросов — инженер подберёт материал под ваш бюджет, ветровую нагрузку и высоту забора.</p>
        <button class="btn btn--light" type="button" data-goquiz style="margin-top:6px">Подобрать материал</button>
      </article>
    </div>
  </div>
</section>

<!-- ================= 07. ЭТАПЫ ================= -->
<section class="sec sec--tint">
  <div class="wrap">
    <p class="chip rv">Порядок работы</p>
    <h2 class="rv">От заявки до акта — 5 шагов и 4 дня</h2>
    <div class="steps">
      <div class="step rv"><span class="step-n">01</span><div><h3>Заявка и расчёт</h3><p>Инженер собирает вилку стоимости по вашим параметрам и присылает три варианта сметы.</p></div><span class="when">12 минут</span></div>
      <div class="step rv"><span class="step-n">02</span><div><h3>Замер на участке</h3><p>Замерщик привозит образцы металла, меряет периметр, смотрит грунт и уклон, считает ворота и калитку. Бесплатно, даже если вы откажетесь.</p></div><span class="when">1 день · бесплатно</span></div>
      <div class="step rv"><span class="step-n">03</span><div><h3>Договор с фиксированной ценой</h3><p>В договоре — смета, срок, гарантия и сумма. Предоплата 30%, остальное после сдачи. Дальше цена не меняется.</p></div><span class="when">предоплата 30%</span></div>
      <div class="step rv"><span class="step-n">04</span><div><h3>Столбы</h3><p>Бурение ямобуром на 1,5 м, выставление по нивелиру, бетонирование или забутовка щебнем — по типу грунта.</p></div><span class="when">1 день</span></div>
      <div class="step rv"><span class="step-n">05</span><div><h3>Секции, ворота и сдача</h3><p>Монтаж лаг и секций, установка ворот и калитки, уборка мусора. Подписываем акт и передаём паспорт объекта с фото скрытых работ.</p></div><span class="when">2 дня</span></div>
    </div>
  </div>
</section>

<!-- ================= 08. ФОРМА ЗАХВАТА №2 ================= -->
<section class="sec">
  <div class="wrap">
    <div class="panel panel-grid rv">
      <div>
        <h2>Приедем на бесплатный замер завтра</h2>
        <p style="margin-top:14px">Замерщик привезёт образцы металла и посчитает точную стоимость на месте. Решите не ставить — ничего не должны: замер бесплатный в любом случае.</p>
      </div>
      <form id="formMeasure" novalidate>
        <label class="field">
          <span>Ваш телефон — перезвоним, чтобы согласовать время</span>
          <input type="tel" name="phone" placeholder="+7 900 000-00-00" autocomplete="tel" inputmode="tel">
        </label>
        <label class="consent"><input type="checkbox" name="agree"> Согласен на обработку персональных данных</label>
        <p class="err">Укажите номер и подтвердите согласие.</p>
        <button class="btn btn--accent btn--block" type="submit" style="margin-top:16px">Записаться на замер</button>
      </form>
    </div>
  </div>
</section>

<!-- ================= 09. ОБЪЕКТЫ ================= -->
<section class="sec sec--tight">
  <div class="wrap">
    <p class="chip rv">Объекты</p>
    <h2 class="rv">Три недавние работы с цифрами</h2>
    <div class="grid g-3" style="margin-top:40px">
      <article class="case rv">@@CASE_SLOPE@@<div class="case-b"><span class="kicker">КП Довиль · 78 м · евроштакетник</span><h3>Участок с перепадом 2,4 метра</h3><p>Две бригады отказались: «на таком склоне ровно не встанет». Поставили секции лесенкой с шагом 20 см по нивелиру, низ закрыли подпорной планкой.</p><p class="res">Смонтировали за <b>4 дня</b>, смета не выросла ни на рубль от подписанной.</p></div></article>
      <article class="case rv rv-2">@@CASE_WINTER@@<div class="case-b"><span class="kicker">Дмитровский р-н · 112 м · профнастил</span><h3>Монтаж в феврале при −18 °C</h3><p>Клиент был уверен, что до мая ничего не сделать. Прошли мёрзлый грунт ямобуром, забутовали щебнем — по весне ни один столб не повело.</p><p class="res">Зимняя цена оказалась на <b>31 400 ₽</b> ниже майской.</p></div></article>
      <article class="case rv rv-3">@@CASE_LONG@@<div class="case-b"><span class="kicker">КП Заречье · 640 м · 3D-сетка</span><h3>Периметр посёлка для УК</h3><p>Работали по графику вместе с прокладкой сетей: три бригады параллельно, ежедневный отчёт управляющей компании.</p><p class="res">Сдали на <b>6 дней</b> раньше срока по договору.</p></div></article>
    </div>
  </div>
</section>

<!-- ================= 10. ОТЗЫВЫ ================= -->
<section class="sec sec--tint">
  <div class="wrap">
    <p class="chip rv">Отзывы</p>
    <h2 class="rv">Что пишут после сдачи объекта</h2>
    <div class="grid g-3" style="margin-top:40px">
      <div class="rev rv"><div class="stars">@@STARS@@</div><p>Брал 64 метра штакетника с откатными воротами. Больше всего боялся, что на монтаже начнётся «а вот тут доплатить». <mark>Заплатил ровно столько, сколько в договоре</mark>, хотя грунт оказался с глиной и бурили дольше.</p><footer><span class="ava">СМ</span><span class="who"><b>Сергей М.</b><span>КП Лесной берег · 64 м</span></span></footer></div>
      <div class="rev rv rv-2"><div class="stars">@@STARS@@</div><p>Живу в городе, на участок вырваться некогда. <mark>Каждый вечер приходили фото и видео</mark> — как бурили, как бетонировали, как ставили секции. Приехал уже на приёмку, придраться не к чему.</p><footer><span class="ava">ИВ</span><span class="who"><b>Ирина В.</b><span>Истринский р-н · 88 м</span></span></footer></div>
      <div class="rev rv rv-3"><div class="stars">@@STARS@@</div><p>Ставили в конце января. Соседи крутили пальцем у виска. <mark>Прошла зима, весна — ни один столб не выперло</mark>, калитка закрывается как в первый день. Плюс зимой вышло дешевле.</p><footer><span class="ava">АК</span><span class="who"><b>Андрей К.</b><span>Дмитровский р-н · 112 м</span></span></footer></div>
    </div>
  </div>
</section>

<!-- ================= 11. ГАРАНТИИ ================= -->
<section class="sec">
  <div class="wrap">
    <p class="chip rv">Гарантии</p>
    <h2 class="rv">Что будет, если что-то пойдёт не так</h2>
    <div class="grid g-4" style="margin-top:40px">
      <div class="guar rv"><b class="num">7 лет</b><h3>Гарантия на монтаж</h3><p>Столб вышел из грунта, секцию повело, калитка просела — приезжаем и переделываем за свой счёт.</p></div>
      <div class="guar rv rv-2"><b class="num">12 лет</b><h3>Гарантия на покрытие</h3><p>Полимерное покрытие от сквозной коррозии. Появилась ржавчина насквозь — меняем секцию.</p></div>
      <div class="guar rv rv-3"><b class="num">30%</b><h3>Предоплата, а не 70%</h3><p>Остальное платите после подписания акта. Договор высылаем до любой оплаты — читайте спокойно.</p></div>
      <div class="guar rv rv-4"><b class="num">40+ фото</b><h3>Паспорт объекта</h3><p>Глубина лунок, бетонирование, узлы крепления — всё снято и передано вам. Через 5 лет будет чем подтвердить гарантийный случай.</p></div>
    </div>
  </div>
</section>

<!-- ================= 12. FAQ ================= -->
<section class="sec sec--tint">
  <div class="wrap">
    <p class="chip rv">Вопросы</p>
    <h2 class="rv">О чём спрашивают чаще всего</h2>
    <div class="faq rv">
      <details><summary>Зимой правда ставите? Земля же мёрзлая</summary><div class="ans">Ставим круглый год. Мёрзлый грунт проходим ямобуром на базе ГАЗона — для техники разницы почти нет, добавляется около часа на объект. Зимой у нас нет очереди, поэтому цена ниже сезонной, а бригада выезжает через 2–3 дня после договора.</div></details>
      <details><summary>Почему у вас дороже, чем у бригады с Авито?</summary><div class="ans">Разница обычно 25–30%, и вот из чего она складывается: бурение на 1,5 м вместо забивания на 80 см, оцинкованные столбы 60×60×2 мм вместо 40×40×1,5 мм, договор с фиксированной ценой, гарантия 7 лет и юрлицо, которое отвечает за объект. Частник дешевле ровно на эти пункты — а переделка забора через две зимы стоит дороже, чем эта разница.</div></details>
      <details><summary>Цена точно не вырастет на монтаже?</summary><div class="ans">Нет. Итоговая сумма фиксируется в договоре после замера — замерщик заранее видит грунт, уклон, длину и подъезд. Если мы что-то не учли, это наша ошибка и наши расходы. За 12 лет ни одной доплаты «по факту» мы клиентам не выставляли.</div></details>
      <details><summary>У меня сильный уклон. Ровно получится?</summary><div class="ans">Да. На уклоне до 15° ставим секции лесенкой с шагом 20 см, каждая секция выводится по нивелиру, а просветы у земли закрываются подпорной планкой. На перепаде больше 15° делаем бетонный цоколь — считаем отдельно на замере.</div></details>
      <details><summary>Какая предоплата и когда остальное?</summary><div class="ans">30% после подписания договора — на материал. Остальные 70% после того, как вы приняли работу и подписали акт. Договор присылаем до оплаты, можно показать юристу.</div></details>
      <details><summary>Ворота можно поставить не сразу?</summary><div class="ans">Можно: закладываем столбы под ворота нужного сечения сейчас, а полотно и автоматику ставим когда скажете. Если заказываете вместе с забором, ворота идут со скидкой 5%.</div></details>
    </div>
  </div>
</section>

<!-- ================= 13. ФИНАЛЬНАЯ ФОРМА ================= -->
<section class="sec">
  <div class="wrap">
    <div class="final rv">
      <div>
        <p class="chip">Последний шаг</p>
        <h2>Зафиксируем цену этого месяца</h2>
        <p class="lead" style="margin-top:16px">Металл дорожает вслед за сезоном. Смета, рассчитанная в этом месяце, действует 30 дней — даже если монтаж вы запланируете на осень.</p>
        <div class="gift"><b>Подарок к заказу</b>Скидка 5% на откатные ворота с автоматикой при заказе забора до конца месяца + чек-лист «7 пунктов договора, из-за которых цена вырастает на монтаже».</div>
      </div>
      <form id="formFinal" novalidate>
        <label class="field">
          <span>Телефон, на который отправить расчёт и закрепить скидку</span>
          <input type="tel" name="phone" placeholder="+7 900 000-00-00" autocomplete="tel" inputmode="tel">
        </label>
        <label class="consent"><input type="checkbox" name="agree"> Согласен на обработку персональных данных и принимаю <a href="#privacy">условия передачи информации</a></label>
        <p class="err">Укажите номер и подтвердите согласие.</p>
        <button class="btn btn--accent btn--lg btn--block" type="submit" style="margin-top:18px">Зафиксировать цену и получить расчёт</button>
        <p class="note">Перезвоним в течение 12 минут в рабочее время. Никаких рассылок — только по вашему объекту.</p>
      </form>
    </div>
  </div>
</section>

<!-- ================= 14. ПОДВАЛ ================= -->
<footer class="foot" id="privacy">
  <div class="wrap">
    <div class="grid g-4">
      <div>
        <div class="brandmark" style="margin-bottom:16px">
          <span class="glyph" aria-hidden="true"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"><path d="M5 21V6l2.5-3L10 6v15M14 21V6l2.5-3L19 6v15M3 10h18M3 15h18"/></svg></span>
          <span><b>Периметр</b></span>
        </div>
        <p>Заборы под ключ в Москве и области. Свой цех, свои бригады, фиксированная цена в договоре.</p>
      </div>
      <div><h4>Связь</h4><ul><li><a href="tel:+74951208419">+7 495 120-84-19</a></li><li><a href="mailto:zakaz@perimetr-zabor.ru">zakaz@perimetr-zabor.ru</a></li><li>Пн–сб, 9:00–20:00</li></ul></div>
      <div><h4>Производство</h4><ul><li>Московская обл., Дмитров,<br>ул. Профессиональная, 14, стр. 3</li><li>Выезд до 90 км от МКАД</li></ul></div>
      <div><h4>Документы</h4><ul><li><a href="#privacy">Политика конфиденциальности</a></li><li><a href="#privacy">Согласие на обработку ПД</a></li><li><a href="#privacy">Образец договора</a></li></ul></div>
    </div>
    <div class="legal"><span>ООО «Периметр»</span><span>ИНН 5007112438</span><span>ОГРН 1145007002917</span><span>Учебный демонстрационный проект: компания и все данные вымышлены</span></div>
  </div>
</footer>

<div class="sticky">
  <a class="btn btn--ghost" href="tel:+74951208419">Позвонить</a>
  <button class="btn btn--accent" type="button" data-goquiz>Рассчитать</button>
</div>

<dialog id="cbDialog">
  <div class="mbox">
    <button class="mclose" type="button" aria-label="Закрыть" id="cbClose">×</button>
    <h3>Перезвоните мне</h3>
    <p>Оставьте номер — инженер наберёт в течение 12 минут в рабочее время и ответит на вопросы по вашему участку.</p>
    <form id="formCallback" novalidate>
      <label class="field"><span>Номер телефона</span><input type="tel" name="phone" placeholder="+7 900 000-00-00" autocomplete="tel" inputmode="tel"></label>
      <label class="consent"><input type="checkbox" name="agree"> Согласен на обработку персональных данных</label>
      <p class="err">Укажите номер и подтвердите согласие.</p>
      <button class="btn btn--accent btn--block" type="submit" style="margin-top:16px">Жду звонка</button>
    </form>
  </div>
</dialog>
"""


# ================================================================ СКРИПТ
JS = r"""
(function(){
  "use strict";
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!reduce && "IntersectionObserver" in window) document.documentElement.classList.add("js");

  /* ——— шапка при скролле ——— */
  var top = document.getElementById("top");
  var onScroll = function(){ top.classList.toggle("stuck", window.scrollY > 8); };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ——— появление блоков ——— */
  var rvs = document.querySelectorAll(".rv");
  var counted = false;
  if (reduce || !("IntersectionObserver" in window)) {
    rvs.forEach(function(el){ el.classList.add("in"); });
    countUp();
  } else {
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if (!e.isIntersecting) return;
        e.target.classList.add("in");
        io.unobserve(e.target);
        if (e.target.querySelector("[data-count]")) countUp();
      });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.1 });
    rvs.forEach(function(el){ io.observe(el); });
  }

  /* ——— счётчики ——— */
  function countUp(){
    if (counted) return;
    counted = true;
    document.querySelectorAll("[data-count]").forEach(function(el){
      var target = parseInt(el.getAttribute("data-count"), 10);
      if (reduce) { el.textContent = fmt(target); return; }
      var t0 = null, dur = 1100;
      function tick(ts){
        if (t0 === null) t0 = ts;
        var p = Math.min(1, (ts - t0) / dur);
        var eased = 1 - Math.pow(1 - p, 3);
        el.textContent = fmt(Math.round(target * eased));
        if (p < 1) requestAnimationFrame(tick);
      }
      requestAnimationFrame(tick);
    });
  }
  function fmt(n){ return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, " "); }

  /* ——— переход к квизу ——— */
  document.querySelectorAll("[data-goquiz]").forEach(function(b){
    b.addEventListener("click", function(){
      document.getElementById("quiz").scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    });
  });

  document.querySelectorAll(".consent a").forEach(function(a){
    a.addEventListener("click", function(e){ e.stopPropagation(); });
  });

  /* ——— квиз ——— */
  var steps = Array.prototype.slice.call(document.querySelectorAll(".qstep"));
  var total = steps.length, idx = 0, answers = {};
  var qLabel = document.getElementById("qLabel"),
      qPct = document.getElementById("qPct"),
      qFill = document.getElementById("qFill"),
      qBack = document.getElementById("qBack");

  function show(i){
    idx = Math.max(0, Math.min(total - 1, i));
    steps.forEach(function(s, n){ s.classList.toggle("on", n === idx); });
    var pct = Math.round((idx + 1) / total * 100);
    qLabel.textContent = "Шаг " + (idx + 1) + " из " + total;
    qPct.textContent = pct + "%";
    qFill.style.width = pct + "%";
    qBack.hidden = idx === 0;
  }
  function next(){ if (idx < total - 1) show(idx + 1); }

  qBack.addEventListener("click", function(){ show(idx - 1); });
  document.querySelectorAll("[data-next]").forEach(function(b){ b.addEventListener("click", next); });

  document.querySelectorAll(".opts[data-single]").forEach(function(group){
    group.addEventListener("click", function(e){
      var opt = e.target.closest(".opt");
      if (!opt) return;
      group.querySelectorAll(".opt").forEach(function(o){ o.classList.remove("sel"); });
      opt.classList.add("sel");
      answers[group.closest(".qstep").querySelector("h3").textContent] = opt.textContent.trim();
      setTimeout(next, reduce ? 0 : 260);
    });
  });

  var meters = document.getElementById("meters"),
      mVal = document.getElementById("mVal"),
      mUnknown = document.getElementById("mUnknown");
  meters.addEventListener("input", function(){
    mVal.textContent = meters.value;
    answers["Периметр"] = meters.value + " м";
    if (mUnknown.checked) { mUnknown.checked = false; mUnknown.closest(".check").classList.remove("on"); }
  });
  mUnknown.addEventListener("change", function(){
    mUnknown.closest(".check").classList.toggle("on", mUnknown.checked);
    answers["Периметр"] = mUnknown.checked ? "не знает — считаем на замере" : meters.value + " м";
  });

  document.querySelectorAll(".checks .check input").forEach(function(c){
    c.addEventListener("change", function(){
      c.closest(".check").classList.toggle("on", c.checked);
      answers["Куда отправить"] = Array.prototype.slice
        .call(document.querySelectorAll(".checks .check input:checked"))
        .map(function(x){ return x.value; }).join(", ");
    });
  });

  function digits(v){ return (v || "").replace(/\D/g, "").length; }

  var qErr = document.getElementById("qErr");
  document.getElementById("qSubmit").addEventListener("click", function(){
    var phone = document.getElementById("phone"), agree = document.getElementById("agree");
    if (digits(phone.value) < 10 || !agree.checked) { qErr.classList.add("on"); phone.focus(); return; }
    qErr.classList.remove("on");
    answers["Телефон"] = phone.value;
    /* Точка интеграции: отправка в Битрикс24 / Telegram-бот + цель аналитики
       (например ym(XXXXXX,'reachGoal','quiz_lead')). */
    console.log("Заявка из квиза:", answers);
    document.getElementById("qBody").style.display = "none";
    document.querySelector(".qfoot").style.display = "none";
    document.getElementById("qDone").classList.add("on");
  });

  /* ——— короткие формы ——— */
  function handleForm(form, title, text){
    if (!form) return;
    form.addEventListener("submit", function(e){
      e.preventDefault();
      var phone = form.querySelector('input[type="tel"]'),
          agree = form.querySelector('input[type="checkbox"]'),
          err = form.querySelector(".err");
      if (digits(phone.value) < 10 || !agree.checked) { err.classList.add("on"); phone.focus(); return; }
      /* Точка интеграции: отправка заявки + цель аналитики. */
      console.log("Заявка (" + title + "):", phone.value);
      form.innerHTML = '<h3 style="margin-bottom:10px">' + title + '</h3><p style="font-size:15px; opacity:.85">' + text + '</p>';
    });
  }
  handleForm(document.getElementById("formMeasure"), "Записали на замер",
    "Перезвоним в течение 12 минут, чтобы согласовать удобное время. Замерщик привезёт образцы металла.");
  handleForm(document.getElementById("formFinal"), "Цена зафиксирована",
    "Расчёт и чек-лист по договору пришлём на этот номер. Скидка 5% на ворота закреплена за вами на 30 дней.");
  handleForm(document.getElementById("formCallback"), "Заявка принята",
    "Инженер наберёт вас в течение 12 минут в рабочее время.");

  /* ——— модалка ——— */
  var dlg = document.getElementById("cbDialog");
  document.querySelectorAll("[data-callback]").forEach(function(b){
    b.addEventListener("click", function(){
      if (dlg.showModal) dlg.showModal(); else document.getElementById("quiz").scrollIntoView();
    });
  });
  document.getElementById("cbClose").addEventListener("click", function(){ dlg.close(); });
  dlg.addEventListener("click", function(e){ if (e.target === dlg) dlg.close(); });

  show(0);
})();
"""

STAR = ('<svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor">'
        '<path d="M12 2.6l2.9 5.9 6.5.9-4.7 4.6 1.1 6.5L12 17.4 6.2 20.5l1.1-6.5L2.6 9.4l6.5-.9z"/></svg>')

# ================================================================ СБОРКА
def assemble():
    html = BODY
    for token, value in [
        ("@@HERO@@", hero_art()),
        ("@@PLAN@@", plan_art()),
        ("@@MAT_PROF@@", mat_prof()),
        ("@@MAT_SHTAK@@", mat_shtak()),
        ("@@MAT_3D@@", mat_3d()),
        ("@@MAT_RAB@@", mat_rab()),
        ("@@MAT_JAL@@", mat_jal()),
        ("@@CASE_SLOPE@@", scene_slope()),
        ("@@CASE_WINTER@@", scene_winter()),
        ("@@CASE_LONG@@", scene_long()),
        ("@@STARS@@", STAR * 5),
    ]:
        html = html.replace(token, value)

    head = "<title>Периметр</title>\n<style>" + CSS + "</style>"
    page = head + "\n" + html + "\n<script>" + JS + "</script>\n"
    open("page.html", "w", encoding="utf-8").write(page)

    standalone = ('<!doctype html>\n<html lang="ru">\n<head>\n'
                  '<meta charset="utf-8">\n'
                  '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
                  '<meta name="description" content="Заборы под ключ в Москве и области за 3 дня. '
                  'Свой цех профлиста, 9 бригад в штате, цена фиксируется в договоре. '
                  'Рассчитайте стоимость за 1 минуту.">\n'
                  '<meta name="theme-color" content="#0F5A3D">\n'
                  + head + '\n</head>\n<body>' + html + '\n<script>' + JS + '</script>\n</body>\n</html>\n')
    open("index.html", "w", encoding="utf-8").write(standalone)
    return len(page), len(standalone)


if __name__ == "__main__":
    a, b = assemble()
    print("page.html %.1f КБ · index.html %.1f КБ" % (a / 1024, b / 1024))
