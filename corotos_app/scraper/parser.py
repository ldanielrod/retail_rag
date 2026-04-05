import re
from typing import Optional, Tuple
from bs4 import BeautifulSoup

from ..core.config import BASE_URL
from ..core.models import AnuncioBase, AnuncioDetalle

def parse_precio(texto: str) -> Tuple[Optional[float], str]:
    if not texto: return None, ""
    moneda  = "USD" if ("US$" in texto or "USD" in texto) else "DOP"
    limpio  = texto.replace(",", "").replace(".", "")
    numeros = re.findall(r"\d+", limpio)
    valor   = float("".join(numeros)) if numeros else None
    return valor, moneda

def parse_lista_anuncios(html_content: str, current_page: int) -> Tuple[list[AnuncioBase], bool]:
    soup = BeautifulSoup(html_content, "html.parser")
    anchors = soup.select("a[href*='/anuncio/inmuebles-en-']")
    resultados = []
    seen = set()

    for a in anchors:
        href = a.get("href", "")
        if not href.startswith("http"):
            href = BASE_URL + href
        if href in seen or "/anuncio/" not in href:
            continue
        seen.add(href)

        precio_el  = a.select_one("[class*='price'], [class*='precio'], strong")
        precio_txt = precio_el.get_text(strip=True) if precio_el else ""
        if not precio_txt:
            m = re.search(r"(RD\$|US\$)\s?[\d,\.]+", a.get_text())
            precio_txt = m.group(0) if m else ""

        titulo_el = a.select_one("h2, h3, p")
        titulo    = titulo_el.get_text(strip=True) if titulo_el else a.get_text(strip=True)[:80]
        resultados.append(AnuncioBase(titulo=titulo, precio_texto=precio_txt, url=href))

    hay_siguiente = bool(
        soup.find("a", string=re.compile(r"siguiente|next", re.I))
        or soup.select_one(f"a[href*='page={current_page + 1}']")
    )
    return resultados, hay_siguiente

def parse_detalle_anuncio(html_content: str, url: str, operacion: str, sector_buscado: str) -> AnuncioDetalle:
    soup = BeautifulSoup(html_content, "html.parser")
    h1 = soup.select_one("h1")
    titulo = h1.get_text(strip=True) if h1 else ""

    precio_txt = ""
    m = re.search(r"(RD\$|US\$)\s?[\d,\.]+", soup.get_text())
    if m: precio_txt = m.group(0)
    precio_num, moneda = parse_precio(precio_txt)

    habitaciones: Optional[int] = None
    banos: Optional[int] = None
    metros: Optional[int] = None

    for li in soup.select("li"):
        texto_li = li.get_text(separator="|", strip=True).lower()
        if habitaciones is None and ("habitaci" in texto_li or re.match(r"^hab", texto_li)):
            for n in re.findall(r"\b(\d{1,2})\b", texto_li):
                if 1 <= int(n) <= 20: habitaciones = int(n); break
        elif banos is None and ("baño" in texto_li or "bano" in texto_li):
            for n in re.findall(r"\b(\d{1,2})\b", texto_li):
                if 1 <= int(n) <= 10: banos = int(n); break
        elif metros is None and ("m²" in texto_li or "metros" in texto_li or "tamaño" in texto_li):
            nums = re.findall(r"\b(\d{2,4})\b", texto_li)
            if nums: metros = int(nums[0])

    texto_completo = soup.get_text(separator=" ").lower()
    if habitaciones is None:
        m_hab = re.search(r"\b([1-9]|1[0-9]|20)\s*(habitaci[oó]n(?:es)?|hab\.)", texto_completo)
        if m_hab: habitaciones = int(m_hab.group(1))
    if banos is None:
        m_ban = re.search(r"\b([1-9]|10)\s*(ba[ñn]o(?:s)?)", texto_completo)
        if m_ban: banos = int(m_ban.group(1))
    if metros is None:
        m_m2 = re.search(r"\b(\d{2,4})\s*m[²2]", texto_completo)
        if m_m2: metros = int(m_m2.group(1))

    amueblado = "sí" if re.search(r"amueblad[ao]", soup.get_text(), re.I) else "no"

    loc_el = soup.select_one("[class*='location'], [itemprop='address'], [class*='ubicacion']")
    ubicacion = loc_el.get_text(strip=True) if loc_el else ""
    if not ubicacion:
        loc_m = re.search(r"(santo domingo|santiago|distrito nacional)[^\n]{0,80}", texto_completo)
        ubicacion = loc_m.group(0).strip().title() if loc_m else ""

    return AnuncioDetalle(
        titulo=titulo, operacion=operacion, sector_buscado=sector_buscado,
        precio_texto=precio_txt, precio_num=precio_num, moneda=moneda,
        habitaciones=habitaciones, banos=banos, metros_m2=metros,
        amueblado=amueblado, ubicacion=ubicacion, url=url
    )
