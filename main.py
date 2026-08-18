
import json
import re
import threading
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout

KV = r"""
#:import dp kivy.metrics.dp

<ProductBox>:
    orientation: "vertical"
    padding: dp(14)
    spacing: dp(10)

    Label:
        text: "📣 Tecnologia Store — Gerador de Divulgação"
        font_size: dp(20)
        bold: True
        color: 0.95, 1, 0.98, 1
        size_hint_y: None
        height: dp(42)

    Label:
        text: "Cole o link da Shopee. O app tenta buscar título, preço, imagem e desconto automaticamente."
        color: 0.72, 0.84, 0.79, 1
        text_size: self.width, None
        size_hint_y: None
        height: dp(48)

    TextInput:
        id: link
        hint_text: "Cole aqui o link da Shopee..."
        multiline: False
        size_hint_y: None
        height: dp(48)
        background_color: 0.07, 0.10, 0.12, 1
        foreground_color: 1, 1, 1, 1
        padding: dp(12)

    BoxLayout:
        size_hint_y: None
        height: dp(48)
        spacing: dp(8)
        Button:
            text: "🔎 Buscar informações"
            on_release: root.buscar(link.text)
        Button:
            text: "📋 Colar"
            on_release: root.colar()

    Label:
        id: status
        text: root.status
        color: 0.35, 1, 0.65, 1
        text_size: self.width, None
        size_hint_y: None
        height: dp(34)

    TextInput:
        id: title
        hint_text: "Título do produto"
        multiline: False
        size_hint_y: None
        height: dp(44)

    BoxLayout:
        size_hint_y: None
        height: dp(44)
        spacing: dp(8)
        TextInput:
            id: price
            hint_text: "Preço"
            multiline: False
        TextInput:
            id: old_price
            hint_text: "Preço antigo (opcional)"
            multiline: False

    BoxLayout:
        size_hint_y: None
        height: dp(44)
        spacing: dp(8)
        TextInput:
            id: discount
            hint_text: "Desconto (opcional)"
            multiline: False
        TextInput:
            id: image
            hint_text: "URL da imagem (opcional)"
            multiline: False

    Button:
        text: "✨ GERAR DIVULGAÇÃO"
        size_hint_y: None
        height: dp(52)
        background_color: 0.05, 0.55, 0.30, 1
        on_release: root.gerar()

    TextInput:
        id: output
        hint_text: "A divulgação aparecerá aqui..."
        readonly: True
        multiline: True
        background_color: 0.05, 0.07, 0.08, 1
        foreground_color: 0.95, 0.98, 0.96, 1

    BoxLayout:
        size_hint_y: None
        height: dp(50)
        spacing: dp(8)
        Button:
            text: "📋 COPIAR TEXTO"
            on_release: root.copiar()
        Button:
            text: "📤 COMPARTILHAR"
            on_release: root.compartilhar()

    Label:
        text: "Dica: se a Shopee bloquear a consulta automática, preencha título/preço manualmente e gere a divulgação."
        color: 0.55, 0.62, 0.60, 1
        text_size: self.width, None
        size_hint_y: None
        height: dp(42)
"""

Builder.load_string(KV)


def clean_text(value):
    if not value:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def brl(value):
    """Normalize common price formats to R$ 0,00."""
    if value is None:
        return ""
    s = clean_text(value)
    s = re.sub(r"[^\d,\.]", "", s)
    if not s:
        return ""
    # Handle Brazilian and US-like decimal representations.
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        # If there is exactly one dot, assume decimal point.
        if s.count(".") > 1:
            s = s.replace(".", "")
    try:
        n = float(s)
        return f"R$ {n:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return value if str(value).startswith("R$") else f"R$ {value}"


def find_price(text):
    patterns = [
        r'R\$\s?[\d\.\,]+',
        r'BRL\s?[\d\.\,]+',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.I)
        if m:
            return brl(m.group(0))
    return ""


def extract_product(html, final_url):
    soup = BeautifulSoup(html, "html.parser")
    data = {"url": final_url, "title": "", "price": "", "old_price": "", "discount": "", "image": ""}

    # OpenGraph / Twitter metadata
    metas = {}
    for tag in soup.find_all("meta"):
        key = tag.get("property") or tag.get("name")
        val = tag.get("content")
        if key and val:
            metas[key.lower()] = val

    data["title"] = clean_text(
        metas.get("og:title") or metas.get("twitter:title") or
        (soup.title.string if soup.title and soup.title.string else "")
    )
    data["image"] = metas.get("og:image") or metas.get("twitter:image") or ""

    # JSON-LD Product data
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            obj = json.loads(script.string or script.get_text())
            objects = obj if isinstance(obj, list) else [obj]
            for item in objects:
                if not isinstance(item, dict):
                    continue
                if item.get("@type") == "Product" or "offers" in item:
                    data["title"] = clean_text(item.get("name") or data["title"])
                    img = item.get("image")
                    if isinstance(img, list):
                        img = img[0] if img else ""
                    data["image"] = img or data["image"]
                    offers = item.get("offers", {})
                    if isinstance(offers, list):
                        offers = offers[0] if offers else {}
                    if isinstance(offers, dict):
                        data["price"] = brl(offers.get("price") or offers.get("lowPrice") or "")
                    if data["price"]:
                        break
        except Exception:
            pass

    # Common embedded data patterns used by e-commerce pages.
    text = soup.get_text(" ", strip=True)
    if not data["price"]:
        data["price"] = find_price(text)

    # Search embedded JSON for price/current_price and discount.
    for key in ("current_price", "sale_price", "price", "price_min"):
        if not data["price"]:
            m = re.search(rf'"{key}"\s*:\s*"?([0-9]+(?:\.[0-9]+)?)"?', html, re.I)
            if m:
                data["price"] = brl(m.group(1))
    if not data["old_price"]:
        for key in ("original_price", "old_price", "price_before_discount"):
            m = re.search(rf'"{key}"\s*:\s*"?([0-9]+(?:\.[0-9]+)?)"?', html, re.I)
            if m:
                data["old_price"] = brl(m.group(1))
                break

    # Try to infer discount percentage.
    if data["old_price"] and data["price"]:
        try:
            old = float(re.sub(r"[^\d,]", "", data["old_price"]).replace(".", "").replace(",", "."))
            new = float(re.sub(r"[^\d,]", "", data["price"]).replace(".", "").replace(",", "."))
            if old > new:
                data["discount"] = f"{round((1 - new / old) * 100)}% OFF"
        except Exception:
            pass

    return data


class ProductBox(BoxLayout):
    status = StringProperty("Pronto para buscar.")

    def colar(self):
        self.ids.link.text = Clipboard.paste() or ""

    def buscar(self, url):
        url = clean_text(url)
        if not url:
            self.status = "Cole um link da Shopee primeiro."
            return
        if "shopee" not in url.lower():
            self.status = "O link informado não parece ser da Shopee."
            return

        self.status = "Buscando dados do produto..."
        threading.Thread(target=self._fetch, args=(url,), daemon=True).start()

    def _fetch(self, url):
        try:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0 Mobile Safari/537.36"
                ),
                "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
            }
            r = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
            r.raise_for_status()
            data = extract_product(r.text, r.url)
            Clock.schedule_once(lambda dt: self._fill(data), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._error(str(e)), 0)

    def _fill(self, data):
        self.ids.link.text = data.get("url") or self.ids.link.text
        self.ids.title.text = data.get("title", "")
        self.ids.price.text = data.get("price", "")
        self.ids.old_price.text = data.get("old_price", "")
        self.ids.discount.text = data.get("discount", "")
        self.ids.image.text = data.get("image", "")
        self.status = "✅ Informações encontradas. Revise e gere a divulgação."

    def _error(self, msg):
        self.status = "⚠️ Não foi possível ler a página automaticamente. Preencha os campos e tente gerar."

    def gerar(self):
        title = clean_text(self.ids.title.text) or "Oferta especial"
        price = clean_text(self.ids.price.text)
        old = clean_text(self.ids.old_price.text)
        discount = clean_text(self.ids.discount.text)
        link = clean_text(self.ids.link.text)

        parts = [f"🔥 {title}"]
        if discount:
            parts.append(f"🏷️ {discount}")
        if old and price:
            parts.append(f"💰 De {old} por {price}")
        elif price:
            parts.append(f"💰 Por apenas {price}")
        else:
            parts.append("💰 Confira o preço no link!")

        parts += [
            "",
            "🛒 Aproveite essa oferta na Shopee!",
            "⚡ Estoque e preço podem mudar a qualquer momento.",
        ]
        if link:
            parts += ["", f"🔗 Comprar agora: {link}"]

        self.ids.output.text = "\n".join(parts)
        self.status = "✅ Divulgação pronta para copiar."

    def copiar(self):
        text = self.ids.output.text
        if text:
            Clipboard.copy(text)
            self.status = "📋 Texto copiado para a área de transferência."

    def compartilhar(self):
        text = self.ids.output.text
        if not text:
            self.status = "Gere a divulgação antes de compartilhar."
            return
        try:
            from jnius import autoclass
            Intent = autoclass("android.content.Intent")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            intent = Intent(Intent.ACTION_SEND)
            intent.setType("text/plain")
            intent.putExtra(Intent.EXTRA_TEXT, text)
            chooser = Intent.createChooser(intent, "Compartilhar divulgação")
            PythonActivity.mActivity.startActivity(chooser)
            self.status = "📤 Abrindo opções de compartilhamento..."
        except Exception:
            Clipboard.copy(text)
            self.status = "📋 Compartilhamento não disponível; texto copiado."


class TecnologiaStoreApp(App):
    def build(self):
        self.title = "Tecnologia Store — Divulgador Shopee"
        return ProductBox()


if __name__ == "__main__":
    TecnologiaStoreApp().run()
