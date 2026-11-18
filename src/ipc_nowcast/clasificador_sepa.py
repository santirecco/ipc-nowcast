"""Clasificación de productos de SEPA (Precios Claros) en clases del IPC a partir de la descripción.

Las descripciones de SEPA son cortas y suelen empezar por el sustantivo del producto
("LECHE ENTERA ...", "QUESO CREMOSO ...") aunque a veces va primero la marca ("SANCOR LECHE ...").
Por eso se busca la primera palabra "conocida" entre las primeras cuatro. Antes se descartan los
productos que no son alimentos (cosmética, limpieza, bazar, juguetes) con una lista de exclusiones.
"""
from __future__ import annotations

import re
import unicodedata

# palabra (o comienzo de palabra) -> clase. Se compara contra cada palabra normalizada.
PALABRAS = {
    "01.1.1": ["pan", "panes", "pancito", "harina", "arroz", "fideo", "fideos", "tallarin", "spaghetti", "tirabuzon",
               "mostachol", "galletita", "galletitas", "gall", "galle", "galletit", "galleta", "galletas", "crackers", "bizcocho", "bizcochos",
               "bizcochuelo", "tostada", "tostadas", "budin", "tapas", "tapa", "prepizza", "pizza", "pizzas", "medialuna",
               "medialunas", "facturas", "factura", "cereal", "cereales", "copos", "avena", "polenta", "noquis", "ñoquis",
               "ravioles", "raviolones", "sorrentinos", "canelones", "lasagna", "lasana", "pasta", "pastas", "premezcla",
               "granola", "salvado", "semola", "pionono", "vainillas", "grisines", "rebozador", "pan rallado", "magdalenas",
               "magdalena", "torta", "tortitas", "obleas_no", "trigo", "maicena", "fecula", "almidon", "levadura", "capeletinis",
               "capelettis", "mostacholes", "fetuccini", "tagliatelle", "penne", "mezcla"],
    "01.1.2": ["carne", "vacio", "asado", "nalga", "cuadril", "peceto", "bife", "bifes", "milanesa", "milanesas", "pollo",
               "suprema", "supremas", "pata", "muslo", "cerdo", "bondiola", "matambre", "chorizo", "chorizos", "salchicha",
               "salchichas", "hamburguesa", "hamburguesas", "medallon", "medallones", "fiambre", "jamon", "salame", "salamin",
               "mortadela", "paleta", "panceta", "morcilla", "pechuga", "pechugas", "lomo", "colita", "tapa de asado",
               "osobuco", "roast", "picada", "carre", "costilla", "costillas", "achuras", "higado", "mondongo",
               "riñon", "molleja", "chinchulin", "nuggets", "patitas", "arrollado", "lomito", "bocadito", "bocaditos",
               "pastron", "leberwurst", "queso de cerdo", "vitel", "matambrito", "entraña", "entrana", "tortuguita",
               "nalgas", "carnaza", "sobrecostilla", "nalga", "cuadrada", "tapa de nalga", "bola de lomo", "palomita", "churrasco", "pollos", "alitas", "ala", "pavo", "carnes"],
    "01.1.4": ["leche", "yogur", "yogurt", "yoghurt", "queso", "quesos", "que", "crema", "huevo", "huevos", "postre",
               "postres", "flan", "flanes", "ricota", "mozzarella", "muzzarella", "muzarella", "cremoso", "reggianito",
               "rallado", "provoleta", "manchego", "dulce de leche", "leches", "lacteo", "lacteos", "kefir", "budin de leche"],
    "01.1.5": ["aceite", "aceites", "margarina", "grasa", "manteca", "rocio"],
    "01.1.6": ["manzana", "manzanas", "banana", "bananas", "naranja", "naranjas", "mandarina", "mandarinas", "pera",
               "peras", "limon", "limones", "frutilla", "frutillas", "uva", "uvas", "durazno", "duraznos", "kiwi", "anana",
               "pomelo", "palta", "paltas", "ciruela", "ciruelas", "melon", "sandia", "frutas", "fruta", "coctel",
               "nuez", "nueces", "almendra", "almendras", "pasas", "pasa", "castañas", "avellanas", "pistachos", "datiles",
               "arandanos", "cerezas", "damasco", "damascos", "higos", "frutos"],
    "01.1.7": ["papa", "papas", "tomate", "tomates", "cebolla", "cebollas", "lechuga", "zanahoria", "zanahorias", "zapallo",
               "zapallito", "zapallitos", "acelga", "espinaca", "espinacas", "batata", "batatas", "choclo", "choclos",
               "arveja", "arvejas", "lenteja", "lentejas", "poroto", "porotos", "garbanzo", "garbanzos", "champignon",
               "champignones", "champiñones", "hongos", "pimiento", "pimientos", "morron", "morrones", "berenjena",
               "berenjenas", "remolacha", "remolachas", "repollo", "brocoli", "coliflor", "ajo", "ajos", "verdura",
               "verduras", "vegetales", "legumbres", "jardinera", "chauchas", "chaucha", "puerro", "apio", "pepino",
               "rucula", "radicheta", "palmitos", "soja", "mandioca", "calabaza", "hortalizas", "cebollita", "verdeo",
               "esparragos", "alcauciles", "pickles", "pepinillos"],
    "01.1.8": ["azucar", "dulce", "dulces", "mermelada", "jalea", "chocolate", "chocolates", "chocolatin", "tableta",
               "alfajor", "alfajores", "caramelo", "caramelos", "chicle", "chicles", "golosina", "golosinas", "bombon",
               "bombones", "helado", "helados", "oblea", "obleas", "turron", "turrones", "endulzante", "edulcorante", "miel",
               "confites", "pastillas", "chupetin", "chupetines", "gomitas", "malvaviscos", "bocadito de chocolate",
               "barrita", "barritas", "cubanitos", "membrillo", "batata dulce", "jaleas", "almibar", "chocolatada_no"],
    "01.1.resto": ["mayonesa", "ketchup", "mostaza", "salsa", "salsas", "pure", "aderezo", "aderezos", "sal", "condimento",
                   "condimentos", "especias", "pimienta", "oregano", "pimenton", "aji", "comino", "caldo", "caldos", "sopa",
                   "sopas", "vinagre", "aceto", "atun", "caballa", "sardina", "sardinas", "merluza", "pescado", "filet",
                   "filete", "mariscos", "langostinos", "calamar", "salmon", "abadejo", "kanikama", "snack", "snacks",
                   "palitos", "mani", "aceitunas", "aceituna", "conserva", "empanadas", "empanada", "tarta", "tartas",
                   "croquetas", "bastones", "rebozados", "pate", "paté", "gelatina", "postre en polvo", "bizcochuelo en polvo",
                   "polvo", "esencia", "colorante", "chimichurri", "provenzal", "nachos", "chizitos", "tutuca", "pochoclo",
                   "pororo", "anchoas", "humus", "hummus", "tofu", "seitan", "saborizador", "adobo", "fondo", "risotto",
                   "rissot", "sandwich", "sandwiches", "wraps", "comida", "pastel", "tortilla", "tortillas"],
    "01.2.1": ["yerba", "cafe", "te", "tes", "mate", "cacao", "saquitos", "capuccino", "cappuccino", "malta", "infusion",
               "chocolatada", "nesquik", "toddy", "cascarilla"],
    "01.2.2": ["agua", "aguas", "gaseosa", "gaseosas", "jugo", "jugos", "soda", "isotonico", "isotonica", "energizante",
               "amargo", "bebida", "bebidas", "pomelo_no", "limonada", "tonica", "agua saborizada", "polvo para jugo",
               "sifon", "refresco", "cola", "pepsi", "sprite", "fanta", "seven", "powerade", "gatorade", "speed", "monster"],
    "02.1": ["vino", "vinos", "cerveza", "cervezas", "fernet", "whisky", "whiskey", "vodka", "gin", "sidra", "espumante",
             "champagne", "champaña", "aperitivo", "licor", "ron", "tequila", "vermouth", "vermut", "gancia", "campari",
             "aperol", "malbec", "cabernet", "chardonnay", "torrontes", "brut", "cognac", "brandy", "grappa", "anis",
             "cynar", "hesperidina", "bitter", "porron", "sake"],
}
# Expresiones que excluyen el producto (no es alimento o no corresponde a la clase).
EXCLUIR = re.compile(
    r"\b(jabon|detergen\w*|lavandin\w*|limpiador\w*|suavizante|shampoo|champu|acondicionador|desodorante|desod|panal\w*|"
    r"toallit\w*|toalla\w*|papel|servillet\w*|perro\w*|gato\w*|mascota\w*|pedigree|whiskas|insectic\w*|esponja|"
    r"bolsas?|dental|cepillo|afeitar|preservativo\w*|tintura|coloracion|esmalte|protector|repelente|algodon|aposito\w*|"
    r"curitas|pilas?|lampara|encendedor|carbon|alcohol|desinfect\w*|cloro|cera|trapo|rejilla|film|aluminio|vaso\w*|"
    r"plato\w*|cubierto\w*|fosforos?|velas?|maquill\w*|labial|colonia|perfume|talco|corporal|facial|manos|peinar|"
    r"micelar|oxigenada|lanzador|pistola|juguete\w*|peluche|aromatizante|calefactor|olla|sarten|termo|botella|jarra|"
    r"mate de|bombilla|tetera|cafetera|pava|exprimidor|cortador|rallador|molde|recipiente|tupper|taza\w*|mug|"
    r"set|kit|juego|disfraz|mascara|adorno\w*|navide\w*|guirnalda|regalo|tarjeta|crema de enjuague|enjuague|"
    r"bronceador|autobronceante|hidratante|antitranspirante|gel|serum|exfoliante|nutritiva para|tratamiento|"
    r"alimento para|balanceado|piedras|arena|sanitaria|bebe|bebes|baby|infantil formula|nutrilon|nan|sancor bebe|"
    r"vela|incienso|difusor|repuesto|recarga|rociador|dispenser|det|emoc|maquina|espumador|colchoneta|enduido|autos|masc|"
    r"nivea|hinds|loreal|revitalift|dove|ponds|rexona|axe|colgate|garnier|pantene|sedal|elvive|dif|rep|robo|cuch|cuchara|lata|latex|pintura|esmalte|jersey|denim|remera|pantalon|media|medias|short|"
    r"pijama|ojota|zapatilla|campera|buzo|camisa|vestido|pollera|bermuda|musculosa|boxer|bombacha|corpino)\b")

_INDICE: dict[str, str] = {}
_FRASES: list[tuple[str, str]] = []
for _clase, _palabras in PALABRAS.items():
    for _p in _palabras:
        if _p.endswith("_no"):
            continue
        if " " in _p:
            _FRASES.append((_p, _clase))
        else:
            _INDICE.setdefault(_p, _clase)
_FRASES.sort(key=lambda x: -len(x[0]))


def normalizar(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s.replace("/", " ").replace(".", " "))
    return re.sub(r"\s+", " ", s).strip()


# Palabras que solo deciden si no aparece otra más específica (ej. "TAPA DE NALGA", "COCO RALLADO").
DEBILES = {"tapa", "tapas", "pasta", "pastas", "mezcla", "crema", "dulce", "dulces", "mate", "te", "rallado", "palitos",
           "bocadito", "bocaditos", "polvo", "fondo", "barrita", "barritas", "tableta", "pastillas", "bebida", "bebidas",
           "frutos", "fruta", "frutas", "salsa", "comida", "que", "cremoso", "pure", "rocio", "mix"}
# Frutas y verduras: solo cuentan si son la primera palabra (si no, suelen ser un sabor: "JUGO ... NARANJA").
SOLO_PRIMERA = {"manzana", "manzanas", "banana", "bananas", "naranja", "naranjas", "mandarina", "mandarinas", "pera",
                "peras", "limon", "limones", "frutilla", "frutillas", "uva", "uvas", "durazno", "duraznos", "kiwi",
                "anana", "pomelo", "ciruela", "ciruelas", "melon", "sandia", "damasco", "cerezas", "arandanos", "tomate",
                "cebolla", "zanahoria", "zapallo", "calabaza", "espinaca", "choclo", "papa", "batata", "pimiento",
                "morron", "ajo", "coco", "mani", "cafe", "cacao", "vainilla", "chocolate", "miel", "lenteja", "lentejas"}


def clasificar(descripcion: str) -> str | None:
    t = normalizar(descripcion)
    if not t or EXCLUIR.search(t):
        return None
    for frase, clase in _FRASES:  # frases que cambian el sentido: "dulce de leche", "pan rallado", "papas fritas"
        if t.startswith(frase) or f" {frase} " in f" {t} "[:60]:
            return clase
    palabras = t.split()[:4]
    candidatos = [(i, p) for i, p in enumerate(palabras) if p in _INDICE and (i == 0 or p not in SOLO_PRIMERA)]
    fuertes = [c for c in candidatos if c[1] not in DEBILES]
    for i, p in (fuertes or candidatos)[:1]:
        if True:
            clase = _INDICE[p]
            # casos ambiguos frecuentes
            if p in ("papas", "papa") and re.search(r"\bfritas?\b|\bpay\b|chips|snack|\bpringles\b", t):
                return "01.1.resto"
            if p == "pure" and re.search(r"\bpapa", t):
                return "01.1.7"
            if p == "crema" and re.search(r"\b(helad|chantilly)", t):
                return "01.1.4"
            if p in ("pan",) and re.search(r"\bhamburgues|\bpancho|\bviena", t):
                return "01.1.1"
            return clase
    return None


EXTRA_FRASES = [("salsa de soja", "01.1.resto"), ("leche de coco", "01.1.resto"), ("coco rallado", "01.1.6"), ("dulce de leche", "01.1.4"), ("pan rallado", "01.1.1"), ("papas fritas", "01.1.resto"),
                ("tapa de asado", "01.1.2"), ("queso de cerdo", "01.1.2"), ("batata dulce", "01.1.8"),
                ("postre en polvo", "01.1.resto"), ("agua saborizada", "01.2.2"), ("polvo para jugo", "01.2.2"),
                ("mate cocido", "01.2.1"), ("budin de leche", "01.1.4"), ("bocadito de chocolate", "01.1.8")]
for _f, _c in EXTRA_FRASES:
    if (_f, _c) not in _FRASES:
        _FRASES.append((_f, _c))
_FRASES.sort(key=lambda x: -len(x[0]))


# Carne vacuna fresca (cortes al mostrador): la usa un índice aparte, porque la clase 01.1.2 de SEPA mezcla
# fiambres, hamburguesas y congelados que se mueven distinto que la carne que mide INDEC.
VACUNO_FRESCO = re.compile(
    r"\b(asado|vacio|nalga|cuadril|peceto|bife|bola de lomo|lomo|matambre|falda|roast|osobuco|tapa de asado|tapa de nalga|"
    r"carnaza|palomita|colita|entrana|picada|carne picada|paleta|cuadrada|tortuguita|aguja|marucha|blando|churrasco|"
    r"ojo de bife|tapa de bife)\b")
NO_FRESCO = re.compile(
    r"\b(cerdo|pollo|pavo|soja|vegana?|vegetal|pescado|merluza|salmon|atun|fiambre|jamon|salame|hamburgues\w*|medallon\w*|"
    r"rebozad\w*|congelad\w*|swift|paty|nuggets|empanad\w*|tarta|pizza|sopa|caldo|pure|salsa|ravioles|sorrentinos|tapas|"
    r"alfajor|galletit\w*|jugo|queso|maquillaje\w*|banqueta|chocolate|choc|crema|sombras|silla)\b")


def es_carne_fresca(descripcion: str) -> bool:
    t = normalizar(descripcion)
    return bool(VACUNO_FRESCO.search(t)) and not NO_FRESCO.search(t)
