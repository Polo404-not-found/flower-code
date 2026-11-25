import math
import sys
import numpy as np
import pygame

pygame.init()
ancho, alto = 1280, 920
pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Jardín de Lirios ASCII - Modo 2D y Modo 3D")
reloj = pygame.time.Clock()

fuente_ascii = pygame.font.SysFont("Consolas", 9) if pygame.font.match_font("consolas") else pygame.font.Font(None, 12)
fuente_ui = pygame.font.Font(None, 24)
fuente_peq = pygame.font.Font(None, 20)
fuente_mini = pygame.font.Font(None, 18)

cache_chars = {}


def render_char(ch, color):
  col_tuple = (int(color[0]), int(color[1]), int(color[2]))
  key = (ch, col_tuple)
  if key not in cache_chars:
    cache_chars[key] = fuente_ascii.render(ch, True, col_tuple)
  return cache_chars[key]


NOMBRES_TIPOS = [
    "Lirio Stargazer",
    "Lirio Tigre",
    "Lirio Trompeta",
    "Lirio Asiático",
    "Lirio Araña",
]


def mapear_paleta(t, c0, c1, c2, c3):
  t_norm = np.clip(t, 0.0, 1.0)
  m1 = t_norm < 0.33
  m2 = (t_norm >= 0.33) & (t_norm < 0.66)
  m3 = t_norm >= 0.66

  colores = np.empty((len(t_norm), 3), dtype=np.float32)

  f1 = (t_norm[m1] / 0.33)[:, None]
  colores[m1] = c0 * (1.0 - f1) + c1 * f1

  f2 = ((t_norm[m2] - 0.33) / 0.33)[:, None]
  colores[m2] = c1 * (1.0 - f2) + c2 * f2

  f3 = ((t_norm[m3] - 0.66) / 0.34)[:, None]
  colores[m3] = c2 * (1.0 - f3) + c3 * f3

  return colores


def generar_lirio_3d(semilla=21, tipo_forzado=None):
  rng = np.random.default_rng(semilla)
  tipo = (tipo_forzado % 5) if tipo_forzado is not None else int(rng.integers(0, 5))

  c0 = np.array([255.0, rng.uniform(90.0, 160.0), rng.uniform(0.0, 30.0)])
  c1 = np.array([255.0, rng.uniform(30.0, 75.0), rng.uniform(95.0, 145.0)])
  c2 = np.array([rng.uniform(175.0, 220.0), rng.uniform(20.0, 55.0), 255.0])
  c3 = np.array([rng.uniform(85.0, 135.0), rng.uniform(10.0, 35.0), 255.0])

  rad_max = 245.0
  puntos = []

  for y_s in np.linspace(0.0, 360.0, 65):
    frac_s = y_s / 360.0
    r_stem = 8.5 * (1.0 - frac_s * 0.25)
    curv_stem = math.sin(frac_s * math.pi * 0.85) * 18.0
    for a_s in np.linspace(0.0, 2 * math.pi, 12, endpoint=False):
      sx = curv_stem + r_stem * math.cos(a_s)
      sz = r_stem * math.sin(a_s)
      col_s = np.array([75.0, 195.0 - frac_s * 50.0, 95.0 + frac_s * 75.0])
      ch_s = "|" if abs(math.cos(a_s)) < 0.6 else ("/" if math.cos(a_s) > 0 else "\\")
      puntos.append((sx, y_s, sz, ch_s, col_s, (1.0 - frac_s) * 0.9, 0.0))

  n_hojas = 4
  for h_idx in range(n_hojas):
    ang_h = h_idx * (2 * math.pi / n_hojas) + 0.45
    y_base_h = 100.0 + h_idx * 60.0
    len_hoja = 180.0
    for u_h in np.linspace(0.05, 1.0, 32):
      r_h = u_h * len_hoja
      y_h = y_base_h - math.sin(u_h * math.pi * 0.6) * 40.0 + (u_h ** 2.2) * 60.0
      ancho_h = math.sin(u_h * math.pi) * 24.0
      for w_h in np.linspace(-ancho_h, ancho_h, max(3, int(ancho_h / 3.0))):
        perp_h = ang_h + math.pi / 2.0
        hx = r_h * math.cos(ang_h) + w_h * math.cos(perp_h)
        hz = r_h * math.sin(ang_h) + w_h * math.sin(perp_h)
        col_h = np.array([70.0 + u_h * 35.0, 205.0 - u_h * 40.0, 95.0 + u_h * 65.0])
        ch_h = ">" if w_h > 0 else "<"
        if u_h > 0.92:
          ch_h = "^"
        elif abs(w_h) > ancho_h * 0.65:
          ch_h = "~"
        puntos.append((hx, y_h, hz, ch_h, col_h, 0.8 + u_h * 0.4, 0.0))

  for _ in range(130):
    r_c = rng.uniform(0.0, 25.0)
    ang_c = rng.uniform(0.0, 2 * math.pi)
    cy_off = rng.uniform(-10.0, 8.0)
    cx_p = r_c * math.cos(ang_c)
    cz_p = r_c * math.sin(ang_c)
    t_pal_c = (r_c / 25.0) * 0.22
    col_c = mapear_paleta(np.array([t_pal_c]), c0, c1, c2, c3)[0]
    ch_c = rng.choice(["@", "8", "%", "O", "0", "*", "&", "Q", "$"])
    puntos.append((cx_p, cy_off, cz_p, ch_c, col_c, 1.15 + rng.uniform(0.0, 0.25), 1.0))

  n_petalos = 6
  for p in range(n_petalos):
    ang_base = p * (2 * math.pi / n_petalos)
    es_int = (p % 2 == 1)
    r_pet_max = rad_max * (0.92 if es_int else 1.06)
    ang_elev = math.radians(46.0 if es_int else 56.0)

    if tipo == 1:
      curv_tip = 165.0
    elif tipo == 2:
      curv_tip = 45.0
      ang_elev = math.radians(65.0 if es_int else 72.0)
    elif tipo == 4:
      curv_tip = 100.0
    else:
      curv_tip = 95.0

    for u in np.linspace(0.04, 1.0, 48):
      r_dist = u * r_pet_max
      h_y = -math.sin(ang_elev) * r_dist + (u ** 2.2) * curv_tip
      r_horiz = math.cos(ang_elev) * r_dist + (u ** 1.8) * 35.0

      if tipo == 4:
        ancho_w = math.sin(u * math.pi) * 16.0
        n_w = 4
      elif tipo == 3:
        ancho_w = math.sin(u * math.pi) * (58.0 if es_int else 66.0)
        n_w = max(3, int(ancho_w / 3.8))
      else:
        ancho_w = math.sin(u * math.pi) * (50.0 if es_int else 58.0)
        n_w = max(3, int(ancho_w / 4.0))

      for w in np.linspace(-ancho_w, ancho_w, n_w):
        perp_ang = ang_base + math.pi / 2.0
        px = r_horiz * math.cos(ang_base) + w * math.cos(perp_ang)
        pz = r_horiz * math.sin(ang_base) + w * math.sin(perp_ang)
        cup_y = ((w / (ancho_w + 1e-5)) ** 2) * 15.0
        py = h_y + cup_y

        t_p = u
        col_p = mapear_paleta(np.array([t_p]), c0, c1, c2, c3)[0]

        if abs(w) < 3.0:
          ch_p = "|" if abs(math.cos(ang_base)) < 0.5 else ("/" if math.cos(ang_base) > 0 else "\\")
        elif u < 0.2:
          ch_p = "@" if abs(w) < ancho_w * 0.4 else "%"
        elif u > 0.88:
          ch_p = "^" if abs(w) < 4.0 else rng.choice(["(", ")", "{", "}", "~"])
        else:
          ch_p = ":" if (abs(w) > ancho_w * 0.35 and rng.random() < 0.32) else rng.choice(["*", "o", "S", "s", "x", "a", "(", ")"])

        puntos.append((px, py, pz, ch_p, col_p, 1.25 + u * 1.3, 1.0))

  for s_idx in range(6):
    ang_stamen = s_idx * (2 * math.pi / 6.0) + 0.32
    r_st_max = rad_max * (0.62 if tipo != 1 else 0.78)
    for u_st in np.linspace(0.05, 1.0, 28):
      r_st = u_st * r_st_max
      sy = -math.sin(math.radians(62.0)) * r_st + (u_st ** 2.0) * 22.0
      sx = math.cos(math.radians(62.0)) * r_st * math.cos(ang_stamen)
      sz = math.cos(math.radians(62.0)) * r_st * math.sin(ang_stamen)

      col_st = np.array([255.0, 185.0 - u_st * 55.0, 25.0 + u_st * 85.0])
      ch_st = "-" if u_st < 0.88 else "T"

      if u_st >= 0.88:
        col_st = np.array([255.0, 120.0, 15.0])
        for a_off in [-4.0, 0.0, 4.0]:
          a_ang = ang_stamen + math.pi / 2.0
          ax = sx + a_off * math.cos(a_ang)
          az = sz + a_off * math.sin(a_ang)
          puntos.append((ax, sy, az, "o", col_st, 1.45 + u_st * 0.45, 1.0))

      puntos.append((sx, sy, sz, ch_st, col_st, 1.45 + u_st * 0.45, 1.0))

  for u_p in np.linspace(0.05, 1.0, 32):
    r_p = u_p * (rad_max * 0.72)
    py = -math.sin(math.radians(72.0)) * r_p
    px = math.cos(math.radians(72.0)) * r_p * 0.3
    pz = 0.0
    col_pistilo = np.array([110.0 + u_p * 130.0, 245.0 - u_p * 60.0, 90.0])
    ch_pistilo = "|" if u_p < 0.9 else "Y"
    puntos.append((px, py, pz, ch_pistilo, col_pistilo, 1.55 + u_p * 0.35, 1.0))

  for _ in range(140):
    px_pol = rng.uniform(-rad_max * 0.65, rad_max * 0.65)
    py_pol = rng.uniform(-rad_max * 0.85, 40.0)
    pz_pol = rng.uniform(-rad_max * 0.65, rad_max * 0.65)
    ch_pol = rng.choice([".", "*", "+", "'", "`", ":"])
    col_pol = np.array([255.0, rng.uniform(160.0, 220.0), rng.uniform(20.0, 80.0)])
    puntos.append((px_pol, py_pol, pz_pol, ch_pol, col_pol, 1.7 + rng.uniform(0.0, 0.6), 1.0))

  return tipo, puntos, c0, c1, c2, c3


def generar_jardin_lirios_2d(semilla=21, tipo_forzado=None):
  rng = np.random.default_rng(semilla)
  tipo = (tipo_forzado % 5) if tipo_forzado is not None else int(rng.integers(0, 5))

  c0 = np.array([255.0, rng.uniform(90.0, 160.0), rng.uniform(0.0, 30.0)])
  c1 = np.array([255.0, rng.uniform(30.0, 75.0), rng.uniform(95.0, 145.0)])
  c2 = np.array([rng.uniform(175.0, 220.0), rng.uniform(20.0, 55.0), 255.0])
  c3 = np.array([rng.uniform(85.0, 135.0), rng.uniform(10.0, 35.0), 255.0])

  tallos = [
      (0.0, 810.0, 435.0, 1.0, 185.0),
      (-310.0, 810.0, 350.0, 0.82, 145.0),
      (310.0, 810.0, 370.0, 0.86, 150.0),
      (-155.0, 810.0, 275.0, 0.68, 115.0),
      (155.0, 810.0, 295.0, 0.72, 122.0),
  ]

  puntos = []

  for bx in np.linspace(-620.0, 620.0, 220):
    for gy in range(0, int(rng.integers(2, 6))):
      ch_g = rng.choice(['"', "'", ",", "~", "|", "^", ":", "`", ";"])
      col_g = np.array([rng.uniform(50.0, 95.0), rng.uniform(160.0, 235.0), rng.uniform(70.0, 130.0)])
      puntos.append((bx + rng.uniform(-4.0, 4.0), 810.0 - gy * 6.5, ch_g, col_g, 0.08, 0.0, 0))

  for f_id, (bx, by_ground, h_tallo, escala_f, rad_max) in enumerate(tallos):
    n_seg = int(h_tallo / 4.2)
    curv_total = (28.0 if f_id in [0, 2, 4] else -28.0) * (0.8 + 0.4 * escala_f)
    for s in range(n_seg):
      frac = s / float(n_seg)
      y_s = by_ground - frac * h_tallo
      curv = math.sin(frac * math.pi * 0.85) * curv_total
      x_s = bx + curv
      for w_off in [-4.0, -2.0, 0.0, 2.0, 4.0]:
        ch_t = "|" if abs(curv) < 10.0 else ("/" if curv > 0 else "\\")
        if w_off < 0:
          col_stem = np.array([95.0, 210.0 - frac * 50.0, 115.0 + frac * 75.0])
        elif w_off == 0:
          col_stem = np.array([80.0, 190.0 - frac * 50.0, 100.0 + frac * 80.0])
        else:
          col_stem = np.array([60.0, 160.0 - frac * 50.0, 80.0 + frac * 85.0])
        t_ign_stem = frac * 1.15
        puntos.append((x_s + w_off, y_s, ch_t, col_stem, t_ign_stem, frac, f_id + 1))

      if s > 6 and s % 4 == 0:
        dir_h = 1.0 if (s // 4) % 2 == 0 else -1.0
        n_hoja = int(rng.integers(12, 18))
        for l in range(1, n_hoja):
          frac_l = l / float(n_hoja)
          lx = x_s + dir_h * l * 8.5
          ly = y_s - l * 4.2 + math.sin(frac_l * math.pi) * 6.5
          for h_w in [-1.5, 0.0, 1.5]:
            ch_h = ">" if dir_h > 0 else "<"
            if l == n_hoja - 1:
              ch_h = "^"
            elif h_w != 0:
              ch_h = "~"
            col_leaf = np.array([75.0 + frac_l * 40.0, 210.0 - frac_l * 50.0, 95.0 + frac_l * 70.0])
            puntos.append((lx, ly + h_w, ch_h, col_leaf, t_ign_stem + 0.15, frac, f_id + 1))

    c_x = bx + math.sin(math.pi * 0.85) * curv_total
    c_y = by_ground - h_tallo

    for _ in range(int(90 * escala_f)):
      r_cent = rng.uniform(0.0, 18.0 * escala_f)
      ang_c = rng.uniform(0.0, 2 * math.pi)
      cx_p = c_x + r_cent * math.cos(ang_c)
      cy_p = c_y + r_cent * math.sin(ang_c)
      ch_c = rng.choice(["@", "8", "%", "O", "0", "*", "&", "Q", "$"])
      t_pal_c = (r_cent / (18.0 * escala_f)) * 0.2
      col_cent = mapear_paleta(np.array([t_pal_c]), c0, c1, c2, c3)[0]
      puntos.append((cx_p, cy_p, ch_c, col_cent, 1.25 + rng.uniform(0.0, 0.3), 1.0, f_id + 1))

    n_petalos = 6
    if tipo == 0:
      for p in range(n_petalos):
        ang_base = p * (2 * math.pi / n_petalos) - math.pi / 2.0
        for r_step in np.linspace(6.0, rad_max, 46):
          frac_r = r_step / rad_max
          ancho_ang = math.sin(frac_r * math.pi) * 0.34
          n_d = max(3, int(18 * math.sin(frac_r * math.pi)))
          for dang in np.linspace(-ancho_ang, ancho_ang, n_d):
            ang = ang_base + dang
            r_curv = r_step * (1.0 - 0.14 * (frac_r ** 2.2))
            px = c_x + r_curv * math.cos(ang)
            py = c_y + r_curv * math.sin(ang) * 0.82
            t_p = frac_r
            col_p = mapear_paleta(np.array([t_p]), c0, c1, c2, c3)[0]
            if abs(dang) < 0.02:
              ch_p = "|" if abs(math.cos(ang)) < 0.5 else ("/" if math.cos(ang) > 0 else "\\")
            elif frac_r < 0.2:
              ch_p = "@" if abs(dang) < 0.08 else "%"
            elif frac_r > 0.88:
              ch_p = "^" if abs(dang) < 0.05 else rng.choice(["(", ")", "{", "}", "~"])
            else:
              ch_p = ":" if (abs(dang) > 0.08 and rng.random() < 0.35) else rng.choice(["*", "o", "S", "s", "x", "a", "(", ")"])
            puntos.append((px, py, ch_p, col_p, 1.35 + frac_r * 1.3, 1.0, f_id + 1))

    elif tipo == 1:
      for p in range(n_petalos):
        ang_base = p * (2 * math.pi / n_petalos) - math.pi / 2.0
        for r_step in np.linspace(6.0, rad_max * 1.2, 48):
          frac_r = r_step / (rad_max * 1.2)
          ancho_ang = math.sin(frac_r * math.pi * 0.9) * 0.28
          n_d = max(3, int(15 * math.sin(frac_r * math.pi * 0.9)))
          for dang in np.linspace(-ancho_ang, ancho_ang, n_d):
            ang = ang_base + dang
            r_curv = r_step * (1.0 - 0.3 * (frac_r ** 2.3))
            px = c_x + r_curv * math.cos(ang)
            py = c_y + r_curv * math.sin(ang) * 0.76
            t_p = frac_r * 0.95
            col_p = mapear_paleta(np.array([t_p]), c0, c1, c2, c3)[0]
            ch_p = "~" if frac_r > 0.82 else (":" if (abs(dang) > 0.07 and rng.random() < 0.38) else rng.choice(["*", "(", ")", "/", "\\", "s", "z", "x"]))
            puntos.append((px, py, ch_p, col_p, 1.35 + frac_r * 1.3, 1.0, f_id + 1))

    elif tipo == 2:
      for p in range(n_petalos):
        ang_base = p * (2 * math.pi / n_petalos) - math.pi / 2.0
        for r_step in np.linspace(8.0, rad_max * 1.1, 44):
          frac_r = r_step / (rad_max * 1.1)
          ancho_ang = (0.08 + 0.35 * (frac_r ** 1.7))
          n_d = max(3, int(16 * ancho_ang))
          for dang in np.linspace(-ancho_ang, ancho_ang, n_d):
            ang = ang_base + dang
            px = c_x + r_step * math.cos(ang)
            py = c_y + r_step * math.sin(ang) * 0.88
            t_p = frac_r
            col_p = mapear_paleta(np.array([t_p]), c0, c1, c2, c3)[0]
            ch_p = rng.choice(["/", "\\", "|", "!"]) if frac_r < 0.55 else rng.choice(["*", "^", "(", ")", "~", "v", "Y", "s"])
            puntos.append((px, py, ch_p, col_p, 1.35 + frac_r * 1.2, 1.0, f_id + 1))

    elif tipo == 3:
      for p in range(n_petalos):
        ang_base = p * (2 * math.pi / n_petalos) - math.pi / 2.0
        for r_step in np.linspace(8.0, rad_max * 1.0, 44):
          frac_r = r_step / (rad_max * 1.0)
          ancho_ang = math.sin(frac_r * math.pi) * 0.38
          n_d = max(3, int(18 * math.sin(frac_r * math.pi)))
          for dang in np.linspace(-ancho_ang, ancho_ang, n_d):
            ang = ang_base + dang
            px = c_x + r_step * math.cos(ang)
            py = c_y + r_step * math.sin(ang) * 0.84
            t_p = (0.0 if frac_r < 0.35 else (frac_r - 0.35) / 0.65)
            col_p = mapear_paleta(np.array([t_p]), c0, c1, c2, c3)[0]
            ch_p = "@" if frac_r < 0.28 else rng.choice(["*", "o", "(", ")", "^", "S", "+", "%", "x"])
            puntos.append((px, py, ch_p, col_p, 1.35 + frac_r * 1.2, 1.0, f_id + 1))

    else:
      for p in range(n_petalos):
        ang_base = p * (2 * math.pi / n_petalos) - math.pi / 2.0
        for r_step in np.linspace(8.0, rad_max * 1.35, 52):
          frac_r = r_step / (rad_max * 1.35)
          curv_onda = math.sin(frac_r * 4.5) * 16.0
          for d_w in [-2.4, -1.2, 0.0, 1.2, 2.4]:
            ang = ang_base + (curv_onda + d_w) * 0.016
            px = c_x + r_step * math.cos(ang)
            py = c_y + r_step * math.sin(ang) * 0.8
            t_p = frac_r
            col_p = mapear_paleta(np.array([t_p]), c0, c1, c2, c3)[0]
            ch_p = "~" if frac_r > 0.75 else rng.choice(["-", "~", "'", "*", "`", "s"])
            puntos.append((px, py, ch_p, col_p, 1.35 + frac_r * 1.3, 1.0, f_id + 1))

    for s_idx in range(6):
      ang_stamen = s_idx * (2 * math.pi / 6.0) - math.pi / 2.0 + 0.35
      for r_st in np.linspace(6.0, rad_max * 0.6, 26):
        frac_st = r_st / (rad_max * 0.6)
        curv_st = math.sin(frac_st * math.pi * 0.65) * 20.0
        sx = c_x + r_st * math.cos(ang_stamen) - curv_st * math.sin(ang_stamen)
        sy = c_y + r_st * math.sin(ang_stamen) * 0.85 + curv_st * math.cos(ang_stamen) * 0.5
        col_stamen = np.array([255.0, 185.0 - frac_st * 55.0, 25.0 + frac_st * 85.0])
        ch_stamen = "-" if frac_st < 0.88 else "T"
        if frac_st >= 0.88:
          col_stamen = np.array([255.0, 115.0, 15.0])
          for a_off in [-3.5, 0.0, 3.5]:
            puntos.append((sx + a_off, sy, "o", col_stamen, 1.5 + frac_st * 0.45, 1.0, f_id + 1))
        puntos.append((sx, sy, ch_stamen, col_stamen, 1.5 + frac_st * 0.45, 1.0, f_id + 1))

    pistilo_ang = -math.pi / 2.0
    for r_p in np.linspace(6.0, rad_max * 0.7, 28):
      frac_p = r_p / (rad_max * 0.7)
      px = c_x + r_p * math.cos(pistilo_ang)
      py = c_y + r_p * math.sin(pistilo_ang) * 0.85
      col_pistilo = np.array([110.0 + frac_p * 130.0, 245.0 - frac_p * 60.0, 90.0])
      ch_pistilo = "|" if frac_p < 0.9 else "Y"
      puntos.append((px, py, ch_pistilo, col_pistilo, 1.6 + frac_p * 0.35, 1.0, f_id + 1))

    for _ in range(int(55 * escala_f)):
      px_pol = c_x + rng.uniform(-rad_max * 0.75, rad_max * 0.75)
      py_pol = c_y + rng.uniform(-rad_max * 0.55, rad_max * 0.55)
      ch_pol = rng.choice([".", "*", "+", "'", "`", ":"])
      col_pol = np.array([255.0, rng.uniform(160.0, 220.0), rng.uniform(20.0, 80.0)])
      puntos.append((px_pol, py_pol, ch_pol, col_pol, 1.8 + rng.uniform(0.0, 0.6), 1.0, f_id + 1))

  return tipo, puntos, c0, c1, c2, c3


semilla_actual = 21
if len(sys.argv) > 1 and sys.argv[1].isdigit():
  semilla_actual = int(sys.argv[1])

modo_3d = True
tipo_forzado = None

tipo_actual_3d, puntos_3d, c0_3d, c1_3d, c2_3d, c3_3d = generar_lirio_3d(semilla_actual, tipo_forzado)
tipo_actual_2d, puntos_2d, c0_2d, c1_2d, c2_2d, c3_2d = generar_jardin_lirios_2d(semilla_actual, tipo_forzado)

rot_x = 0.42
rot_y = 0.0
distancia_camara = 620.0
fov = 760.0
cx_3d = ancho // 2
cy_3d = alto // 2 + 50

zoom_2d = 1.0
pan_x_2d = 0.0
pan_y_2d = 0.0

petalos_caidos = []
tiempo_total = 0.0
tiempo_entrada = 0.0
pausado = False
viento_rafaga = 0.0

texto_seed = str(semilla_actual)
input_activo = False

input_rect = pygame.Rect(20, 16, 175, 36)
boton_rand_rect = pygame.Rect(205, 16, 105, 36)
boton_tipo_rect = pygame.Rect(320, 16, 215, 36)
boton_modo_rect = pygame.Rect(545, 16, 140, 36)
boton_viento_rect = pygame.Rect(695, 16, 105, 36)

corriendo = True
while corriendo:
  dt = reloj.tick(60) / 1000.0
  tiempo_total += dt
  tiempo_entrada += dt

  if viento_rafaga > 0.0:
    viento_rafaga = max(0.0, viento_rafaga - dt * 1.5)

  if modo_3d and not pausado:
    rot_y += dt * 0.22

  for evento in pygame.event.get():
    if evento.type == pygame.QUIT:
      corriendo = False
    elif evento.type == pygame.MOUSEBUTTONDOWN:
      if evento.button == 1:
        if input_rect.collidepoint(evento.pos):
          input_activo = True
        elif boton_rand_rect.collidepoint(evento.pos):
          semilla_actual = int(np.random.default_rng().integers(1, 10000000))
          texto_seed = str(semilla_actual)
          tipo_actual_3d, puntos_3d, c0_3d, c1_3d, c2_3d, c3_3d = generar_lirio_3d(semilla_actual, tipo_forzado)
          tipo_actual_2d, puntos_2d, c0_2d, c1_2d, c2_2d, c3_2d = generar_jardin_lirios_2d(semilla_actual, tipo_forzado)
          petalos_caidos.clear()
          tiempo_entrada = 0.0
          input_activo = False
        elif boton_tipo_rect.collidepoint(evento.pos):
          tipo_actual_ref = tipo_actual_3d if modo_3d else tipo_actual_2d
          tipo_forzado = (tipo_actual_ref + 1) % 5
          tipo_actual_3d, puntos_3d, c0_3d, c1_3d, c2_3d, c3_3d = generar_lirio_3d(semilla_actual, tipo_forzado)
          tipo_actual_2d, puntos_2d, c0_2d, c1_2d, c2_2d, c3_2d = generar_jardin_lirios_2d(semilla_actual, tipo_forzado)
          petalos_caidos.clear()
          tiempo_entrada = 0.0
          input_activo = False
        elif boton_modo_rect.collidepoint(evento.pos):
          modo_3d = not modo_3d
          tiempo_entrada = 0.0
          input_activo = False
        elif boton_viento_rect.collidepoint(evento.pos):
          viento_rafaga = 3.5
          rng_desp = np.random.default_rng()
          if modo_3d:
            for p in puntos_3d:
              if p[6] > 0.75 and rng_desp.random() < 0.16:
                vx_p = rng_desp.uniform(-110.0, 110.0)
                vy_p = rng_desp.uniform(-130.0, -30.0)
                vz_p = rng_desp.uniform(-110.0, 110.0)
                petalos_caidos.append([p[0], p[1], p[2], vx_p, vy_p, vz_p, p[3], p[4], 0.0])
          else:
            for p in puntos_2d:
              if p[5] > 0.75 and rng_desp.random() < 0.15:
                vx_p = rng_desp.uniform(50.0, 200.0)
                vy_p = rng_desp.uniform(-95.0, -25.0)
                petalos_caidos.append([p[0], p[1], 0.0, vx_p, vy_p, 0.0, p[2], p[3], 0.0])
        else:
          input_activo = False
    elif evento.type == pygame.MOUSEWHEEL:
      if modo_3d:
        distancia_camara = max(180.0, min(1800.0, distancia_camara - evento.y * 35.0))
      else:
        zoom_2d = max(0.4, min(3.0, zoom_2d + evento.y * 0.08))
    elif evento.type == pygame.MOUSEMOTION:
      en_ui = (input_rect.collidepoint(evento.pos) or boton_rand_rect.collidepoint(evento.pos)
               or boton_tipo_rect.collidepoint(evento.pos) or boton_modo_rect.collidepoint(evento.pos)
               or boton_viento_rect.collidepoint(evento.pos))
      if not en_ui:
        if modo_3d:
          if evento.buttons[0]:
            rot_y += evento.rel[0] * 0.007
            rot_x += evento.rel[1] * 0.007
          if evento.buttons[2]:
            cx_3d += evento.rel[0]
            cy_3d += evento.rel[1]
        else:
          if evento.buttons[0] or evento.buttons[2]:
            pan_x_2d += evento.rel[0]
            pan_y_2d += evento.rel[1]
    elif evento.type == pygame.KEYDOWN:
      if input_activo:
        if evento.key == pygame.K_RETURN:
          if texto_seed.strip():
            semilla_actual = int(texto_seed)
            tipo_actual_3d, puntos_3d, c0_3d, c1_3d, c2_3d, c3_3d = generar_lirio_3d(semilla_actual, tipo_forzado)
            tipo_actual_2d, puntos_2d, c0_2d, c1_2d, c2_2d, c3_2d = generar_jardin_lirios_2d(semilla_actual, tipo_forzado)
            petalos_caidos.clear()
            tiempo_entrada = 0.0
          input_activo = False
        elif evento.key == pygame.K_BACKSPACE:
          texto_seed = texto_seed[:-1]
        elif evento.key == pygame.K_ESCAPE:
          texto_seed = str(semilla_actual)
          input_activo = False
        elif evento.unicode.isdigit():
          if len(texto_seed) < 10:
            texto_seed += evento.unicode
      else:
        if evento.unicode.isdigit():
          input_activo = True
          texto_seed = evento.unicode
        elif evento.key in [pygame.K_m, pygame.K_3]:
          modo_3d = not modo_3d
          tiempo_entrada = 0.0
        elif evento.key == pygame.K_c:
          viento_rafaga = 3.5
          rng_desp = np.random.default_rng()
          if modo_3d:
            for p in puntos_3d:
              if p[6] > 0.75 and rng_desp.random() < 0.16:
                vx_p = rng_desp.uniform(-110.0, 110.0)
                vy_p = rng_desp.uniform(-130.0, -30.0)
                vz_p = rng_desp.uniform(-110.0, 110.0)
                petalos_caidos.append([p[0], p[1], p[2], vx_p, vy_p, vz_p, p[3], p[4], 0.0])
          else:
            for p in puntos_2d:
              if p[5] > 0.75 and rng_desp.random() < 0.15:
                vx_p = rng_desp.uniform(50.0, 200.0)
                vy_p = rng_desp.uniform(-95.0, -25.0)
                petalos_caidos.append([p[0], p[1], 0.0, vx_p, vy_p, 0.0, p[2], p[3], 0.0])
        elif evento.key == pygame.K_n:
          semilla_actual = int(np.random.default_rng().integers(1, 10000000))
          texto_seed = str(semilla_actual)
          tipo_actual_3d, puntos_3d, c0_3d, c1_3d, c2_3d, c3_3d = generar_lirio_3d(semilla_actual, tipo_forzado)
          tipo_actual_2d, puntos_2d, c0_2d, c1_2d, c2_2d, c3_2d = generar_jardin_lirios_2d(semilla_actual, tipo_forzado)
          petalos_caidos.clear()
          tiempo_entrada = 0.0
        elif evento.key == pygame.K_t:
          tipo_actual_ref = tipo_actual_3d if modo_3d else tipo_actual_2d
          tipo_forzado = (tipo_actual_ref + 1) % 5
          tipo_actual_3d, puntos_3d, c0_3d, c1_3d, c2_3d, c3_3d = generar_lirio_3d(semilla_actual, tipo_forzado)
          tipo_actual_2d, puntos_2d, c0_2d, c1_2d, c2_2d, c3_2d = generar_jardin_lirios_2d(semilla_actual, tipo_forzado)
          petalos_caidos.clear()
          tiempo_entrada = 0.0
        elif evento.key == pygame.K_i:
          tiempo_entrada = 0.0
        elif evento.key == pygame.K_SPACE:
          pausado = not pausado
        elif evento.key == pygame.K_r:
          rot_x = 0.42
          rot_y = 0.0
          distancia_camara = 620.0
          cx_3d = ancho // 2
          cy_3d = alto // 2 + 50
          zoom_2d = 1.0
          pan_x_2d = 0.0
          pan_y_2d = 0.0

  pantalla.fill((5, 3, 10))

  mouse_pos = pygame.mouse.get_pos()

  if not pausado:
    for pet in petalos_caidos:
      if modo_3d:
        pet[0] += pet[3] * dt
        pet[1] += pet[4] * dt
        pet[2] += pet[5] * dt
        pet[4] += 120.0 * dt
        pet[3] *= 0.985
        pet[5] *= 0.985
        if pet[1] >= 360.0:
          pet[1] = 360.0
          pet[4] = -abs(pet[4]) * 0.25
          pet[8] = min(3.0, pet[8] + 1.2)
          pet[3] *= 0.65
          pet[5] *= 0.65
      else:
        mouse_wind = (mouse_pos[0] - ancho // 2) * 0.035
        viento_base = math.sin(tiempo_total * 1.8) * 16.0 + viento_rafaga * 40.0 + mouse_wind
        pet[0] += (pet[3] + viento_base * 0.6) * dt
        pet[1] += pet[4] * dt
        pet[4] += 85.0 * dt
        pet[3] *= 0.985
        if pet[1] >= 810.0:
          pet[1] = 810.0
          pet[4] = -abs(pet[4]) * 0.28
          pet[8] = min(3.0, pet[8] + 1.2)
          pet[3] *= 0.65

  if modo_3d:
    cos_ry, sin_ry = math.cos(rot_y), math.sin(rot_y)
    cos_rx, sin_rx = math.cos(rot_x), math.sin(rot_x)

    pts_visibles = []
    for p in puntos_3d:
      t_ign = p[5]
      if tiempo_entrada < t_ign:
        continue
      prog_brot = min(1.0, (tiempo_entrada - t_ign) / 0.45)
      escala_brot = 0.2 + 0.8 * prog_brot
      x = p[0] * escala_brot
      y = p[1] * escala_brot
      z = p[2] * escala_brot

      x1 = x * cos_ry + z * sin_ry
      z1 = -x * sin_ry + z * cos_ry
      rx = x1
      ry = y * cos_rx - z1 * sin_rx
      rz = y * sin_rx + z1 * cos_rx

      prof = rz + distancia_camara
      if prof > 10.0:
        escala = fov / prof
        px = int(cx_3d + rx * escala)
        py = int(cy_3d + ry * escala)
        if 0 <= px < ancho and 0 <= py < alto:
          factor_luz = np.clip(1.0 - (rz / 380.0), 0.45, 1.35)
          col_p = p[4]
          if prog_brot < 1.0:
            flash = 1.0 + math.sin(prog_brot * math.pi) * 1.25
            col_render = np.clip(col_p * factor_luz * flash, 0, 255)
          else:
            col_render = np.clip(col_p * factor_luz, 0, 255)
          pts_visibles.append((rz, px, py, p[3], col_render))

    for pet in petalos_caidos:
      x = pet[0]
      y = pet[1]
      z = pet[2]
      x1 = x * cos_ry + z * sin_ry
      z1 = -x * sin_ry + z * cos_ry
      rx = x1
      ry = y * cos_rx - z1 * sin_rx
      rz = y * sin_rx + z1 * cos_rx
      prof = rz + distancia_camara
      if prof > 10.0:
        escala = fov / prof
        px = int(cx_3d + rx * escala)
        py = int(cy_3d + ry * escala)
        if 0 <= px < ancho and 0 <= py < alto:
          ch_p = pet[6]
          if pet[8] > 0.8:
            ch_p = "_" if pet[8] > 1.8 else "~"
          factor_luz = np.clip(1.0 - (rz / 380.0), 0.45, 1.35)
          col_p = np.clip(pet[7] * factor_luz, 0, 255)
          pts_visibles.append((rz, px, py, ch_p, col_p))

    pts_visibles.sort(key=lambda item: item[0], reverse=True)
    for _, px, py, ch, col in pts_visibles:
      pantalla.blit(render_char(ch, col), (px, py))

  else:
    mouse_wind = (mouse_pos[0] - ancho // 2) * 0.035
    viento_base = math.sin(tiempo_total * 1.8) * 16.0 + viento_rafaga * 40.0 + mouse_wind

    for pet in petalos_caidos:
      scr_x = int((pet[0] + ancho // 2 + pan_x_2d - ancho // 2) * zoom_2d + ancho // 2)
      scr_y = int((pet[1] + pan_y_2d - alto // 2) * zoom_2d + alto // 2)
      if 0 <= scr_x < ancho and 0 <= scr_y < alto:
        ch_pet = pet[6]
        if pet[8] > 0.8:
          ch_pet = "_" if pet[8] > 1.8 else "~"
        pantalla.blit(render_char(ch_pet, pet[7]), (scr_x, scr_y))

    for px, py, ch, col, t_ign, frac_h, f_id in puntos_2d:
      if tiempo_entrada < t_ign:
        continue

      prog_brot = min(1.0, (tiempo_entrada - t_ign) / 0.45)
      desv_viento = (frac_h ** 1.8) * viento_base
      rx = px + desv_viento
      ry = py - (1.0 - prog_brot) * 15.0

      scr_x = int((rx + pan_x_2d) * zoom_2d + (ancho // 2) * (1.0 - zoom_2d) + ancho // 2)
      scr_y = int((ry + pan_y_2d) * zoom_2d + (alto // 2) * (1.0 - zoom_2d))

      if 0 <= scr_x < ancho and 0 <= scr_y < alto:
        if prog_brot < 1.0:
          flash_c = np.clip(col * (1.0 + math.sin(prog_brot * math.pi) * 1.25), 0, 255)
          surf_ch = render_char(ch, flash_c)
        else:
          surf_ch = render_char(ch, col)
        pantalla.blit(surf_ch, (scr_x, scr_y))

  panel_fondo = pygame.Surface((815, 80), pygame.SRCALPHA)
  panel_fondo.fill((14, 10, 24, 215))
  pantalla.blit(panel_fondo, (12, 10))

  borde_color = (255, 140, 60) if input_activo else (75, 55, 95)
  pygame.draw.rect(pantalla, (26, 18, 38), input_rect, border_radius=6)
  pygame.draw.rect(pantalla, borde_color, input_rect, 2, border_radius=6)

  cursor = "|" if input_activo and (int(tiempo_total * 2) % 2 == 0) else ""
  texto_mostrar = f"Seed: {texto_seed}{cursor}"
  sup_texto = fuente_ui.render(texto_mostrar, True, (255, 230, 210))
  pantalla.blit(sup_texto, (input_rect.x + 10, input_rect.y + 8))

  pygame.draw.rect(pantalla, (45, 25, 60), boton_rand_rect, border_radius=6)
  pygame.draw.rect(pantalla, (180, 70, 160), boton_rand_rect, 1, border_radius=6)
  txt_rand = fuente_peq.render("Aleatorio (N)", True, (255, 220, 245))
  pantalla.blit(txt_rand, (boton_rand_rect.x + 10, boton_rand_rect.y + 10))

  tipo_ref = tipo_actual_3d if modo_3d else tipo_actual_2d
  pygame.draw.rect(pantalla, (55, 28, 48), boton_tipo_rect, border_radius=6)
  pygame.draw.rect(pantalla, (230, 90, 120), boton_tipo_rect, 1, border_radius=6)
  txt_tipo = fuente_peq.render(f"Tipo (T): {NOMBRES_TIPOS[tipo_ref]}", True, (255, 215, 230))
  pantalla.blit(txt_tipo, (boton_tipo_rect.x + 10, boton_tipo_rect.y + 10))

  color_btn_modo = (70, 35, 100) if modo_3d else (35, 50, 75)
  borde_btn_modo = (200, 100, 255) if modo_3d else (100, 150, 210)
  pygame.draw.rect(pantalla, color_btn_modo, boton_modo_rect, border_radius=6)
  pygame.draw.rect(pantalla, borde_btn_modo, boton_modo_rect, 1, border_radius=6)
  txt_modo = fuente_peq.render("Modo (M): 3D Única" if modo_3d else "Modo (M): 2D Campo", True, (245, 225, 255))
  pantalla.blit(txt_modo, (boton_modo_rect.x + 10, boton_modo_rect.y + 10))

  pygame.draw.rect(pantalla, (65, 30, 25), boton_viento_rect, border_radius=6)
  pygame.draw.rect(pantalla, (255, 120, 50), boton_viento_rect, 1, border_radius=6)
  txt_choque = fuente_peq.render("Viento (C)", True, (255, 220, 190))
  pantalla.blit(txt_choque, (boton_viento_rect.x + 16, boton_viento_rect.y + 10))

  if modo_3d:
    info_txt = fuente_mini.render("Modo 3D: C: Desprender Pétalos 3D | Drag Izq: Rotar 360° | Rueda: Zoom | Drag Der: Pan | M: Modo", True, (210, 170, 220))
  else:
    info_txt = fuente_mini.render("Modo 2D: C: Viento/Colisión | Rueda: Zoom | Drag: Pan | I: Florecer | M: Modo 2D/3D | T: Lirio", True, (200, 160, 205))
  pantalla.blit(info_txt, (18, 62))

  pygame.display.flip()

pygame.quit()
