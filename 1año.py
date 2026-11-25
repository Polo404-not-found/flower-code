import math
import sys
import numpy as np
import pygame

pygame.init()
ancho, alto = 1200, 900
pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Galaxia 3D - Simulador Cósmico Multigaláctico")
reloj = pygame.time.Clock()
fuente = pygame.font.Font(None, 24)
fuente_peq = pygame.font.Font(None, 20)
fuente_mini = pygame.font.Font(None, 18)

num_estrellas_bg = 500
rng_bg = np.random.default_rng(999)
bg_x = rng_bg.integers(0, ancho, size=num_estrellas_bg)
bg_y = rng_bg.integers(0, alto, size=num_estrellas_bg)
bg_brillo = rng_bg.integers(40, 150, size=num_estrellas_bg)

NOMBRES_TIPOS = [
    "Espiral Asimétrica",
    "Aros Concéntricos",
    "Quásar con Jets",
    "Colisión Binaria",
    "Vórtice Alabeado 3D",
]


def mapear_paleta(t, c0, c1, c2, c3):
  t_norm = np.clip(t, 0.0, 1.0)
  colores = np.empty((len(t_norm), 3), dtype=np.float32)

  m1 = t_norm < 0.33
  m2 = (t_norm >= 0.33) & (t_norm < 0.66)
  m3 = t_norm >= 0.66

  f1 = (t_norm[m1] / 0.33)[:, None]
  colores[m1] = c0 * (1.0 - f1) + c1 * f1

  f2 = ((t_norm[m2] - 0.33) / 0.33)[:, None]
  colores[m2] = c1 * (1.0 - f2) + c2 * f2

  f3 = ((t_norm[m3] - 0.66) / 0.34)[:, None]
  colores[m3] = c2 * (1.0 - f3) + c3 * f3

  return colores


def crear_galaxia_numpy(semilla=21, num_estrellas=12000, radio_max=320, tipo_forzado=None):
  rng = np.random.default_rng(semilla)
  tipo = (tipo_forzado % 5) if tipo_forzado is not None else int(rng.integers(0, 5))
  fases = rng.uniform(0.0, 2 * np.pi, size=num_estrellas)
  es_jet = np.zeros(num_estrellas, dtype=bool)
  es_warp = np.zeros(num_estrellas, dtype=bool)
  es_b = np.zeros(num_estrellas, dtype=bool)
  vel_jet = np.zeros(num_estrellas, dtype=np.float32)

  c0 = np.array([255.0, rng.uniform(85.0, 160.0), rng.uniform(0.0, 35.0)])
  c1 = np.array([255.0, rng.uniform(25.0, 75.0), rng.uniform(90.0, 145.0)])
  c2 = np.array([rng.uniform(170.0, 220.0), rng.uniform(20.0, 50.0), 255.0])
  c3 = np.array([rng.uniform(80.0, 135.0), rng.uniform(10.0, 35.0), 255.0])

  n_core = int(rng.integers(2200, 3200))
  n_disco = num_estrellas - n_core

  spread_r = rng.uniform(11.0, 22.0)
  spread_y = rng.uniform(5.5, 13.0)

  if tipo == 3:
    mitad_core = n_core // 2
    offset = rng.uniform(0.35, 0.52) * radio_max
    x_ca = rng.normal(-offset, spread_r * 0.85, size=mitad_core)
    z_ca = rng.normal(0.0, spread_r * 0.85, size=mitad_core)
    y_ca = rng.normal(0.0, spread_y * 0.85, size=mitad_core)
    vel_ca = np.full(mitad_core, 0.012 * rng.uniform(0.8, 1.3))
    t_ca = rng.uniform(0.0, 0.25, size=mitad_core)
    col_ca = mapear_paleta(t_ca, c0, c1, c2, c3)

    x_cb = rng.normal(offset, spread_r * 0.85, size=n_core - mitad_core)
    z_cb = rng.normal(0.0, spread_r * 0.85, size=n_core - mitad_core)
    y_cb = rng.normal(0.0, spread_y * 0.85, size=n_core - mitad_core)
    vel_cb = np.full(n_core - mitad_core, -0.012 * rng.uniform(0.8, 1.3))
    t_cb = rng.uniform(0.68, 1.0, size=n_core - mitad_core)
    col_cb = mapear_paleta(t_cb, c0, c1, c2, c3)

    x_c = np.concatenate([x_ca, x_cb])
    y_c = np.concatenate([y_ca, y_cb])
    z_c = np.concatenate([z_ca, z_cb])
    vel_c = np.concatenate([vel_ca, vel_cb])
    col_c = np.concatenate([col_ca, col_cb])
    r_c = np.sqrt(x_c**2 + z_c**2)
    es_b[:n_core] = np.concatenate([np.zeros(mitad_core, dtype=bool), np.ones(n_core - mitad_core, dtype=bool)])
  else:
    x_c = rng.normal(0.0, spread_r, size=n_core)
    z_c = rng.normal(0.0, spread_r, size=n_core)
    y_c = rng.normal(0.0, spread_y, size=n_core)
    r_c = np.sqrt(x_c**2 + z_c**2)
    vel_c = np.full(n_core, 0.012 * rng.uniform(0.85, 1.25))
    t_c = rng.uniform(0.0, 0.28, size=n_core)
    col_c = mapear_paleta(t_c, c0, c1, c2, c3)
    col_c[r_c < spread_r * 0.5] = [255.0, 195.0, 60.0]

  idx_d = np.arange(n_disco)

  if tipo == 0:
    frac_barra = rng.uniform(0.2, 0.45)
    n_barra = int(n_disco * frac_barra)
    n_brazos = n_disco - n_barra
    bar_len = rng.uniform(0.25, 0.55) * radio_max
    ang_bar = rng.uniform(0.0, np.pi)
    x_b0 = rng.uniform(-1.0, 1.0, size=n_barra) * bar_len
    z_b0 = rng.normal(0.0, rng.uniform(6.0, 15.0), size=n_barra)
    x_b = x_b0 * np.cos(ang_bar) - z_b0 * np.sin(ang_bar)
    z_b = x_b0 * np.sin(ang_bar) + z_b0 * np.cos(ang_bar)
    y_b = rng.normal(0.0, rng.uniform(3.0, 8.0), size=n_barra)
    r_b = np.sqrt(x_b**2 + z_b**2)
    t_b = (r_b / (bar_len + 1.0)) * 0.38
    col_b = mapear_paleta(t_b, c0, c1, c2, c3)
    vel_b = np.full(n_barra, 0.012 * rng.uniform(0.85, 1.2))

    brazos = int(rng.integers(1, 9))
    twist = rng.uniform(0.012, 0.042)
    idx_br = np.arange(n_brazos)
    b_id = idx_br % brazos
    potencia_r = rng.uniform(0.6, 0.82)
    r_br = (rng.random(n_brazos) ** potencia_r) * (radio_max - bar_len * 0.7) + bar_len * 0.7
    disp_ang = rng.normal(0.0, rng.uniform(0.15, 0.35), size=n_brazos)
    ang_br = b_id * (2 * np.pi / brazos) + r_br * twist + disp_ang
    x_br = r_br * np.cos(ang_br)
    z_br = r_br * np.sin(ang_br)
    grosor_max = rng.uniform(22.0, 48.0)
    y_br = rng.normal(0.0, 1.0, size=n_brazos) * (grosor_max * np.exp(-r_br / 95.0) + 4.5)
    vel_br = (0.012 * rng.uniform(0.8, 1.25)) / (1.0 + (r_br - 25.0) * 0.008)
    t_br = 0.25 + (r_br / radio_max) * 0.75 + (b_id / max(1, brazos)) * rng.uniform(-0.15, 0.15)
    col_br = mapear_paleta(t_br, c0, c1, c2, c3)

    x_d = np.concatenate([x_b, x_br])
    y_d = np.concatenate([y_b, y_br])
    z_d = np.concatenate([z_b, z_br])
    vel_d = np.concatenate([vel_b, vel_br])
    col_d = np.concatenate([col_b, col_br])
    r_d = np.concatenate([r_b, r_br])

  elif tipo == 1:
    n_aros = int(rng.integers(2, 7))
    aro_id = idx_d % n_aros
    radios_aro = np.sort(rng.uniform(radio_max * 0.18, radio_max * 0.98, size=n_aros))
    anchos_aro = rng.uniform(8.0, 24.0, size=n_aros)
    sentidos = rng.choice([1.0, -1.0], size=n_aros) * rng.uniform(0.75, 1.4, size=n_aros)
    r_d = radios_aro[aro_id] + rng.normal(0.0, anchos_aro[aro_id], size=n_disco)
    ang_d = rng.uniform(0.0, 2 * np.pi, size=n_disco)
    x_d = r_d * np.cos(ang_d)
    z_d = r_d * np.sin(ang_d)
    y_d = rng.normal(0.0, rng.uniform(2.5, 6.0), size=n_disco)
    vel_d = sentidos[aro_id] * (0.014 / (1.0 + r_d * 0.006))
    t_aros = aro_id / float(max(1, n_aros - 1))
    col_d = mapear_paleta(t_aros, c0, c1, c2, c3)

  elif tipo == 2:
    frac_jets = rng.uniform(0.18, 0.35)
    n_jets = int(n_disco * frac_jets)
    n_disco_q = n_disco - n_jets
    r_min_d = rng.uniform(12.0, 30.0)
    r_max_d = rng.uniform(0.65, 0.88) * radio_max
    r_dq = (rng.random(n_disco_q) ** rng.uniform(0.45, 0.62)) * (r_max_d - r_min_d) + r_min_d
    ang_dq = rng.uniform(0.0, 2 * np.pi, size=n_disco_q)
    x_dq = r_dq * np.cos(ang_dq)
    z_dq = r_dq * np.sin(ang_dq)
    y_dq = rng.normal(0.0, rng.uniform(1.8, 4.0), size=n_disco_q)
    vel_dq = rng.uniform(0.018, 0.035) / (np.sqrt(r_dq) * 0.16 + 0.5)
    t_dq = (r_dq / r_max_d) * 0.55
    col_dq = mapear_paleta(t_dq, c0, c1, c2, c3)

    dir_jet = np.where(rng.random(n_jets) > 0.5, 1.0, -1.0)
    alt_max_j = rng.uniform(1.1, 1.6) * radio_max
    y_j = dir_jet * rng.uniform(6.0, alt_max_j, size=n_jets)
    ang_j = rng.uniform(0.0, 2 * np.pi, size=n_jets)
    r_cone = rng.uniform(2.5, 5.0) + (np.abs(y_j) / alt_max_j) * rng.uniform(12.0, 26.0)
    rad_j = rng.normal(0.0, r_cone, size=n_jets)
    x_j = rad_j * np.cos(ang_j)
    z_j = rad_j * np.sin(ang_j)
    vel_j = np.full(n_jets, 0.003)
    v_jet_vals = dir_jet * rng.uniform(160.0, 380.0, size=n_jets)
    t_j = 0.65 + (np.abs(y_j) / alt_max_j) * 0.35
    col_j = mapear_paleta(t_j, c0, c1, c2, c3)

    x_d = np.concatenate([x_dq, x_j])
    y_d = np.concatenate([y_dq, y_j])
    z_d = np.concatenate([z_dq, z_j])
    vel_d = np.concatenate([vel_dq, vel_j])
    col_d = np.concatenate([col_dq, col_j])
    r_d = np.sqrt(x_d**2 + z_d**2)
    es_jet[n_core + n_disco_q:] = True
    vel_jet[n_core + n_disco_q:] = v_jet_vals

  elif tipo == 3:
    frac_a = rng.uniform(0.35, 0.65)
    mitad = int(n_disco * frac_a)
    offset = rng.uniform(0.35, 0.52) * radio_max
    r_max_a = rng.uniform(0.45, 0.68) * radio_max
    r_a = (rng.random(mitad) ** rng.uniform(0.55, 0.72)) * r_max_a
    brazos_a = int(rng.integers(1, 5))
    ang_a = (idx_d[:mitad] % brazos_a) * (2 * np.pi / brazos_a) + r_a * rng.uniform(0.015, 0.035) + rng.normal(0.0, 0.22, size=mitad)
    x_a = r_a * np.cos(ang_a) - offset
    z_a = r_a * np.sin(ang_a)
    y_a = rng.normal(0.0, rng.uniform(3.5, 7.0), size=mitad)
    vel_a = (0.013 * rng.uniform(0.8, 1.2)) / (1.0 + r_a * 0.012)
    t_a = (r_a / r_max_a) * 0.48
    col_a = mapear_paleta(t_a, c0, c1, c2, c3)

    r_max_b = rng.uniform(0.45, 0.68) * radio_max
    r_b = (rng.random(n_disco - mitad) ** rng.uniform(0.55, 0.72)) * r_max_b
    brazos_b = int(rng.integers(1, 5))
    ang_b = (idx_d[mitad:] % brazos_b) * (2 * np.pi / brazos_b) + r_b * rng.uniform(0.015, 0.035) + rng.normal(0.0, 0.22, size=n_disco - mitad)
    x_b0 = r_b * np.cos(ang_b)
    z_b0 = r_b * np.sin(ang_b)
    y_b0 = rng.normal(0.0, rng.uniform(3.5, 7.0), size=n_disco - mitad)
    inc_b = rng.uniform(0.3, 1.4)
    x_b = x_b0 + offset
    y_b = y_b0 * np.cos(inc_b) - z_b0 * np.sin(inc_b)
    z_b = y_b0 * np.sin(inc_b) + z_b0 * np.cos(inc_b)
    vel_b = -(0.013 * rng.uniform(0.8, 1.2)) / (1.0 + r_b * 0.012)
    t_b = 0.52 + (r_b / r_max_b) * 0.48
    col_b = mapear_paleta(t_b, c0, c1, c2, c3)

    x_d = np.concatenate([x_a, x_b])
    y_d = np.concatenate([y_a, y_b])
    z_d = np.concatenate([z_a, z_b])
    vel_d = np.concatenate([vel_a, vel_b])
    col_d = np.concatenate([col_a, col_b])
    r_d = np.sqrt(x_d**2 + z_d**2)
    es_b[n_core:] = np.concatenate([np.zeros(mitad, dtype=bool), np.ones(n_disco - mitad, dtype=bool)])

  else:
    brazos = int(rng.integers(3, 9))
    twist = rng.uniform(0.015, 0.045)
    r_d = (rng.random(n_disco) ** rng.uniform(0.55, 0.75)) * (radio_max - 20.0) + 20.0
    b_id = idx_d % brazos
    ang_d = b_id * (2 * np.pi / brazos) + r_d * twist + rng.normal(0.0, rng.uniform(0.14, 0.3), size=n_disco)
    x_d = r_d * np.cos(ang_d)
    z_d = r_d * np.sin(ang_d)
    y_d = rng.normal(0.0, rng.uniform(3.5, 7.5), size=n_disco)
    vel_d = (0.012 * rng.uniform(0.85, 1.25)) / (1.0 + (r_d - 20.0) * 0.008)
    t_w = (r_d / radio_max)
    col_d = mapear_paleta(t_w, c0, c1, c2, c3)
    es_warp[n_core:] = True

  x = np.concatenate([x_c, x_d])
  y = np.concatenate([y_c, y_d])
  z = np.concatenate([z_c, z_d])
  vel_orbita = np.concatenate([vel_c, vel_d])
  colores = np.concatenate([col_c, col_d])
  r = np.concatenate([r_c, r_d])

  t_ignicion = (r / radio_max) * rng.uniform(1.8, 2.5) + rng.uniform(0.0, 0.6, size=num_estrellas)

  return tipo, x, y, z, vel_orbita, colores, r, fases, es_jet, vel_jet, es_warp, es_b, t_ignicion


semilla_actual = 21
if len(sys.argv) > 1 and sys.argv[1].isdigit():
  semilla_actual = int(sys.argv[1])

tipo_forzado = None
num_estrellas_actual = 12000
radio_max_actual = 320

tipo_actual, x, y, z, vel_orbita, colores_base, r_estrellas, fases_estrellas, es_jet, vel_jet, es_warp, es_b, t_ignicion = (
    crear_galaxia_numpy(
        semilla_actual,
        num_estrellas_actual,
        radio_max_actual,
        tipo_forzado,
    )
)

deformacion = np.zeros(num_estrellas_actual, dtype=np.float32)

rot_x = 0.45
rot_y = 0.0
distancia_camara = 600.0
fov = 760.0
cx, cy = ancho // 2, alto // 2
velocidad_tiempo = 1.0
pausado = False
tiempo_total = 0.0
tiempo_entrada = 0.0

onda_radio = -1.0
impacto_activo = False
t_impacto = 0.0

texto_seed = str(semilla_actual)
input_activo = False
input_rect = pygame.Rect(20, 16, 190, 36)
boton_rand_rect = pygame.Rect(220, 16, 110, 36)
boton_tipo_rect = pygame.Rect(340, 16, 210, 36)
boton_choque_rect = pygame.Rect(560, 16, 110, 36)

corriendo = True
while corriendo:
  dt = reloj.tick(60) / 1000.0
  tiempo_total += dt
  tiempo_entrada += dt

  deformacion = np.maximum(0.0, deformacion - dt * 2.2)

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
          tipo_actual, x, y, z, vel_orbita, colores_base, r_estrellas, fases_estrellas, es_jet, vel_jet, es_warp, es_b, t_ignicion = (
              crear_galaxia_numpy(
                  semilla_actual,
                  num_estrellas_actual,
                  radio_max_actual,
                  tipo_forzado,
              )
          )
          deformacion.fill(0.0)
          onda_radio = 0.0
          tiempo_entrada = 0.0
          input_activo = False
        elif boton_tipo_rect.collidepoint(evento.pos):
          tipo_forzado = (tipo_actual + 1) % 5
          tipo_actual, x, y, z, vel_orbita, colores_base, r_estrellas, fases_estrellas, es_jet, vel_jet, es_warp, es_b, t_ignicion = (
              crear_galaxia_numpy(
                  semilla_actual,
                  num_estrellas_actual,
                  radio_max_actual,
                  tipo_forzado,
              )
          )
          deformacion.fill(0.0)
          onda_radio = 0.0
          tiempo_entrada = 0.0
          input_activo = False
        elif boton_choque_rect.collidepoint(evento.pos):
          impacto_activo = True
          t_impacto = 0.0
        else:
          input_activo = False
    elif evento.type == pygame.MOUSEWHEEL:
      distancia_camara = max(80.0, min(2400.0, distancia_camara - evento.y * 35.0))
    elif evento.type == pygame.MOUSEMOTION:
      en_ui = input_rect.collidepoint(evento.pos) or boton_rand_rect.collidepoint(evento.pos) or boton_tipo_rect.collidepoint(evento.pos) or boton_choque_rect.collidepoint(evento.pos)
      if not en_ui:
        if evento.buttons[0]:
          rot_y += evento.rel[0] * 0.007
          rot_x += evento.rel[1] * 0.007
        if evento.buttons[2]:
          cx += evento.rel[0]
          cy += evento.rel[1]
    elif evento.type == pygame.KEYDOWN:
      if input_activo:
        if evento.key == pygame.K_RETURN:
          if texto_seed.strip():
            semilla_actual = int(texto_seed)
            tipo_actual, x, y, z, vel_orbita, colores_base, r_estrellas, fases_estrellas, es_jet, vel_jet, es_warp, es_b, t_ignicion = (
                crear_galaxia_numpy(
                    semilla_actual,
                    num_estrellas_actual,
                    radio_max_actual,
                    tipo_forzado,
                )
            )
            deformacion.fill(0.0)
            onda_radio = 0.0
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
        elif evento.key == pygame.K_c:
          impacto_activo = True
          t_impacto = 0.0
        elif evento.key == pygame.K_n:
          semilla_actual = int(np.random.default_rng().integers(1, 10000000))
          texto_seed = str(semilla_actual)
          tipo_actual, x, y, z, vel_orbita, colores_base, r_estrellas, fases_estrellas, es_jet, vel_jet, es_warp, es_b, t_ignicion = (
              crear_galaxia_numpy(
                  semilla_actual,
                  num_estrellas_actual,
                  radio_max_actual,
                  tipo_forzado,
              )
          )
          deformacion.fill(0.0)
          onda_radio = 0.0
          tiempo_entrada = 0.0
        elif evento.key == pygame.K_t:
          tipo_forzado = (tipo_actual + 1) % 5
          tipo_actual, x, y, z, vel_orbita, colores_base, r_estrellas, fases_estrellas, es_jet, vel_jet, es_warp, es_b, t_ignicion = (
              crear_galaxia_numpy(
                  semilla_actual,
                  num_estrellas_actual,
                  radio_max_actual,
                  tipo_forzado,
              )
          )
          deformacion.fill(0.0)
          onda_radio = 0.0
          tiempo_entrada = 0.0
        elif evento.key == pygame.K_i:
          tiempo_entrada = 0.0
        elif evento.key == pygame.K_SPACE:
          pausado = not pausado
        elif evento.key == pygame.K_UP:
          velocidad_tiempo = min(5.0, velocidad_tiempo + 0.25)
        elif evento.key == pygame.K_DOWN:
          velocidad_tiempo = max(-5.0, velocidad_tiempo - 0.25)
        elif evento.key == pygame.K_r:
          rot_x = 0.45
          rot_y = 0.0
          distancia_camara = 600.0
          cx, cy = ancho // 2, alto // 2
          velocidad_tiempo = 1.0
        elif evento.key == pygame.K_e:
          onda_radio = 0.0

  pantalla.fill((2, 2, 6))

  for bx, by, bb in zip(bg_x, bg_y, bg_brillo):
    pantalla.set_at((bx, by), (bb, int(bb * 0.65), min(255, int(bb * 1.35))))

  if not pausado:
    ang = vel_orbita * (dt * 60.0 * velocidad_tiempo)
    cos_a = np.cos(ang)
    sin_a = np.sin(ang)
    x_nuevo = x * cos_a + z * sin_a
    z_nuevo = -x * sin_a + z * cos_a
    x, z = x_nuevo, z_nuevo

    if np.any(es_jet):
      y[es_jet] += vel_jet[es_jet] * (dt * velocidad_tiempo)
      fuera = np.abs(y[es_jet]) > (radio_max_actual * 1.35)
      if np.any(fuera):
        idx_f = np.where(es_jet)[0][fuera]
        y[idx_f] = np.sign(vel_jet[idx_f]) * (4.0 + np.random.default_rng().uniform(0.0, 4.0, size=len(idx_f)))

    if tipo_actual == 3:
      ang_col = tiempo_total * 0.35 * velocidad_tiempo
      cen_bx = (radio_max_actual * 0.44) * math.cos(ang_col)
      cen_bz = (radio_max_actual * 0.44) * math.sin(ang_col)
      cen_ax = -cen_bx
      cen_az = -cen_bz

      dist_to_opp = np.where(
          es_b,
          np.sqrt((x - cen_ax)**2 + y**2 + (z - cen_az)**2 + 100.0),
          np.sqrt((x - cen_bx)**2 + y**2 + (z - cen_bz)**2 + 100.0),
      )
      cercania_choque = np.clip(1.0 - dist_to_opp / (radio_max_actual * 0.48), 0.0, 1.0)
      deformacion = np.maximum(deformacion, cercania_choque * 2.8)

      fuerza_marea = (cercania_choque * 45.0 * dt * velocidad_tiempo)
      tironeo_x = np.where(es_b, (cen_ax - x) / dist_to_opp, (cen_bx - x) / dist_to_opp)
      tironeo_z = np.where(es_b, (cen_az - z) / dist_to_opp, (cen_bz - z) / dist_to_opp)
      x += tironeo_x * fuerza_marea
      z += tironeo_z * fuerza_marea

  if impacto_activo and not pausado:
    t_impacto += dt * 1.2 * velocidad_tiempo
    imp_x = (t_impacto * 600.0 - 300.0)
    imp_y = math.sin(t_impacto * 3.5) * 35.0
    imp_z = math.cos(t_impacto * 2.2) * 75.0

    vec_ix = x - imp_x
    vec_iy = y - imp_y
    vec_iz = z - imp_z
    dist_imp = np.sqrt(vec_ix**2 + vec_iy**2 + vec_iz**2 + 10.0)
    en_colision = dist_imp < 95.0

    if np.any(en_colision):
      intensidad_imp = (1.0 - dist_imp[en_colision] / 95.0)
      repulsion = intensidad_imp * (65.0 * dt * velocidad_tiempo)
      x[en_colision] += (vec_ix[en_colision] / dist_imp[en_colision]) * repulsion * 3.0
      y[en_colision] += (vec_iy[en_colision] / dist_imp[en_colision]) * repulsion * 1.5
      z[en_colision] += (vec_iz[en_colision] / dist_imp[en_colision]) * repulsion * 3.0
      deformacion[en_colision] = np.maximum(deformacion[en_colision], intensidad_imp * 3.5)

    if t_impacto > 1.2:
      impacto_activo = False

  y_render = y.copy()
  if np.any(es_warp) and not pausado:
    ang_p = np.arctan2(z, x)
    offset_warp = np.where(
        r_estrellas > 35.0,
        np.sin(r_estrellas * 0.03 - tiempo_total * 2.8)
        * ((r_estrellas - 35.0) * 0.16)
        * np.cos(ang_p - tiempo_total * 0.5),
        0.0,
    )
    y_render += offset_warp

  if onda_radio >= 0.0:
    onda_radio += dt * 360.0
    if onda_radio > radio_max_actual * 1.85:
      onda_radio = -1.0

  cos_ry, sin_ry = math.cos(rot_y), math.sin(rot_y)
  cos_rx, sin_rx = math.cos(rot_x), math.sin(rot_x)

  x1 = x * cos_ry + z * sin_ry
  z1 = -x * sin_ry + z * cos_ry
  y1 = y_render

  rx = x1
  ry = y1 * cos_rx - z1 * sin_rx
  rz = y1 * sin_rx + z1 * cos_rx

  vx_3d = -z * vel_orbita
  vz_3d = x * vel_orbita
  vy_3d = np.zeros_like(x)
  vx1 = vx_3d * cos_ry + vz_3d * sin_ry
  vz1 = -vx_3d * sin_ry + vz_3d * cos_ry
  vy1 = vy_3d
  rx_vdir = vx1
  ry_vdir = vy1 * cos_rx - vz1 * sin_rx

  profundidad = rz + distancia_camara
  visible = profundidad > 10.0

  prof_v = profundidad[visible]
  rx_v = rx[visible]
  ry_v = ry[visible]
  rz_v = rz[visible]
  col_v = colores_base[visible]
  r_v = r_estrellas[visible]
  fases_v = fases_estrellas[visible]
  t_ign_v = t_ignicion[visible]
  deform_v = deformacion[visible]
  rx_vd_v = rx_vdir[visible]
  ry_vd_v = ry_vdir[visible]

  escala = fov / prof_v
  px = (cx + rx_v * escala).astype(np.int32)
  py = (cy + ry_v * escala).astype(np.int32)

  orden = np.argsort(rz_v)[::-1]
  px = px[orden]
  py = py[orden]
  prof_ord = prof_v[orden]
  esc_ord = escala[orden]
  col_ord = col_v[orden].copy()
  r_ord = r_v[orden]
  fases_ord = fases_v[orden]
  t_ign_ord = t_ign_v[orden]
  deform_ord = deform_v[orden]
  rx_vd_ord = rx_vd_v[orden]
  ry_vd_ord = ry_vd_v[orden]

  dif_t = tiempo_entrada - t_ign_ord
  iluminada = dif_t > 0.0
  factor_entrada = np.ones_like(dif_t, dtype=np.float32)
  factor_entrada[~iluminada] = 0.0
  if np.any(iluminada):
    prog = np.clip(dif_t[iluminada] / 0.45, 0.0, 1.0)
    flash = np.where(prog < 1.0, prog * (1.0 + 1.25 * np.sin(prog * np.pi)), 1.0)
    factor_entrada[iluminada] = flash

  if onda_radio >= 0.0:
    dist_onda = np.abs(r_ord - onda_radio)
    cerca_onda = dist_onda < 26.0
    intensidad_onda = (1.0 - dist_onda[cerca_onda] / 26.0)[:, None]
    col_ord[cerca_onda] = np.clip(
        col_ord[cerca_onda] + np.array([255.0, 160.0, 220.0]) * intensidad_onda,
        0,
        255,
    )
    deform_ord[cerca_onda] = np.maximum(deform_ord[cerca_onda], 2.4)

  en_choque = deform_ord > 0.12
  if np.any(en_choque):
    col_ord[en_choque] = np.clip(
        col_ord[en_choque] + (deform_ord[en_choque, None] * np.array([120.0, 70.0, 110.0])),
        0,
        255,
    )

  twinkle = 0.84 + 0.26 * np.sin(tiempo_total * 4.0 + fases_ord)[:, None]
  factor_luz = np.clip((720.0 / prof_ord)[:, None] * twinkle, 0.45, 1.8)
  col_final = np.clip(col_ord * factor_luz * factor_entrada[:, None], 0, 255).astype(np.uint8)
  radios = np.clip((1.9 * esc_ord).astype(np.int32), 1, 4)

  mult_def = np.clip(deform_ord * 3.8, 0.0, 15.0)
  dx_s = (rx_vd_ord * esc_ord * mult_def).astype(np.int32)
  dy_s = (ry_vd_ord * esc_ord * mult_def).astype(np.int32)
  deformado = en_choque & ((dx_s**2 + dy_s**2) >= 4)

  dentro = (px >= 0) & (px < ancho) & (py >= 0) & (py < alto) & (factor_entrada > 0.02)
  for x_i, y_i, dx_i, dy_i, r_i, c_i, def_i in zip(
      px[dentro], py[dentro], dx_s[dentro], dy_s[dentro], radios[dentro], col_final[dentro], deformado[dentro]
  ):
    color_p = (int(c_i[0]), int(c_i[1]), int(c_i[2]))
    if def_i:
      pygame.draw.line(pantalla, color_p, (x_i - dx_i, y_i - dy_i), (x_i + dx_i, y_i + dy_i), max(1, int(r_i)))
    else:
      pygame.draw.circle(pantalla, color_p, (int(x_i), int(y_i)), int(r_i))

  panel_fondo = pygame.Surface((700, 80), pygame.SRCALPHA)
  panel_fondo.fill((14, 10, 24, 215))
  pantalla.blit(panel_fondo, (12, 10))

  borde_color = (255, 140, 60) if input_activo else (75, 55, 95)
  pygame.draw.rect(pantalla, (26, 18, 38), input_rect, border_radius=6)
  pygame.draw.rect(pantalla, borde_color, input_rect, 2, border_radius=6)

  cursor = "|" if input_activo and (int(tiempo_total * 2) % 2 == 0) else ""
  texto_mostrar = f"Seed: {texto_seed}{cursor}"
  sup_texto = fuente.render(texto_mostrar, True, (255, 230, 210))
  pantalla.blit(sup_texto, (input_rect.x + 10, input_rect.y + 8))

  pygame.draw.rect(pantalla, (45, 25, 60), boton_rand_rect, border_radius=6)
  pygame.draw.rect(pantalla, (180, 70, 160), boton_rand_rect, 1, border_radius=6)
  txt_rand = fuente_peq.render("Aleatorio (N)", True, (255, 220, 245))
  pantalla.blit(txt_rand, (boton_rand_rect.x + 12, boton_rand_rect.y + 10))

  pygame.draw.rect(pantalla, (55, 28, 48), boton_tipo_rect, border_radius=6)
  pygame.draw.rect(pantalla, (230, 90, 120), boton_tipo_rect, 1, border_radius=6)
  txt_tipo = fuente_peq.render(f"Tipo (T): {NOMBRES_TIPOS[tipo_actual]}", True, (255, 215, 230))
  pantalla.blit(txt_tipo, (boton_tipo_rect.x + 10, boton_tipo_rect.y + 10))

  pygame.draw.rect(pantalla, (65, 30, 25), boton_choque_rect, border_radius=6)
  pygame.draw.rect(pantalla, (255, 120, 50), boton_choque_rect, 1, border_radius=6)
  txt_choque = fuente_peq.render("Choque (C)", True, (255, 220, 190))
  pantalla.blit(txt_choque, (boton_choque_rect.x + 14, boton_choque_rect.y + 10))

  info_txt = fuente_mini.render("Enter: Aplicar | C: Choque/Impacto | T: Tipo | N: Seed | I: Entrada | Rueda: Zoom | Drag: Rotar | E: Onda", True, (200, 160, 205))
  pantalla.blit(info_txt, (18, 62))

  pygame.display.flip()

pygame.quit()
