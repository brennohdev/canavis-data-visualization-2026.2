"""Mede contraste WCAG 2.1 e separabilidade sob daltonismo da paleta do CanaVis.

Uso: python scripts/contraste_paleta.py
Sem dependências externas. As matrizes de simulação são as de Machado et al. (2009),
severidade 1,0, aplicadas em RGB linear.
"""
from __future__ import annotations

import math

FUNDO = "#F2F2F2"
BRANCO = "#FFFFFF"

TEXTO = [
    ("Texto principal", "#1A1A1A", FUNDO),
    ("Texto secundário", "#50565E", FUNDO),
    ("Verde-cana (texto)", "#2F6B3C", FUNDO),
    ("Âmbar escuro (texto)", "#8A4B00", FUNDO),
    ("Azul-ardósia escuro (texto)", "#2B5580", FUNDO),
    ("Cinza de dado (texto)", "#566170", FUNDO),
    ("Branco sobre verde-cana", BRANCO, "#2F6B3C"),
    ("Branco sobre azul-ardósia escuro", BRANCO, "#2B5580"),
    ("Texto principal sobre âmbar", "#1A1A1A", "#C26F00"),
]

FORMAS = [
    ("Verde-cana (marca, acima da ref.)", "#2F6B3C", FUNDO),
    ("Âmbar (abaixo da ref.)", "#C26F00", FUNDO),
    ("Verde médio (série secundária)", "#5E9170", FUNDO),
    ("Açúcar (azul-ardósia)", "#3A6EA5", FUNDO),
    ("Etanol (ocre)", "#A8641A", FUNDO),
    ("Cinza de dado (ausente, outras UFs)", "#6B7785", FUNDO),
    ("Eixo e contorno de forma", "#7C8691", FUNDO),
    ("Anel de foco", "#1D4ED8", FUNDO),
    ("Contorno de área da rampa", "#50565E", FUNDO),
    ("Rampa nível 6 (maior)", "#1F4D2B", FUNDO),
]

RAMPA = ["#E3EFE5", "#B5D3BB", "#7BA886", "#4A8057", "#2F6B3C", "#1F4D2B"]

PARES_DALTONISMO = [
    ("Acima x abaixo (verde-cana x âmbar)", "#2F6B3C", "#C26F00"),
    ("Açúcar x etanol (azul x ocre)", "#3A6EA5", "#A8641A"),
    ("Verde-cana x azul-ardósia", "#2F6B3C", "#3A6EA5"),
    ("Verde médio x cinza de dado", "#5E9170", "#6B7785"),
    ("Açúcar x etanol (descartado: azul x verde)", "#3A6EA5", "#5E9170"),
]

MACHADO = {
    "protanopia": [
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281, 0.099216),
        (-0.003882, -0.048116, 1.051998),
    ],
    "deuteranopia": [
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501, 0.047413),
        (-0.011820, 0.042940, 0.968881),
    ],
    "tritanopia": [
        (1.255528, -0.076749, -0.178779),
        (-0.078411, 0.930809, 0.147602),
        (0.004733, 0.691367, 0.303900),
    ],
}


def rgb(hex_: str) -> tuple[float, float, float]:
    h = hex_.lstrip("#")
    return tuple(int(h[i : i + 2], 16) / 255 for i in (0, 2, 4))


def linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def delinear(c: float) -> float:
    c = min(1.0, max(0.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def luminancia(hex_: str) -> float:
    r, g, b = (linear(c) for c in rgb(hex_))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a: str, b: str) -> float:
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def simular(hex_: str, tipo: str) -> tuple[float, float, float]:
    lin = [linear(c) for c in rgb(hex_)]
    m = MACHADO[tipo]
    return tuple(delinear(sum(m[i][j] * lin[j] for j in range(3))) for i in range(3))


def _lab(c: tuple[float, float, float]) -> tuple[float, float, float]:
    r, g, b = (linear(v) for v in c)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883

    def f(t: float) -> float:
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116

    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def delta_e(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.dist(_lab(a), _lab(b))


def main() -> None:
    print("## Texto (alvo >= 4,5:1)")
    for nome, fg, bg in TEXTO:
        r = contraste(fg, bg)
        print(f"{nome:36} {fg} sobre {bg}  {r:5.2f}:1  {'OK' if r >= 4.5 else 'FALHA'}")
    print("\n## Formas (alvo >= 3:1)")
    for nome, fg, bg in FORMAS:
        r = contraste(fg, bg)
        print(f"{nome:36} {fg} sobre {bg}  {r:5.2f}:1  {'OK' if r >= 3 else 'abaixo'}")
    print("\n## Rampa sequencial (luminância deve decrescer)")
    prev = 2.0
    for h in RAMPA:
        l = luminancia(h)
        print(f"{h}  L={l:.3f}  {'OK' if l < prev else 'NAO MONOTONICA'}")
        prev = l
    print("\n## Separação sob daltonismo (delta E CIELAB; >= 20 separa bem)")
    for nome, a, b in PARES_DALTONISMO:
        linha = [f"normal {delta_e(rgb(a), rgb(b)):5.1f}"]
        for tipo in MACHADO:
            linha.append(f"{tipo[:5]} {delta_e(simular(a, tipo), simular(b, tipo)):5.1f}")
        print(f"{nome:34} " + " | ".join(linha))


if __name__ == "__main__":
    main()
