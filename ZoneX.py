import pygame
import random
import colorsys
import time

# Initialisierung
pygame.init()
pygame.mixer.init()  # Initialisierung des Soundsystems

raster_groesse = 32
raster_breite, raster_hoehe = 30, 20
breite, hoehe = raster_breite * raster_groesse, raster_hoehe * raster_groesse
bildschirm = pygame.display.set_mode((breite, hoehe))
pygame.display.set_caption("Boulder Dash")

# Farben
SCHWARZ = (0, 0, 0)
WEISS = (255, 255, 255)
ROT = (255, 0, 0)
BLAU = (0, 0, 255)
GELB = (255, 255, 0)
LILA = (128, 0, 128)
GRAU = (128, 128, 128)

# Grafiken laden
wand_bild = pygame.image.load("wand.jpg")
wand_bild = pygame.transform.scale(wand_bild, (raster_groesse, raster_groesse))
spieler_bild = pygame.image.load("player.jpg")
spieler_bild = pygame.transform.scale(spieler_bild, (raster_groesse, raster_groesse))
zeit_bild = pygame.image.load("diamand.jpg")  # Wir verwenden weiterhin das Diamanten-Bild für Zeit-Elemente
zeit_bild = pygame.transform.scale(zeit_bild, (raster_groesse, raster_groesse))
tonne_bild = pygame.image.load("tonne.jpg")
tonne_bild = pygame.transform.scale(tonne_bild, (raster_groesse, raster_groesse))
plutonium_bild = pygame.image.load("plutonium.jpg")
plutonium_bild = pygame.transform.scale(plutonium_bild, (raster_groesse, raster_groesse))
save_bild = pygame.image.load("save.jpg")  # Neues Bild für die sichere Position
save_bild = pygame.transform.scale(save_bild, (raster_groesse, raster_groesse))
matte_bild = pygame.image.load("matt.jpg")  # Neues Bild für die Matte
matte_bild = pygame.transform.scale(matte_bild, (raster_groesse, raster_groesse))

# Soundeffekte laden
diamant_sound = pygame.mixer.Sound("diamant.mp3")
wand_sound = pygame.mixer.Sound("wand.mp3")
tot_sound = pygame.mixer.Sound("dead.mp3")
gameover_sound = pygame.mixer.Sound("gameover.mp3")
gamestart_sound = pygame.mixer.Sound("gamestart.mp3")
move_sound = pygame.mixer.Sound("move.mp3")
timer_sound = pygame.mixer.Sound("timer.mp3")
plutonium_sound = pygame.mixer.Sound("plutonium.mp3")
tonne_sound = pygame.mixer.Sound("tonne.mp3")
drama_sound = pygame.mixer.Sound("drama.mp3")
matt_sound = pygame.mixer.Sound("matt.mp3")

# Aktueller Sound
aktueller_sound = None

# Funktion zum Abspielen von Sounds
def play_sound(sound):
    sound.play()

# Globale Variablen
aktuelles_level = 1
benoetigte_plutonium = 2  # Startwert, wird mit jedem Level erhöht
zeit_elemente = []  # Umbenannt von diamanten zu zeit_elemente
gegner = []
waende = []
plutonium = None
tonne = None
punkte = 0
leben = 5
spieler_geschwindigkeit = 4  # Geschwindigkeit des Spielers (muss ein Teiler von raster_groesse sein)
timer = 10  # Startwert, wird mit jedem Level erhöht
timer_aktiv = False
gesammelte_plutonium = 0
matten = []  # Liste für die platzierten Matten
verfuegbare_matten = 9  # Startanzahl der verfügbaren Matten
sichere_position = None

# Kollisionserkennung
def kollision(rect1, rect2):
    return rect1[0] < rect2[0] + rect2[2] and rect1[0] + rect1[2] > rect2[0] and rect1[1] < rect2[1] + rect2[3] and rect1[1] + rect1[3] > rect2[1]

# Funktion zum Finden einer sicheren Position
def finde_sichere_position():
    global sichere_position, gegner
    moegliche_positionen = []
    for x in range(0, breite, raster_groesse):
        for y in range(0, hoehe, raster_groesse):
            if not kollision_mit_objekten(x, y) and all(abs(x - g[0]) > raster_groesse or abs(y - g[1]) > raster_groesse for g in gegner):
                moegliche_positionen.append((x, y))
    if moegliche_positionen:
        sichere_position = random.choice(moegliche_positionen)
    else:
        # Fallback, falls keine sichere Position gefunden wird
        sichere_position = (0, 0)

# Funktion zur Überprüfung der Kollision mit allen Objekten
def kollision_mit_objekten(x, y):
    global tonne, sichere_position  # Füge sichere_position hinzu
    # Kollision mit Wänden
    if any(kollision([x, y, raster_groesse, raster_groesse], [w[0], w[1], raster_groesse, raster_groesse]) for w in waende):
        return True
    # Kollision mit Zeit-Elementen
    if any(kollision([x, y, raster_groesse, raster_groesse], [z[0], z[1], raster_groesse, raster_groesse]) for z in zeit_elemente):
        return True
    # Kollision mit Tonne
    if tonne and kollision([x, y, raster_groesse, raster_groesse], [tonne[0], tonne[1], raster_groesse, raster_groesse]):
        return True
    # Kollision mit sicherer Position
    if sichere_position and kollision([x, y, raster_groesse, raster_groesse], [sichere_position[0], sichere_position[1], raster_groesse, raster_groesse]):
        return True
    # Kollision mit Spielfeldrand
    if x < 0 or x >= breite or y < 0 or y >= hoehe:
        return True
    # Kollision mit Matten
    if (x, y) in matten:
        return True
    return False

# Funktion zum Entfernen von Gegnern in der Nähe des Spielers
def entferne_nahe_gegner(spieler_x, spieler_y):
    global gegner
    gegner = [g for g in gegner if not (g[0] // raster_groesse == spieler_x // raster_groesse or 
                                        g[1] // raster_groesse == spieler_y // raster_groesse)]

# Funktion zum Neustart des Levels
def level_neustart():
    global spieler_x, spieler_y, spieler_ziel_x, spieler_ziel_y, spieler_richtung, zeit_elemente, gegner, waende, plutonium, tonne, punkte, timer, timer_aktiv, gesammelte_plutonium, benoetigte_plutonium, sichere_position
    
    # Initialisiere die Spielobjekte
    waende = []
    zeit_elemente = []
    gegner = []
    tonne = None
    plutonium = None

    # Spieler
    finde_sichere_position()
    spieler_x, spieler_y = spieler_ziel_x, spieler_ziel_y = sichere_position
    spieler_richtung = None

    # Zeit-Elemente
    for _ in range(aktuelles_level * 3):  # Anzahl der Zeit-Elemente ist nun level * 3
        position = generiere_position([z[:2] for z in zeit_elemente])
        zeit_elemente.append(position)

    # Wände
    for _ in range(40 * aktuelles_level):  # Anzahl der Wände verdoppelt sich pro Level
        position = generiere_position([z[:2] for z in zeit_elemente] + waende)
        waende.append(position)

    # Gegner
    for _ in range(aktuelles_level * 6):  # Anzahl der Gegner verdoppelt sich pro Level
        position = generiere_position([z[:2] for z in zeit_elemente] + waende + [g[:2] for g in gegner])
        gegner.append(list(position) + [random.choice(["rechts", "links", "oben", "unten"]), 2, position[0], position[1]])

    # Entferne Gegner in der Nähe des Spielers
    entferne_nahe_gegner(spieler_x, spieler_y)

    # Generiere Tonne und Plutonium
    tonne = generiere_position([z[:2] for z in zeit_elemente] + waende + [g[:2] for g in gegner])
    plutonium = generiere_position([z[:2] for z in zeit_elemente] + waende + [g[:2] for g in gegner] + [tonne])

    # Timer und Plutonium-Zähler zurücksetzen
    timer = aktuelles_level * 5
    timer_aktiv = False
    gesammelte_plutonium = 0
    benoetigte_plutonium = aktuelles_level * 2

    # Zeige Spieler, Tonne und Plutonium für 2 Sekunden
    zeige_level_start()

    # Spiele den Gamestart-Sound
    play_sound(gamestart_sound)

# Funktion zum Anzeigen des Levelstarts
def zeige_level_start():
    bildschirm.fill(SCHWARZ)
    
    # Spieler zeichnen
    bildschirm.blit(spieler_bild, (spieler_x, spieler_y))

    # Plutonium zeichnen
    if plutonium:
        bildschirm.blit(plutonium_bild, (plutonium[0], plutonium[1]))

    # Tonne zeichnen
    bildschirm.blit(tonne_bild, (tonne[0], tonne[1]))

    # Level-Anzeige mit 30% Transparenz
    schrift = pygame.font.Font(None, 72)
    level_text = schrift.render(f"Level {aktuelles_level}", True, WEISS)
    level_text.set_alpha(int(255 * 0.7))  # 70% Deckkraft = 30% Transparenz
    text_rect = level_text.get_rect(center=(breite // 2, hoehe // 2))
    bildschirm.blit(level_text, text_rect)

    pygame.display.flip()
    pygame.time.wait(2000)  # Warte 2 Sekunden

# Funktion zum Zurücksetzen des Timers und Neupositionieren des Plutoniums
def reset_timer_und_plutonium():
    global timer, timer_aktiv, plutonium, plutonium_blink_start, gesammelte_plutonium
    timer = aktuelles_level * 10
    timer_aktiv = False
    plutonium = generiere_position([z[:2] for z in zeit_elemente] + waende + [g[:2] for g in gegner] + [tonne])
    plutonium_blink_start = time.time()  # Starte das Blinken des Plutoniums

# Funktion zur Bestimmung der nächsten Richtung
def naechste_zufaellige_richtung():
    return random.choice(["rechts", "links", "oben", "unten"])

# Funktion zum Anzeigen des Game Over Textes und Abspielen des Sounds
def zeige_game_over():
    schrift = pygame.font.Font(None, 72)
    game_over_text = schrift.render("GAME OVER", True, WEISS)
    text_rect = game_over_text.get_rect(center=(breite // 2, hoehe // 2))
    bildschirm.blit(game_over_text, text_rect)
    pygame.display.flip()
    
    # Spiele den Game Over Sound
    gameover_sound.play()
    
    # Warte, bis der Sound fertig ist (maximal 5 Sekunden)
    pygame.time.wait(min(5000, int(gameover_sound.get_length() * 1000)))

# Funktion zum Generieren einer zufälligen Position
def generiere_position(besetzte_positionen):
    while True:
        x = random.randint(0, (breite - raster_groesse) // raster_groesse) * raster_groesse
        y = random.randint(0, (hoehe - raster_groesse) // raster_groesse) * raster_groesse
        if (x, y) not in besetzte_positionen:
            return (x, y)

# Lade das Cover-Bild
cover_bild = pygame.image.load("cover.jpg")
cover_bild = pygame.transform.scale(cover_bild, (breite, hoehe))

# Funktion zum Anzeigen des Cover-Bildes
def zeige_cover():
    bildschirm.blit(cover_bild, (0, 0))
    pygame.display.flip()
    time.sleep(2)

# Zeige Cover zu Beginn des Spiels
zeige_cover()

# Initialisiere das erste Level
level_neustart()

# Farbanimation für Gegner
farb_offset = 0
farb_geschwindigkeit = 0.1  # Erhöhen Sie diesen Wert für eine schnellere Animation

# Funktion zur Generierung der aktuellen Farbe
def get_regenbogen_farbe(offset):
    r, g, b = colorsys.hsv_to_rgb((offset % 1), 1.0, 1.0)
    return (int(r * 255), int(g * 255), int(b * 255))

# Funktion zur Bestimmung der entgegengesetzten Richtung
def umkehrrichtung(richtung):
    if richtung == "rechts":
        return "links"
    elif richtung == "links":
        return "rechts"
    elif richtung == "oben":
        return "unten"
    elif richtung == "unten":
        return "oben"

# Funktion zur Platzierung einer Matte
def platziere_matte(x, y, richtung):
    global verfuegbare_matten
    if verfuegbare_matten > 0:
        if richtung == "rechts":
            matte_pos = (x - raster_groesse, y)
        elif richtung == "links":
            matte_pos = (x + raster_groesse, y)
        elif richtung == "oben":
            matte_pos = (x, y + raster_groesse)
        elif richtung == "unten":
            matte_pos = (x, y - raster_groesse)
        else:
            return  # Keine Matte platzieren, wenn keine Richtung angegeben ist

        if matte_pos not in matten and not kollision_mit_objekten(*matte_pos):
            matten.append(matte_pos)
            verfuegbare_matten -= 1
            matt_sound.play()

# Funktion zum Aufsammeln einer Matte
def sammle_matte(x, y):
    global verfuegbare_matten
    matte_pos = (x, y)
    if matte_pos in matten:
        matten.remove(matte_pos)
        verfuegbare_matten += 1
        matt_sound.play()

# Funktion zum Verlieren eines Lebens
def verliere_leben():
    global leben, spieler_x, spieler_y, spieler_ziel_x, spieler_ziel_y, spieler_richtung, gesammelte_plutonium
    leben -= 1
    play_sound(tot_sound)
    finde_sichere_position()
    spieler_x, spieler_y = spieler_ziel_x, spieler_ziel_y = sichere_position
    spieler_richtung = None
    
    if timer_aktiv:
        gesammelte_plutonium += 1
        reset_timer_und_plutonium()

# Hauptspielschleife
laueft = True
uhr = pygame.time.Clock()
letzter_rasterpunkt = (spieler_x, spieler_y)
letzter_timer_update = time.time()
plutonium_blink_start = None

while laueft:
    for ereignis in pygame.event.get():
        if ereignis.type == pygame.QUIT:
            laueft = False
        elif ereignis.type == pygame.KEYDOWN:
            if ereignis.key == pygame.K_SPACE:
                platziere_matte(spieler_x, spieler_y, spieler_richtung)

    # Spielerbewegung und Mattenaufsammeln
    if spieler_x == spieler_ziel_x and spieler_y == spieler_ziel_y:
        sammle_matte(spieler_x, spieler_y)
        tasten = pygame.key.get_pressed()
        neue_ziel_x, neue_ziel_y = spieler_x, spieler_y
        neue_richtung = None

        if tasten[pygame.K_LEFT] and spieler_x > 0:
            neue_ziel_x -= raster_groesse
            neue_richtung = "links"
        elif tasten[pygame.K_RIGHT] and spieler_x < breite - raster_groesse:
            neue_ziel_x += raster_groesse
            neue_richtung = "rechts"
        elif tasten[pygame.K_UP] and spieler_y > 0:
            neue_ziel_y -= raster_groesse
            neue_richtung = "oben"
        elif tasten[pygame.K_DOWN] and spieler_y < hoehe - raster_groesse:
            neue_ziel_y += raster_groesse
            neue_richtung = "unten"

        # Überprüfe Kollision mit Wänden
        if not any(kollision([neue_ziel_x, neue_ziel_y, raster_groesse, raster_groesse], [w[0], w[1], raster_groesse, raster_groesse]) for w in waende):
            if neue_ziel_x != spieler_x or neue_ziel_y != spieler_y:  # Nur wenn sich die Position ändert
                spieler_ziel_x, spieler_ziel_y = neue_ziel_x, neue_ziel_y
                spieler_richtung = neue_richtung
                play_sound(move_sound)

    else:
        if spieler_richtung == "links":
            spieler_x = max(spieler_ziel_x, spieler_x - spieler_geschwindigkeit)
        elif spieler_richtung == "rechts":
            spieler_x = min(spieler_ziel_x, spieler_x + spieler_geschwindigkeit)
        elif spieler_richtung == "oben":
            spieler_y = max(spieler_ziel_y, spieler_y - spieler_geschwindigkeit)
        elif spieler_richtung == "unten":
            spieler_y = min(spieler_ziel_y, spieler_y + spieler_geschwindigkeit)
        
        # Überprüfe, ob der Spieler einen neuen Rasterpunkt erreicht hat
        aktueller_rasterpunkt = (spieler_x // raster_groesse * raster_groesse, 
                                 spieler_y // raster_groesse * raster_groesse)
        if aktueller_rasterpunkt != letzter_rasterpunkt:
            play_sound(move_sound)
            letzter_rasterpunkt = aktueller_rasterpunkt

    # Kollisionsprüfung für Zeit-Elemente
    for zeit in zeit_elemente[:]:
        if kollision([spieler_x, spieler_y, raster_groesse, raster_groesse], [zeit[0], zeit[1], raster_groesse, raster_groesse]):
            zeit_elemente.remove(zeit)
            punkte += 1
            timer += 1  # Timer um 1 erhöhen
            play_sound(diamant_sound)

    # Kollisionsprüfung für Tonne
    if kollision([spieler_x, spieler_y, raster_groesse, raster_groesse], [tonne[0], tonne[1], raster_groesse, raster_groesse]):
        if timer_aktiv:
            punkte += 10
            gesammelte_plutonium += 1
            play_sound(tonne_sound)
            reset_timer_und_plutonium()
            if gesammelte_plutonium >= benoetigte_plutonium:
                # Level abgeschlossen
                aktuelles_level += 1
                level_neustart()
                play_sound(gamestart_sound)

    # Kollisionsprüfung für Plutonium
    if plutonium and kollision([spieler_x, spieler_y, raster_groesse, raster_groesse], [plutonium[0], plutonium[1], raster_groesse, raster_groesse]):
        plutonium = None
        timer_aktiv = True
        letzter_timer_update = time.time()
        play_sound(plutonium_sound)

    # Timer-Logik
    if timer_aktiv:
        aktueller_zeit = time.time()
        if aktueller_zeit - letzter_timer_update >= 1:
            timer -= 1
            letzter_timer_update = aktueller_zeit
            play_sound(timer_sound)
            if timer <= 0:
                play_sound(drama_sound)  # Spiele den Drama-Sound ab
                verliere_leben()
                if leben <= 0:
                    zeige_game_over()
                    play_sound(gameover_sound)
                    laueft = False

    # Gegnerbewegung
    for g in gegner:
        if (g[0], g[1]) == (g[4], g[5]):  # Wenn der Gegner einen Rasterpunkt erreicht hat
            # Suche nach einer freien Richtung
            versuche = 0
            while versuche < 10:
                if g[2] == "rechts":
                    naechster_x, naechster_y = g[0] + raster_groesse, g[1]
                elif g[2] == "links":
                    naechster_x, naechster_y = g[0] - raster_groesse, g[1]
                elif g[2] == "unten":
                    naechster_x, naechster_y = g[0], g[1] + raster_groesse
                else:  # oben
                    naechster_x, naechster_y = g[0], g[1] - raster_groesse

                if not kollision_mit_objekten(naechster_x, naechster_y):
                    g[4], g[5] = naechster_x, naechster_y  # Setze neues Ziel
                    break
                else:
                    g[2] = umkehrrichtung(g[2])  # Kehre um bei Kollision
                    versuche += 1

            if versuche == 10:  # Wenn kein freier Weg gefunden wurde, pausiere
                g[4], g[5] = g[0], g[1]

        # Bewege den Gegner in Richtung des Zielpunkts
        if g[0] < g[4]:
            g[0] = min(g[0] + g[3], g[4])
        elif g[0] > g[4]:
            g[0] = max(g[0] - g[3], g[4])
        if g[1] < g[5]:
            g[1] = min(g[1] + g[3], g[5])
        elif g[1] > g[5]:
            g[1] = max(g[1] - g[3], g[5])
        
        # Kollision mit Spieler
        if kollision([spieler_x, spieler_y, raster_groesse, raster_groesse], [g[0], g[1], raster_groesse, raster_groesse]):
            verliere_leben()
            if leben <= 0:
                zeige_game_over()
                play_sound(gameover_sound)
                laueft = False
                break

    # Prüfen, ob das Spiel vorbei ist (außerhalb der Gegnerschleife)
    if leben <= 0:
        break

    # Bildschirm leeren
    bildschirm.fill(SCHWARZ)

    # Zeichne die sichere Position
    if sichere_position:
        bildschirm.blit(save_bild, (sichere_position[0], sichere_position[1]))

    # Wände zeichnen
    for wand in waende:
        bildschirm.blit(wand_bild, (wand[0], wand[1]))

    # Zeit-Elemente zeichnen
    for zeit in zeit_elemente:
        bildschirm.blit(zeit_bild, (zeit[0], zeit[1]))

    # Gegner zeichnen mit Farbanimation
    for i, g in enumerate(gegner):
        farbe = get_regenbogen_farbe(farb_offset + i * 0.1)  # Unterschiedliche Farben für jeden Gegner
        pygame.draw.rect(bildschirm, farbe, (g[0], g[1], raster_groesse, raster_groesse))
    
    # Farboffset aktualisieren
    farb_offset += farb_geschwindigkeit
    if farb_offset > 1:
        farb_offset -= 1

    # Plutonium zeichnen (blinkend, wenn neu gesetzt)
    if plutonium:
        if plutonium_blink_start and time.time() - plutonium_blink_start < 2:
            if int(time.time() * 4) % 2 == 0:  # Blinken mit 4 Hz
                bildschirm.blit(plutonium_bild, (plutonium[0], plutonium[1]))
        else:
            bildschirm.blit(plutonium_bild, (plutonium[0], plutonium[1]))
            plutonium_blink_start = None

    # Tonne zeichnen
    bildschirm.blit(tonne_bild, (tonne[0], tonne[1]))

    # Matten zeichnen
    for matte in matten:
        bildschirm.blit(matte_bild, (matte[0], matte[1]))

    # Spieler zuletzt zeichnen, damit er über allen anderen Elementen erscheint
    bildschirm.blit(spieler_bild, (spieler_x, spieler_y))

    # Informationen anzeigen mit 30% Transparenz
    schrift = pygame.font.Font(None, 36)
    info_texte = [
        f"Level: {aktuelles_level}",
        f"Plutonium: {gesammelte_plutonium}/{benoetigte_plutonium}",
        f"Punkte: {punkte}",
        f"Timer: {timer}",
        f"Leben: {leben}",
        f"Matten: {verfuegbare_matten}"
    ]
    for i, text in enumerate(info_texte):
        info_surface = schrift.render(text, True, WEISS)
        info_surface.set_alpha(int(255 * 0.7))  # 70% Deckkraft = 30% Transparenz
        bildschirm.blit(info_surface, (10, 10 + i * 40))

    # Anzeige aktualisieren
    pygame.display.flip()

    # Framerate begrenzen
    uhr.tick(60)

# Zeige Cover am Ende des Spiels
zeige_cover()

# Nach dem Spielende
if leben <= 0:
    zeige_game_over()

pygame.quit()
