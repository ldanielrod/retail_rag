import re
from typing import Optional, Tuple
from bs4 import BeautifulSoup
from ...core.models import AnuncioBase, AnuncioDetalle
from .config import BASE_URL


def parse_lista_anuncios(html: str, current_page: int) -> Tuple[list[AnuncioBase], bool]:
    soup = BeautifulSoup(html, "html.parser")
    resultados = []
    seen = set()

    contenedor = soup.find(True, class_='generic-results')
    tarjetas = contenedor.find_all('li', recursive=False) if contenedor else []

    for li in tarjetas:
        a = li.find('a', href=True)
        if not a:
            continue

        href = a['href']
        if not href.startswith('http'):
            href = BASE_URL + href
        if href in seen:
            continue
        seen.add(href)

        info2 = li.select_one('div.info2')
        if info2:
            titulo   = info2.get_text(separator='|', strip=True).split('|')[0]
            precio_b = info2.find('b')
            precio_txt = precio_b.get_text(strip=True) if precio_b else ""
        else:
            titulo, precio_txt = "", ""

        resultados.append(AnuncioBase(titulo=titulo, precio_texto=precio_txt, url=href))

    hay_siguiente = bool(
        soup.find('a', string=re.compile(r'siguiente|next', re.I))
        or soup.select_one(f"a[href*='page={current_page + 1}']")
    )
    return resultados, hay_siguiente


def parse_detalle_anuncio(html: str, url: str, operacion: str, sector: str) -> AnuncioDetalle:
    soup = BeautifulSoup(html, "html.parser")

    titulo = soup.select_one('h1').get_text(strip=True) if soup.select_one('h1') else ""

    precio_txt = ""
    precio_b = soup.select_one('div.info2 b')
    if precio_b:
        precio_txt = precio_b.get_text(strip=True)

    habitaciones = _bullet_valor(soup, 'Habitaciones')
    banos        = _bullet_valor(soup, 'Baños')
    metros       = _bullet_metros(soup)

    amueblado = "sí" if re.search(r"amueblad[ao]", soup.get_text(), re.I) else "no"

    loc_el = soup.select_one('div.info2')
    ubicacion = loc_el.get_text(separator='|', strip=True).split('|')[0] if loc_el else ""

    precio_num, moneda = _parse_precio(precio_txt)

    return AnuncioDetalle(
        titulo=titulo, operacion=operacion, sector_buscado=sector,
        precio_texto=precio_txt, precio_num=precio_num, moneda=moneda,
        habitaciones=habitaciones, banos=banos, metros_m2=metros,
        amueblado=amueblado, ubicacion=ubicacion, url=url,
    )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _bullet_valor(soup, label: str) -> Optional[int]:
    """Extrae el número de un bullet como  <span>Habitaciones:</span> 3"""
    for li in soup.select('div.bullets li, ul.bullets li'):
        if label.lower() in li.get_text().lower():
            nums = re.findall(r'\d+', li.get_text())
            if nums:
                return int(nums[0])
    return None


def _bullet_metros(soup) -> Optional[int]:
    """Extrae metros desde  Construcción: 112 Mt2"""
    for li in soup.select('div.bullets li, ul.bullets li'):
        if 'construcci' in li.get_text().lower():
            nums = re.findall(r'\d+', li.get_text())
            if nums:
                return int(nums[0])
    return None


def _parse_precio(texto: str) -> Tuple[Optional[float], str]:
    if not texto:
        return None, ""
    moneda = "USD" if "US$" in texto else "DOP"
    nums = re.findall(r'[\d,]+', texto.replace('.', ''))
    valor = float(nums[0].replace(',', '')) if nums else None
    return valor, moneda
