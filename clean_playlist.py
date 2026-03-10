"""
clean_playlist.py
=================
Limpia lista_unificada.m3u aplicando todas las reglas definidas.
Uso: python clean_playlist.py [archivo_entrada] [archivo_salida]
     Si no se especifican, usa lista_unificada.m3u (in-place).
"""
import sys
import re
import os

sys.stdout.reconfigure(encoding='utf-8')

# ---------------------------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------------------------

# Categorías que se eliminan por completo
DELETE_CATEGORIES = {
    "Cine y Películas",
    "Religión",
    "Pluto TV",
    "Series",
    "Comedia",
}

# Canales 24/7: eliminar exactamente estos nombres, conservar el resto
DELETE_247 = {
    "Punto Movies", "Beto 7hd", "Neflix01", "Cheli Cooper", "Cinemundo Plus",
    "Peliculas Mania", "Terror Mania", "Shay Saheed", "A Juanmusic", "Cienciaficcion",
    "Cienciaficcion01", "Agente de Familia", "Tele29", "Ysblf", "Disney", "2312",
    "Ganja Gv", "Malcomhd", "Ganja Tv 2", "shy ch eurydice", "zonafilmsterror",
    "tufortunatv", "zonafilmstvseries", "rincondegago", "radiofelove", "ovninews",
    "cityfm", "chelito sv", "nezradiovision", "tvsalvision", "felovetv", "ficoatv",
    "fundacion1410", "lvpradiotv", "omega tv", "telemedellin", "tv777", "vozdelcielotv",
    "yhwhesmisalvacion",
    "Acapulco Shore 24/7 (i)", "Acapulco Shore P", "Acapulco Shore 24/7 (i) op2",
    "Rosa de Guadalupe i", "Rosa de Guadalupe P",
    "Cops en Espanol P", "That 70s Show 24/7 I", "Yellowstone P", "Chicago Fire P",
    "24/7 Starz Family (1080)", "24/7 Starz Encore Action (1080)",
    "24/7 Starz East(1080)", "24/7 Starz East (1080)",
    "24/7 Starz Comedy(1080)", "24/7 Starz Comedy (1080)",
    "24/7 Starz Cinema West (1080)", "24/7 Starz Encore West (1080)",
    "24/7 RetroPlex (1080)", "24/7 OuterMax (1080)", "24/7 MoviePlex (1080)",
    "24/7 MovieMax (1080)", "24/7 IndiePlex (1080)",
    "24/7 Cinemax West (1080)", "24/7 Showtime West (1080)",
}

# Canales a conservar por categoría (el resto se elimina)
KEEP_ARGENTINA = {
    "Anime Zone TV", "Locomotion", "Paka Paka", "Canal 4 San Juan", "Zonda TV",
    "TV Publica", "Music Top", "Sonido Sur", "ZN Noticias",
    "Cool 103.7 (Radio con Video) | HD", "Music Top | HD", "TreceMax TV | SD",
    "Canal 5 Telesol | HD", "El Trece", "A24 (720)", "Direct TV Sports (720)",
    "Espn (Local)", "Espn +", "Espn + (720)", "Espn 1 (720)", "Espn 2 (720)",
    "Espn 3 (720)", "Fox Sports", "Fox Sports 1 (1080)", "Fox Sports 2",
    "Fox Sports 3", "Fox Sports Premium (Local)", "FOX Sports Premium",
    "TNT Sports (1080)", "TYC Sports", "TyC Sports (720)", "A24 (1080)", "A24",
    "America", "America TV", "C5N", "C5N (720)", "El Nueve", "Canal De La Ciudad",
    "Cronica", "Cronica TV (720)", "El Nueve (1080)", "El Trece (1080)",
    "El trece (1080)", "Encuentro (720)", "LN", "Quiero Musica", "Senado",
    "Telefe", "Telefe (720)", "TN", "Todo Noticias (720)", "TV5",
}

KEEP_ENTRETENIMIENTO = {
    "Telefe Hits", "5TV Corrientes (480p) [Not 24/7]",
    "Canal 2 de Ushuaia (1080p)", "Canal 3 La Pampa (1080p)",
    "Canal 3 Las Heras (720p)", "Canal 4 Posadas (576p)",
    "Canal 5 Pico Truncado (540p)", "Canal 5 Santa Fe (240p)",
    "Canal 6 Posadas (1080p)", "Canal 7 Santiago del Estero (720p)",
    "Canal 9 Litoral (720p)", "Canal 9 Resistencia (720p)",
    "Canal 11 de la Costa (720p)", "Canal 12 Puerto Madryn (720p) [Not 24/7]",
    "Canal 13 La Rioja (480p)", "Canal 79 La Costa (240p)",
    "Canal 79 Santa Clara del Mar (240p)", "Canal America (720p)",
    "Chilecito TV (480p)", "CSI en Español", "CSI: Miami en español",
    "CSI: NY en español", "Lapacho TV Canal 11 (720p)", "MTV Flow Latino",
    "Radiocanal San Francisco (1080p)",
    "South Park: Butters Collection", "South Park: Cartman Collection",
    "South Park: Kenny Collection", "South Park: Kyle Collection",
    "South Park: Stan Collection",
    "Stargate", "VTV Canal 32 (1080p)", "PrideTV Latam",
    "Telpin Teven (Argentina)", "PakaPaka (Argentina)",
    "Canal 3 (Argentina)", "Canal 4 (Argentina)", "Canal 9 (Argentina)",
    "Canal 4 (San Juan)", "CineCanal (1080)", "Cinecanal",
    "MTV en Español", "PRIDEtv LATAM (720p)",
}

KEEP_MUSICA = {
    "Cumbia Mix (720p)", "Dance TV [Geo-blocked]", "Más FM 95.9 (720p)",
    "MTV Biggest Pop", "MTV Classic", "MTV Classic (360p)", "MTV Hits Europe",
    "MTV Live", "MTV Music", "MTV Spankin' New",
    "Tropi Q 99.7 FM (1080p)", "Tu Música HD (1080p)", "Urbano TV (720p)",
    "Vevo 2K", "Vevo '70s", "Vevo '80s", "Vevo '90s", "Vevo Country",
    "Vevo R&B", "Vevo Retro Rock", "Vevo True School Hip-Hop", "VH1 East",
    "MTV (1080)", "MTV", "MTV Hits", "MTV Hits(720)", "MTV Live (1080)",
    "VH1 (1080)", "VH1", "VH1 Classic", "Vh1 Classics", "VH1 P", "VH1 Plus",
    "MTV (MX)(P)", "MTV HITS (MX)(P)", "MTV 00'S (MX)(P)",
    "MTV LIVE (MX)(P)", "MTV LIVE HD (MX)(P)", "MTV LIVE LQ (MX)(P)",
    "MTV LQ (MX)(P)", "MTV Rocks", "MTV Flow Latino",
}

KEEP_NOTICIAS = {
    "24/7 Canal de Noticias", "A24 (720p)", "ATV Argentina",
    "Canal 26 (1080p)", "Multivision Federal", "TN",
    "Aleph News (720p)", "Canal E (720p)", "Catamarca TV (720p)",
}

KEEP_INFANTIL = {
    "Nick Jr. Club", "Nickelodeon Clásico", "Rugrats",
    "Nickelodeon Rocket Power", "Nickelodeon Pluto TV",
    "Bob Esponja Pantalones Cuadrados", "Los Padrinos Mágicos",
    "Las Tortugas Ninja", "Kartoon Channel!",
    "Nickelodeon (Spain) (576p)", "Nickelodeon en Español",
    "Ctoon Net Mexico H265 (i)", "Disney Channel HD (i)",
    "Disney Jr HD Mexico (i)", "D-overy INFANTIL HD Mexico (i)",
    "Nickelodeon ES (i)", "Nick Junior Mexico (i)",
    "NickToons HD. (i)", "TeenNick Mexico (i)",
    "CARTOON NETWORK (MX)(P)", "CARTOON NETWORK HD (MX)(P)",
    "CARTOON NETWORK LQ (MX)(P)", "CARTOONITO (MX)(P)",
    "CARTOONITO HD (MX)(P)", "CARTOONITO LQ (MX)(P)",
    "BABY FIRST (MX)(P)", "BABY FIRST HD (MX)(P)",
    "BABY TV (MX)(P)", "BABY TV HD (MX)(P)",
    "DISCOVERY INFANTIL (MX)(P)", "DISCOVERY INFANTIL HD (MX)(P)",
    "DISCOVERY INFANTIL LQ (MX)(P)", "DISNEY CHANNEL (MX)(P)",
    "DISNEY CHANNEL HD (MX)(P)", "DISNEY CHANNEL LQ (MX)(P)",
    "DISNEY JUNIOR (MX)(P)", "DISNEY JUNIOR HD (MX)(P)",
    "DISNEY JUNIOR LQ (MX)(P)", "NICK HD (MX)(P)",
    "NICK JR. (MX)(P)", "NICK JR. HD (MX)(P)",
    "NICK LQ (MX)(P)", "NICK. JR LQ (MX)(P)",
    "ONCE NIÑ@S (MX)(P)", "TEEN NICK (MX)(P)",
    "TOONCAST (MX)(P)", "TOONCAST LQ (MX)(P)",
    "NICK (MX)(P)", "Disney Channel Latin America (1080p)",
}

KEEP_DOCUMENTALES = {
    "National Geographic Latin America South (1080p)",
    "Animal Planet (1080)", "Animal Planet (720)", "Animal Planet",
    "Discovery Channel (1080)", "Discovery Channel (720)", "Discovery Channel",
    "Discovery Civilization (1080)", "Discovery Familia", "Discovery Familia (720)",
    "Discovery Home & Health (1080)", "Discovery Home & Health (720)",
    "Discovery Home & Health", "Discovery Science (720)", "Discovery Science",
    "Discovery Theater (1080)", "Discovery Theater",
    "Discovery TLC (1080)", "Discovery TLC",
    "Discovery Turbo (1080)", "Discovery Turbo (720)", "Discovery Turbo",
    "Discovery World (1080)", "Discovery World (720)", "Discovery World",
    "History Channel (1080)", "History Channel (720)", "History Channel",
    "Nat Geo Mundo", "NatGeo (1080)", "NatGeo (720)", "NatGeo",
    "NatGeo Wild (1080)", "NatGeo Wild (720)", "NatGeo Wild",
}

KEEP_TV_PREMIUM = {
    "AMC HD", "AXN HD", "Adult Swim", "Baby TV", "CNN Español",
    "Cartoon Network HD", "Cartoonito", "Cinecanal HD", "Cinemax HD",
    "Comedy Central HD", "Discovery Channel", "Discovery H&H HD",
    "Discovery HD", "Discovery Kids HD", "Discovery Science",
    "Discovery Theater HD", "Discovery Turbo", "Discovery World HD",
    "Disney HD", "Disney Junior", "El Gourmet HD", "Eurochannel",
    "FX HD", "Food Network HD", "Golden Edge", "Golden HD",
    "HBO 2", "HBO Family", "HBO HD", "HBO POP HD", "HBO XTREME HD",
    "HTV", "History 2", "History Channel HD", "Hola TV",
    "ID - Investigation Discovery", "Kanal D Drama", "Lifetime",
    "Lolly Kids", "Love Nature", "MTV HD", "MTV Live", "Nat Geo HD",
    "Nick HD", "Nick Jr", "Nick Music", "Paramount HD", "Pasiones HD",
    "STAR CHANNEL HD", "Sony", "Space HD", "Studio Universal HD",
    "Sun Channel HD", "TCM", "TLC", "TNT HD", "TNT Series HD",
    "Teen Nick", "Telesur", "Tooncast", "UNIVERSAL CHANNEL HD",
    "Warner Channel HD", "A&E", "AXN", "BABY TV", "BOOMERAN",
    "DISCOVERY TURBO", "DISNEY JR", "FX", "HBO", "HBO +", "ISAT",
    "MTV HITS", "NATGEO LA", "STUDIO UNIVERSAL", "TNT SERIES", "VH1",
    "VIDEO ROLA", "history 2", "hola tv", "CNN", "AMC", "ATLAS",
    "BABY FIRST", "CANAL INFANTIL SD", "CARTOON NETWORK", "CINE LATINO",
    "CINEMAX", "COMEDY CENTRAL", "Cartonito", "DISCOVERY ID",
    "DreamWorks TV Latin America", "EXA TV", "FILM  &  ARTS",
    "HBO FAMILY", "HBO MUNDI", "HBO SIGNATURE", "HBO XTREME",
    "MTV 00", "MULTI PREMIER", "MULTIPREMIER", "NICK JR", "NICKMUSIC",
    "Once niñas y niños", "PARAMOUNT", "SPACE", "SYFY", "WARNER",
    "dw espa", "france 24", "tnt novelas", "A&E HD", "De Pelicula",
    "MTV LIVE HD", "Cartoon Network", "DE PELICULA", "Baby First",
    "Boomerang", "Discovery Kids", "Disney JR", "Disney channel",
    "Nick 2 HD", "Nickelodeon HD", "SEMILLITAS", "Concert Channel",
    "Exa TV", "MTV", "MTV 00s HD", "MTV 80s", "MTV Hits", "MTV SIM HD",
    "DISCOVERY THEATHER HD", "Discovery Channel HD", "Discovery ID HD",
    "El Gourmet", "HBO Family HD", "HBO Plus HD", "HBO2 HD",
    "SONY HD", "SONY MOVIES HD", "STAR LIFE", "Sun Channel",
    "TNT Novelas", "UNIVERSAL CINEMA HD", "UNIVERSAL COMEDY HD",
    "UNIVERSAL CRIME HD", "UNIVERSAL PREMIERE HD", "UNIVERSAL PREMIERE O HD",
    "UNIVERSAL REALITY HD", "CINECANAL HD", "Cine Latino", "CineMax",
    "E! Entertairment HD", "Film & arts HD", "Golden",
    "HOLA! TV HD", "Home & Health HD", "Multipremier",
    "SPACE HD", "Star TVE HD", "WARNER HD",
    "FX HD i", "GOLDEN HD i", "GOLDEN EDGE SD i", "GOLDEN PREMIER HD i",
    "GOLDEN PREMIER 2HR HD i", "GOLDEN MULTIPLEX HD i",
    "LIFETIME HD i", "LIFETIME HD op2 i", "WARNER HD i", "WARNER HD op2 i",
    "MOSAICO HBO HD i", "HBO HD i", "HBO HD op2 i", "HBO HD op3 i",
    "HBO 2 HD i", "HBO 2 HD op2 i", "HBO 2 HD op3 i", "HBO 2 HD op4 i",
    "HBO FAMILY HD i", "HBO FAMILY HD op2 i", "HBO FAMILY HD op3 i",
    "HBO MUNDI HD i", "HBO MUNDI HD op2 i", "HBO MUNDI HD op3 i",
    "HBO PLUS HD i", "HBO PLUS HD op2 i", "HBO PLUS HD op3 i", "HBO PLUS HD op4 i",
    "HBO POP HD i", "HBO POP HD op2 i", "HBO POP HD op3 i",
    "Juego de tronos", "HBO SIGNATURE HD op2 i", "HBO SIGNATURE HD op3 i",
    "HBO XTREME HD i", "HBO XTREME HD op2 i", "HBO XTREME HD op3 i",
    "HERALDO TV HD i", "HERALDO TV HD op2 i", "HLN SD i", "HISTORY 2 HD i",
    "HISTORY CHANNEL HD i", "MTV HD i", "MTV HD op2 i", "MTV DANCE SD i",
    "MTV LIVE HD i", "MTV HITS SD i", "MTV HITS SD op2 i",
    "MUSIC BIG BAND i", "MUSIC BIG BAND op2 i", "MUSIC BLUES i",
    "MUSIC BLUES op2 i", "MUSIC CLASICOS DANCE i", "MUSIC CLASICOS DANCE op2 i",
    "MUSIC CLASICOS PARA TODOS i", "MUSIC CLASICOS PARA TODOS op2 i",
    "MUSIC CLASICOS SOUL i", "MUSIC CLASICOS SOUL op2 i",
    "MUSIC CLUB BAILE i", "MUSIC CLUB BAILE op2 i",
    "MUSIC DEL MUNDO i", "MUSIC DEL MUNDO op2 i",
    "MUSIC ESTANDARES i", "MUSIC ESTANDARES op2 i",
    "MUSIC EURO HITS i", "MUSIC EURO HITS op2 i",
    "MUSIC EXITOS AMERICAS i", "MUSIC EXITOS AMERICAS op2 i",
    "MUSIC EXITOS BRASIL i", "MUSIC EXITOS BRASIL op2 i",
    "MUSIC EXITOS ITALIA i", "MUSIC EXITOS ITALIA op2 i",
    "MUSIC EXITOS RECIENTES i", "MUSIC EXITOS RECIENTES op2 i",
    "MUSIC FIESTA CONTINUA i", "MUSIC FIESTA CONTINUA op2 i",
    "MUSIC HIMNOS ROCK i", "MUSIC HIMNOS ROCK op2 i",
    "MUSIC JAMMIN REGGAE i", "MUSIC JAMMIN REGGAE op2 i",
    "MUSIC JAZZ LATINO i", "MUSIC JAZZ LATINO op2 i",
    "MUSIC LATIN LOUNGE i", "MUSIC LATIN LOUNGE op2 i",
    "MUSIC LATINO TROPICAL i", "MUSIC LATINO TROPICAL op2 i",
    "MUSIC LIGERA i", "MUSIC LIGERA op2 i",
    "MUSIC MARIACHI PARA SIEMPRE i", "MUSIC MARIACHI PARA SIEMPRE op2 i",
    "MUSIC NEW AGE i", "MUSIC NEW AGE op2 i", "MUSIC POPCORN i",
    "MUSIC POP ADULTO i", "MUSIC POP LATINO ACTUAL i",
    "RT En Espanol (i)", "AMC HD (CO) (i)", "AXN FHD (i)", "A&E E (i)",
    "Comedy Central FHD. (i)", "E! Entertainment HD (i)",
    "El Gourmet Norte  (i)", "EUROPA EUROPA (i)", "FILM ARTS. (i)",
    "FX HD (i)", "Hola TV FHD (i)", "I-Sat (i)", "Lifetime HD (i)",
    "Pasion HD (@) (i)", "Star Channel FHD (MX)(i)", "SyFy HD. (i)",
    "Uni-versal Channel HD (i)", "Uni-versal Cinema HD (i)",
    "Cinecanal HD MEX k (i)", "De Peliculas Plus HD (i)",
    "FX HD (i) op2", "GOLDEN + MX (i)", "Golden Premier HD MX (i)",
    "PANICO FHD Mexico (i)", "Sony Cine HD (MX)(i)", "Space (i)",
    "Studio Uni-versal (i)", "History Channel FHD Mexico (i)",
    "Natgeo HD (i).", "NatGeo Wild FHD (i)", "NatGeo Mundo Lat HD (i)",
    "Sony HD (MX)(i)", "Az Cinema HD (MX)(i)", "Sony Cine FHD (MX)(i)",
    "NatGeo Wild HD.(i)", "Uni-versal Reality (MX)(i)",
    "H - v - O Xtreme (i)", "D - ery Tur HD (MX)(i)",
    "D - ery Tur FHD (MX)(i)", "C-Max (i)  op2", "T-N Series FHD (i)",
    "D - ery TL Latino HD (i)", "Warner Latino (i)",
    "D - ery en Espanol FHD (i)", "D - ery Fam Latino HD (i)",
    "D - ery HyH FHD (i)", "Discovery ID FHD (i)",
    "Discovery Science FHD (i)", "Discovery Theater FHD (i)",
    "Discovery Turbo FHD (i)", "D - ery Wo FHD (i)",
    "H - v - O + (i)", "H - v - O Family HD (i)", "H - v - O HD (i)",
    "H - v - O (i)", "Pasiones FHD (MX)(i)", "Food Network (i) op2",
    "H - v - O 2 HD (i)", "H - v - O Fam SD (i)", "H - v - O POP (i)",
    "D - ery Chan (MX)(i)", "D - ery Chan (MX)(i) op3",
    "H - v - O 2 (i) op2", "H - v - O Family HD (i) op2",
    "D-covery Chan (mx)(i) op2", "D-covery Chan (mx)(i) op4",
    "Star Channel HD (MX)(i)", "Star Channel HD op2 (MX)(i)",
    "Star Channel HD op3 (MX)(i)", "Star Channel HD op4 (MX)(i)",
    "Cine The Film Zone (i)", "Filmex Clasico (i)",
    "DW EN ESPANOL (MX)(P)", "EL FINANCIERO BLOOMBERG (MX)(P)",
    "FRANCE 24 (MX)(P)", "CNN ESPANOL (MX)(P)", "CNN INTERNACIONAL (MX)(P)",
    "RT ESPANOL (MX)(P)", "AXN (MX)(P)", "AXN HD (MX)(P)", "AXN LQ (MX)(P)",
    "A&E (MX)(P)", "A&E HD (MX)(P)", "A&E LQ (MX)(P)",
    "AdultSwim (MX)(P)", "AdultSwim HD (MX)(P)", "AMC (MX)(P)", "AMC HD (MX)(P)",
    "DISCOVERY HOME & HEALTH (MX)(P)", "DISCOVERY TURBO (MX)(P)",
    "HOLA TV (MX)(P)", "EUROPA EUROPA HD (MX)(P)", "FILM & ARTS (MX)(P)",
    "FOOD NETWORK (MX)(P)", "HTV (MX)(P)", "PASIONES HD (MX)(P)",
    "SONY (MX)(P)", "SONY HD (1080p) (MX)(P)", "TCM (MX)(P)",
    "Discovery TLC (MX)(P)", "TNT Novelas (MX)(P)",
    "COMEDY CENTRAL (MX)(P)", "COMEDY CENTRAL HD (MX)(P)",
    "DISCOVERY HOME & HEALTH HD (MX)(P)", "DISCOVERY HOME & HEALTH LQ (MX)(P)",
    "DISCOVERY TLC HD (MX)(P)", "DISCOVERY TURBO HD (MX)(P)",
    "E! Entertainment (MX)(P)", "E! ENTERTAINMENT HD (MX)(P)", "E! LQ (MX)(P)",
    "EL GOURMET (MX)(P)", "EL GOURMET HD (MX)(P)", "EL GOURMET LQ (MX)(P)",
    "EUROCHANNEL (MX)(P)", "FILM & ARTS HD (MX)(P)", "FOOD NETWORK LQ (MX)(P)",
    "FX (MX)(P)", "FX HD (MX)(P)", "FX LQ (MX)(P)",
    "HGTV (MX)(P)", "HGTV HD (MX)(P)", "HGTV LQ (MX)(P)",
    "LIFETIME (MX)(P)", "LIFETIME HD (MX)(P)", "LIFETIME LQ (MX)(P)",
    "PASIONES LQ (MX)(P)", "SONY LQ (MX)(P)",
    "STAR CHANNEL (MX)(P)", "STAR CHANNEL HD (MX)(P)", "STAR CHANNEL LQ (MX)(P)",
    "TLC LQ (MX)(P)", "TNT SERIES (MX)(P)", "TNT SERIES HD (MX)(P)",
    "TNT SERIES LQ (MX)(P)", "WARNER (MX)(P)", "WARNER HD (MX)(P)",
    "WARNER LQ (MX)(P)", "DE PELICULA (MX)(P)", "DE PELICULA + (MX)(P)",
    "DE PELICULA HD (1080p) (MX)(P)", "CINE LATINO (MX)(P)",
    "CINECANAL (MX)(P)", "CINECANAL HD (MX)(P)",
    "Azteca CINEMA (MX)(P)", "Azteca CINEMA HD (MX)(P)", "Azteca CINEMA LQ (MX)(P)",
    "CINEMAX (MX)(P)", "CINEMAX HD (MX)(P)", "De Pelicula Plus HD (MX)(P)",
    "SONY MOVIES (MX)(P)", "Universal Cinema HD (MX)(P)",
    "Universal Comedy (p)", "Universal Crime Este HD (MX)(P)",
    "Universal Crime Oeste HD (MX)(P)", "Universal Premier Este HD (MX)(P)",
    "Universal Premier Oeste HD (MX)(P)", "Universal Reality HD (MX)(P)",
    "GOLDEN (MX)(P)", "GOLDEN EDGE (MX)(P)", "Golden Edge HD (MX)(P)",
    "GOLDEN EDGE LQ (MX)(P)", "GOLDEN HD (MX)(P)", "GOLDEN PLUS HD (MX)(P)",
    "GOLDEN PLUS LQ (MX)(P)", "GOLDEN PREMIER HD (MX)(P)",
    "GOLDEN PREMIER LQ (MX)(P)", "HBO (MX)(P)", "HBO + (MX)(P)",
    "HBO + HD (MX)(P)", "HBO + LQ (MX)(P)", "HBO 2 (MX)(P)",
    "HBO 2 HD (MX)(P)", "HBO 2 LQ (MX)(P)", "HBO FAMILY (MX)(P)",
    "HBO FAMILY HD (MX)(P)", "HBO FAMILY LQ (MX)(P)", "HBO HD (MX)(P)",
    "HBO LQ (MX)(P)", "HBO MUNDI (MX)(P)", "HBO MUNDI HD (MX)(P)",
    "HBO POP (MX)(P)", "HBO POP HD (MX)(P)", "HBO SIGNATURE (MX)(P)",
    "HBO SIGNATURE HD (MX)(P)", "HBO SIGNATURE LQ (MX)(P)",
    "HBO XTREME (MX)(P)", "HBO XTREME HD (MX)(P)",
    "MULTIPREMIER  HD (MX)(P)", "PANICO HD (MX)(P)",
    "PARAMOUNT (MX)(P)", "PARAMOUNT HD (MX)(P)", "PARAMOUNT LQ (MX)(P)",
    "SPACE (MX)(P)", "SPACE HD (MX)(P)", "STUDIO UNIVERSAL (MX)(P)",
    "STUDIO UNIVERSAL HD (MX)(P)", "TNT HD (MX)(P)",
    "CINE LATINO LQ (MX)(P)", "DISCOVERY CHANNEL (MX)(P)",
    "DISCOVERY CHANNEL HD (MX)(P)", "DISCOVERY CHANNEL LQ (MX)(P)",
    "DISCOVERY SCIENCE (MX)(P)", "DISCOVERY THEATER (MX)(P)",
    "DISCOVERY THEATER HD (MX)(P)", "DISCOVERY WORLD (MX)(P)",
    "DISCOVERY WORLD HD (MX)(P)", "DISCOVERY WORLD LQ (MX)(P)",
    "HISTORY (MX)(P)", "HISTORY 2 (MX)(P)", "HISTORY HD (1080p) (MX)(P)",
    "HISTORY LQ (MX)(P)", "INVESTIGATION DISCOVERY (MX)(P)",
    "INVESTIGATION DISCOVERY HD (MX)(P)", "INVESTIGATION DISCOVERY LQ (MX)(P)",
    "NATGEO (MX)(P)", "NATGEO HD (MX)(P)", "NATGEO LQ (MX)(P)",
    "Bob Esponja (Pluto)(i)", "Comedy Central Latino (Pluto)(i)",
    "El Reino Infantil (i)", "MTV Embarazada a los 16 (Pluto)(i)",
    "MTV Latino (Pluto)(i)", "MTV Tattoo A Dos (Pluto)(i)",
    "Nick Clásico (Pluto)(i)", "Turma da Mônica (Pluto)(i)",
    "History i", "Love Nature I", "Travelxp HD I", "Euronews I",
    "Pasiones HD I", "Cinelatino I", "KANAL D Drama HD I", "Food Network HD I",
}

# Categorías que se conservan sin filtrar
KEEP_ALL_CATEGORIES = {
    "Deportes",       # filtrado por patrones (ver función abajo)
    "Anime y Animación",
    "Adultos (XXX)",
    "Reality",
    "Canales 24/7",   # filtrado por DELETE_247
}

# Mapa categoría -> conjunto de nombres a conservar
KEEP_BY_CATEGORY = {
    "Argentina":       KEEP_ARGENTINA,
    "Entretenimiento": KEEP_ENTRETENIMIENTO,
    "TV Premium":      KEEP_TV_PREMIUM,
    "Música":          KEEP_MUSICA,
    "Noticias":        KEEP_NOTICIAS,
    "Infantil":        KEEP_INFANTIL,
    "Documentales":    KEEP_DOCUMENTALES,
}

# ---------------------------------------------------------------------------
# FUNCIÓN DE FILTRO PARA DEPORTES (basada en patrones)
# ---------------------------------------------------------------------------

def keep_deportes(name):
    n = name.lower().strip()
    exact = {"dazn women's football", "on football", "football", "tnt sport"}
    if n in exact:
        return True
    patterns = [
        "da-n ", "sky la liga", "sky bundesliga", "fifa+", "es-pn",
        "espn", "foxs", "fox sport", "fox deportes", "tyc",
        "directv sports", "sky sports f1", "sky sport calcio",
        "nba tv", "nba u ", "tennis channel", "ppv ",
    ]
    for p in patterns:
        if p in n:
            return True
    if n.startswith("arg ") and any(x in n for x in ("espn", "fox", "tyc")):
        return True
    if n.startswith("mex ") and any(x in n for x in ("espn", "fox")):
        return True
    return False

# ---------------------------------------------------------------------------
# PROCESAMIENTO
# ---------------------------------------------------------------------------

def process(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    stats = {}
    seen_urls = {}  # category -> set of urls (dedup per category)
    i = 0

    while i < len(lines):
        line = lines[i]

        if line.startswith('#EXTINF'):
            m = re.search(r'group-title="([^"]+)"', line)
            category = m.group(1) if m else ''
            lc = line.rfind(',')
            name = line[lc+1:].strip() if lc != -1 else ''
            url_line = lines[i+1] if i + 1 < len(lines) and not lines[i+1].startswith('#') else None
            url = url_line.strip() if url_line else None

            if category not in stats:
                stats[category] = {'kept': 0, 'deleted': 0}
            if category not in seen_urls:
                seen_urls[category] = set()

            # Decidir si conservar
            keep = False

            if category in DELETE_CATEGORIES:
                keep = False
            elif category == "Deportes":
                keep = keep_deportes(name)
            elif category == "Canales 24/7":
                keep = name not in DELETE_247
            elif category in KEEP_BY_CATEGORY:
                keep = name in KEEP_BY_CATEGORY[category]
            else:
                keep = True  # categorías no configuradas se conservan

            # Deduplicar por URL
            if keep and url and url in seen_urls[category]:
                keep = False  # duplicado

            if keep:
                stats[category]['kept'] += 1
                if url:
                    seen_urls[category].add(url)
                new_lines.append(line)
                if url_line:
                    new_lines.append(url_line)
                    i += 1
            else:
                stats[category]['deleted'] += 1
                if url_line:
                    i += 1
        else:
            new_lines.append(line)

        i += 1

    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    # Resumen
    total_kept = sum(v['kept'] for v in stats.values())
    total_deleted = sum(v['deleted'] for v in stats.values())
    print(f"\n{'Categoría':<30} {'Conservados':>12} {'Eliminados':>12}")
    print("-" * 56)
    for cat in sorted(stats):
        k = stats[cat]['kept']
        d = stats[cat]['deleted']
        print(f"{cat:<30} {k:>12} {d:>12}")
    print("-" * 56)
    print(f"{'TOTAL':<30} {total_kept:>12} {total_deleted:>12}")
    print(f"\nArchivo guardado: {output_file}")

# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    input_file  = sys.argv[1] if len(sys.argv) > 1 else 'lista_unificada.m3u'
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file
    process(input_file, output_file)
