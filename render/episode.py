# -*- coding: utf-8 -*-
"""NACHTGLAS 1.01 — the single timeline.

Both the picture renderer (video.py) and the score/sound renderer (audio.py)
read this file, so sound and image can never drift apart.

A scene has a location and a list of beats:
    ("d", speaker, german_line [, fx])   spoken beat; duration from text length
    ("a", seconds, caption_or_None [, fx])  action beat

fx is an optional dict:
    cam      static | push | pull | pan_l | pan_r | crane | handheld | descend
    lamps    list of per-lantern brightness 0..1  (overrides the location default)
    lo       Loescher x-position 0..1 across frame, or None
    vision   True -> the marble-vision optical treatment
    flash    "flare" | "ignite" | "black"
    figs     list of (character_key, x 0..1, scale)
"""

CHARS = {
    "JUNO":   {"col": (214, 106, 54),  "build": "small"},
    "TAREK":  {"col": (218, 176, 70),  "build": "tall"},
    "NELL":   {"col": (74, 122, 92),   "build": "parka"},
    "BASTI":  {"col": (66, 96, 156),   "build": "broad"},
    "KOSTA":  {"col": (86, 104, 122),  "build": "heavy"},
    "PEPE":   {"col": (196, 62, 52),   "build": "child"},
    "ELIF":   {"col": (150, 108, 168), "build": "small"},
    "ILVA":   {"col": (206, 160, 60),  "build": "adult"},
    "KATRIN": {"col": (120, 124, 132), "build": "adult"},
    "ODA":    {"col": (176, 172, 160), "build": "adult"},
    "BERINGER": {"col": (140, 132, 120), "build": "adult"},
    "DIESING":  {"col": (120, 112, 100), "build": "adult"},
    "FUNK":   {"col": (120, 140, 150), "build": "adult"},
}

# ---------------------------------------------------------------------------

SCENES = [

# ============================ COLD OPEN ====================================
dict(id=1, loc="valley", slug="EXT. HOLLERBRUNN — TALKESSEL — NACHT · 23:38", beats=[
    ("a", 7.0, None, dict(cam="descend", fade_in=2.5)),
    ("a", 6.0, None, dict(cam="descend")),
    ("a", 5.5, None, dict(cam="descend", lamps_out=[0])),
    ("a", 4.5, None, dict(cam="descend", lamps_out=[0, 1, 2])),
]),

dict(id=2, loc="bypass", slug="EXT. BUNDESSTRASSE — NACHT · 23:41", beats=[
    ("a", 4.0, None, dict(cam="static", figs=[("KOSTA", 0.30, 1.0)])),
    ("a", 3.5, None, dict(cam="push", figs=[("KOSTA", 0.30, 1.0)])),
    ("d", "KOSTA", "Ey. Was soll'n das jetzt.", dict(figs=[("KOSTA", 0.30, 1.0)])),
    ("a", 3.0, None, dict(cam="static", lamps_out=[5])),
    ("a", 2.6, None, dict(cam="static", lamps_out=[4, 5])),
    ("a", 2.6, None, dict(cam="push", lamps_out=[3, 4, 5])),
    ("a", 3.0, None, dict(cam="push", lamps_out=[2, 3, 4, 5])),
    ("a", 3.4, None, dict(cam="static", lamps_out=[1, 2, 3, 4, 5], collapse=True)),
    ("a", 4.0, None, dict(cam="push", lamps_out=[0, 1, 2, 3, 4, 5], lo=0.50, collapse=True)),
    ("d", "KOSTA", "Nee. Nee, nee, nee —",
     dict(lamps_out=[0, 1, 2, 3, 4, 5], lo=0.50, collapse=True, figs=[("KOSTA", 0.30, 1.0)])),
    ("a", 3.2, "HANDYDISPLAY: eine leere Straße.",
     dict(cam="static", lamps_out=[0, 1, 2, 3, 4, 5], collapse=True)),
    ("a", 2.0, None, dict(cam="static", lamps_out=[0, 1, 2, 3, 4, 5], lo=0.50, collapse=True)),
    ("a", 2.6, None, dict(cam="static", lamps_out=[0, 1, 2, 3, 4, 5], lo=0.50, lo_near=True,
                          collapse=True, blink=True)),
    ("a", 3.0, None, dict(cam="handheld", lamps_out=[0, 1, 2, 3, 4, 5], flash="engine")),
    ("a", 5.0, None, dict(cam="static", lamps_in=True)),
    ("a", 3.0, None, dict(cam="static")),
]),

# ============================ MAIN TITLE ===================================
dict(id=0, loc="title", slug=None, beats=[
    ("a", 3.0, None, dict(t="gather")),
    ("a", 4.0, None, dict(t="gather")),
    ("a", 3.0, None, dict(t="globe")),
    ("a", 2.4, None, dict(t="face", who="JUNO")),
    ("a", 2.4, None, dict(t="face", who="TAREK")),
    ("a", 2.4, None, dict(t="face", who="NELL")),
    ("a", 2.4, None, dict(t="face", who="BASTI")),
    ("a", 2.6, None, dict(t="face", who="KOSTA")),
    ("a", 4.0, None, dict(t="cool")),
    ("a", 2.4, None, dict(t="fog")),
    ("a", 6.0, None, dict(t="crack")),
    ("a", 3.4, None, dict(t="hold")),
]),

# ============================== ACT ONE ====================================
dict(id=3, loc="markt", slug="EXT. MARKTPLATZ HOLLERBRUNN — MORGEN", act="AKT EINS", beats=[
    ("a", 4.5, None, dict(cam="pan_r", fade_in=1.2)),
    ("a", 3.5, None, dict(cam="push")),
    ("d", "KATRIN", "…und mit der neunten Laterne ist der Marktplatz offiziell umgerüstet."),
    ("d", "KATRIN", "Sechzig Prozent weniger Energie. Doppelt so hell."),
    ("a", 2.6, None, dict(cam="pan_l")),
    ("d", "DIESING", "Hundertelf. Es sind hundertelf. Steht so in der Satzung."),
    ("d", "KATRIN", "Ganz genau, Herr Diesing."),
    ("a", 4.0, "Ilva legt die alte Glaskugel ins Stroh. Neun Kisten.", dict(cam="push")),
]),

dict(id=4, loc="markt", slug="EXT. MARKTPLATZ — WEITER", beats=[
    ("a", 2.6, None, dict(cam="handheld", figs=[("JUNO", 0.40, 1.0), ("TAREK", 0.58, 1.06)])),
    ("d", "TAREK", "Sag was fürs Archiv.", dict(figs=[("JUNO", 0.40, 1.0), ("TAREK", 0.58, 1.06)])),
    ("d", "JUNO", "Nein.", dict(figs=[("JUNO", 0.40, 1.0), ("TAREK", 0.58, 1.06)])),
    ("d", "JUNO", "Deine Folge vierzig hatten elf Hörer, Tarek.",
     dict(figs=[("JUNO", 0.40, 1.0), ("TAREK", 0.58, 1.06)])),
    ("d", "TAREK", "Zwölf.", dict(figs=[("JUNO", 0.40, 1.0), ("TAREK", 0.58, 1.06)])),
    ("d", "JUNO", "Deine Oma zählt nicht doppelt, nur weil sie zweimal einschläft.",
     dict(figs=[("JUNO", 0.40, 1.0), ("TAREK", 0.58, 1.06)])),
    ("a", 3.0, None, dict(cam="push")),
    ("d", "ILVA", "Juno."),
    ("d", "JUNO", "Es ist kaputt!"),
    ("d", "ILVA", "Es ist städtisch kaputt."),
    ("d", "JUNO", "Mama. Bitte."),
    ("a", 3.6, "Pale blue-green. Und es hält das Licht ein bisschen fest.", dict(cam="push")),
    ("d", "TAREK", "Ja, Murmel, hab ich auch, hat jeder. Pepe hat vierzig."),
    ("a", 3.4, None, dict(cam="push")),
]),

dict(id=5, loc="class", slug="INT. GESAMTSCHULE — KLASSENRAUM — TAG", beats=[
    ("a", 4.0, None, dict(cam="pan_r", fade_in=0.8)),
    ("a", 4.2, "NELLS SKIZZENBUCH — 14.10. WIEDER. UHLENGASSE.", dict(cam="push")),
    ("d", "BERINGER", "Elif."),
    ("d", "ELIF", "Ich hab gar nix gesagt!"),
    ("d", "BERINGER", "Du hast gelacht. Laut. Über Kreidefelsen."),
    ("d", "ELIF", "Die sehen aus wie 'n Zahn, Frau Beringer. Wie ein riesiger, trauriger Zahn."),
    ("a", 3.4, None, dict(cam="static")),
    ("d", "BASTI", "Frau Beringer, ich soll Ihnen von meiner Mutter — ähm — den Zettel —"),
    ("d", "BERINGER", "Bastian, du hast Sportunterricht in einem anderen Gebäude."),
    ("d", "BASTI", "Ja. Das stimmt."),
    ("a", 3.0, None, dict(cam="static")),
]),

dict(id=6, loc="uhlen", slug="EXT. UHLENGASSE — DÄMMERUNG · 18:52", beats=[
    ("a", 5.0, None, dict(cam="static", figs=[("ELIF", 0.50, 0.78)], lamps_out=[5])),
    ("a", 4.5, None, dict(cam="static", figs=[("ELIF", 0.50, 0.84)], lamps_out=[5])),
    ("a", 3.2, None, dict(cam="static", figs=[("ELIF", 0.50, 0.88)], lamps_out=[5], collapse=True)),
    ("d", "ELIF", "Hallo?", dict(figs=[("ELIF", 0.50, 0.88)], lamps_out=[5], collapse=True)),
    ("a", 3.0, None, dict(cam="static", figs=[("ELIF", 0.50, 0.88)], lamps_out=[4, 5], collapse=True)),
    ("d", "ELIF", "Ist da wer?", dict(figs=[("ELIF", 0.50, 0.9)], lamps_out=[4, 5], collapse=True)),
    ("a", 3.2, None, dict(cam="static", figs=[("ELIF", 0.50, 0.9)], lamps_out=[3, 4, 5], collapse=True)),
    ("a", 3.4, None, dict(cam="static", figs=[("ELIF", 0.50, 0.9)], lamps_out=[2, 3, 4, 5],
                          collapse=True, bend=True)),
    ("d", "ELIF", "Oh —", dict(figs=[("ELIF", 0.50, 0.9)], lamps_out=[2, 3, 4, 5], collapse=True, bend=True)),
    ("a", 3.0, "SCHAUFENSTER: ihr Spiegelbild steht noch da.",
     dict(cam="static", lamps_out=[2, 3, 4, 5], collapse=True, mirror="ELIF")),
    ("a", 2.6, "GEHWEG: sie nicht.", dict(cam="static", lamps_out=[2, 3, 4, 5], collapse=True)),
    ("a", 3.0, None, dict(cam="static", lamps_in=True, flash="ignite")),
    ("a", 6.0, None, dict(cam="static")),
]),

dict(id=7, loc="class", slug="INT. KLASSENRAUM — AM NÄCHSTEN MORGEN", beats=[
    ("a", 4.0, None, dict(cam="static", fade_in=1.0, desk_gone=True)),
    ("d", "JUNO", "Wo ist Elifs Tisch?", dict(desk_gone=True)),
    ("d", "JUNO", "Frau Beringer? Wo — wo ist Elif?", dict(desk_gone=True)),
    ("d", "BERINGER", "Wer?", dict(desk_gone=True, cam="push")),
    ("a", 4.2, "KLASSENLISTE: 29 Namen. Sahin. Varga. Wendt. Kein Toprak.",
     dict(cam="push", desk_gone=True)),
    ("d", "BERINGER", "Juno. Ist alles okay zu Hause?", dict(desk_gone=True)),
    ("a", 5.0, None, dict(cam="push", desk_gone=True, echo=True)),
]),

# ============================== ACT TWO ====================================
dict(id=8, loc="kiosk", slug="INT. KIOSK SAHIN — NACH DER SCHULE", act="AKT ZWEI", beats=[
    ("a", 3.4, None, dict(cam="pan_l", fade_in=1.0)),
    ("d", "TAREK", "Was?"),
    ("d", "JUNO", "Elif Toprak saß neben mir."),
    ("a", 3.2, None, dict(cam="push")),
    ("d", "JUNO", "Dein Aufnahmegerät. Gestern. Erste Stunde. Du hattest es an."),
    ("a", 2.6, None, dict(cam="push")),
    ("d", "ELIF", "„Die sehen aus wie 'n Zahn, Frau Beringer. Wie ein riesiger, trauriger Zahn.\"",
     dict(vo=True, echo=True)),
    ("a", 3.6, None, dict(cam="push", echo=True)),
    ("d", "TAREK", "und ich weiß nicht, wie sie aussieht."),
    ("d", "PEPE", "Wer ist Elif?"),
    ("a", 3.4, None, dict(cam="static", figs=[("PEPE", 0.52, 0.62)])),
]),

dict(id=9, loc="tanke", slug="EXT. TANKSTELLE RUNDLING — DÄMMERUNG", beats=[
    ("a", 4.0, None, dict(cam="pan_r", fade_in=0.9)),
    ("d", "KOSTA", "Wir haben zu.", dict(figs=[("KOSTA", 0.62, 1.0)])),
    ("d", "JUNO", "Hast du was gesehen. In der Uhlengasse.", dict(figs=[("JUNO", 0.32, 0.94)])),
    ("a", 3.2, None, dict(cam="push")),
    ("d", "KOSTA", "Warum fragst du das.", dict(figs=[("KOSTA", 0.62, 1.0)])),
    ("d", "NELL", "Weil sie's auch gesehen hat. Und weil ich's seit sechs Wochen zeichne.",
     dict(figs=[("NELL", 0.20, 0.98)])),
    ("a", 5.0, "ZWANZIG SEITEN. Dieselbe Gestalt. Auf jeder Seite größer.", dict(cam="push")),
    ("d", "KOSTA", "Die Laterne, die er trägt. Die brennt nicht."),
    ("d", "NELL", "Nein."),
    ("d", "KOSTA", "Ich dachte, ich hätt' — ich hab's mit dem Handy gefilmt. Da war nix drauf."),
    ("d", "NELL", "Ist nie was drauf."),
    ("a", 4.4, "Vier Murmeln auf einer Plastikkiste.", dict(cam="push")),
    ("d", "JUNO", "Wir sind die Einzigen, die sie noch kennen."),
    ("d", "NELL", "Fünf."),
    ("d", "JUNO", "Was?"),
    ("d", "NELL", "Fünf."),
    ("a", 3.6, None, dict(cam="pan_l", figs=[("BASTI", 0.74, 0.96)])),
    ("d", "BASTI", "Ähm. Hallo. Ich hab euch reden hören und — ich weiß, wer Elif Toprak ist.",
     dict(figs=[("BASTI", 0.74, 0.96)])),
    ("d", "BASTI", "und meine Mutter sagt, es gibt sie nicht.", dict(figs=[("BASTI", 0.74, 0.96)])),
    ("d", "BASTI", "Und ich glaube, meine Mutter lügt nicht. Ich glaube, sie weiß es nicht mehr.",
     dict(figs=[("BASTI", 0.74, 0.96)], cam="push")),
    ("a", 3.0, None, dict(cam="static")),
]),

dict(id=10, loc="back", slug="INT. KIOSK SAHIN — LAGERRAUM — NACHT", beats=[
    ("a", 3.6, None, dict(cam="orbit", fade_in=0.8)),
    ("d", "TAREK", "Also. Achtzehnhundertdreiundneunzig. Die Glashütte am Brandhang brennt ab."),
    ("d", "KOSTA", "Und?"),
    ("d", "TAREK", "Und der Besitzer, Emmerich Vandholt, baut die Hütte nicht wieder auf."),
    ("d", "TAREK", "Er bezahlt stattdessen hundertelf Straßenlaternen. Für die ganze Stadt."),
    ("d", "TAREK", "Weil er sie nicht verschenkt. Er schreibt sie in die Stadtsatzung rein."),
    ("d", "NELL", "„Die einhundertelf Nachtlaternen dürfen nie gemeinsam dunkel sein.\""),
    ("a", 4.0, None, dict(cam="static")),
    ("d", "NELL", "Nein. Das ist eine Bedingung."),
    ("a", 5.5, "Die Punkte laufen nicht die Straßen entlang. Sie laufen darum herum.",
     dict(cam="push", map="ring")),
    ("d", "JUNO", "Das ist kein Beleuchtungsplan. Das ist ein Kreis.", dict(map="ring")),
    ("d", "TAREK", "Und in der Mitte vom Kreis?", dict(map="ring")),
    ("d", "JUNO", "Die Glashütte.", dict(map="ring", cam="push")),
    ("d", "KOSTA", "Und was ist mit den neun, die deine Mutter abgeschraubt hat.", dict(map="ring")),
    ("d", "JUNO", "Acht am Marktplatz. Und Nummer siebenundvierzig. Uhlengasse.",
     dict(map="gap")),
    ("d", "NELL", "Da hab ich ihn gezeichnet.", dict(map="gap")),
    ("d", "KOSTA", "Da hab ich ihn gesehen.", dict(map="gap")),
    ("d", "TAREK", "Da wohnt Elif.", dict(map="gap", cam="push")),
    ("d", "BASTI", "Okay, aber — okay. Meine Mutter macht die Stadt heller."),
    ("d", "BASTI", "Doch! Genau das sagst du! Ihr sagt es alle die ganze Zeit,"),
    ("d", "BASTI", "ihr sagt es nur mit den Augen!"),
    ("d", "NELL", "Wir sagen, dass sie den Deckel aufmacht und denkt, es ist eine Lampe."),
    ("a", 3.2, None, dict(cam="static")),
    ("d", "BASTI", "…Der Deckel wovon."),
    ("a", 4.0, None, dict(cam="push")),
]),

dict(id=11, loc="torhaus", slug="EXT. KRAMMERS TORHAUS — NACHT", beats=[
    ("a", 4.6, "In jedem einzelnen Fenster brennt eine Lampe. Um elf Uhr nachts.",
     dict(cam="push", fade_in=0.8)),
    ("d", "ODA", "Nein."),
    ("d", "JUNO", "Wir haben noch nichts gefragt."),
    ("d", "ODA", "Ihr steht zu fünft nach Einbruch der Dunkelheit vor meiner Tür, Kind."),
    ("a", 3.6, None, dict(cam="push")),
    ("d", "ODA", "Fünf. Immerhin fünf."),
    ("d", "JUNO", "Was ist das Glas?"),
    ("d", "ODA", "Nachtglas. Vandholt hat es neunundzwanzig Mal gegossen und einmal richtig."),
    ("d", "ODA", "Sand aus dem Nebelgraben. Es lässt Licht rein und nur die Hälfte wieder raus."),
    ("d", "ODA", "Der Rest bleibt drin."),
    ("d", "ODA", "Das heißt, dass Glas sich erinnert, junger Mann."),
    ("d", "ODA", "Und dass in dieser Stadt etwas ist, das das nicht kann."),
    ("a", 3.4, "Sie gibt ihnen einen Karton Ersatzbirnen.", dict(cam="push")),
    ("d", "JUNO", "Frau Krammer — heißt das, Sie glauben uns?"),
    ("d", "ODA", "Ich glaube euch seit sechs Wochen."),
    ("d", "ODA", "Ich hab nur gehofft, es dauert länger, bis jemand klingelt."),
    ("a", 2.8, None, dict(cam="static")),
    ("d", "NELL", "Netter Mensch."),
]),

dict(id=12, loc="street", slug="EXT. HOLLERBRUNN — STRASSEN — NACHT", beats=[
    ("a", 4.0, None, dict(cam="pan_r", figs=[("JUNO", 0.30, .92), ("TAREK", 0.42, .98),
                                             ("NELL", 0.54, .94), ("BASTI", 0.66, .92),
                                             ("KOSTA", 0.78, .96)])),
    ("d", "BASTI", "Also, mal ganz ehrlich, seid ihr — habt ihr Angst? Ich hab so mittel Angst."),
    ("d", "KOSTA", "Ich hab Angst."),
    ("d", "BASTI", "Okay. Danke. Das hilft irgendwie."),
    ("a", 3.0, None, dict(cam="push")),
    ("d", "JUNO", "Leute."),
    ("a", 6.0, None, dict(cam="push", vision=True)),
    ("a", 4.5, "Nähte aus Licht. Laterne zu Laterne. Ein geschlossener Ring.",
     dict(cam="pan_r", vision=True)),
    ("d", "BASTI", "Das ist — Juno, das ist schön.", dict(vision=True)),
    ("d", "NELL", "Juno.", dict(vision=True)),
    ("a", 5.0, None, dict(cam="push", vision=True, mirror="ELIF")),
    ("d", "JUNO", "Elif. Elif, wir sehen dich. WIR SEHEN DICH!", dict(vision=True, mirror="ELIF")),
    ("d", "NELL", "Leute. Hinter ihr.", dict(vision=True, mirror="ELIF")),
    ("a", 6.0, None, dict(cam="push", vision=True, mirror="ELIF", crowd=15)),
    ("d", "KOSTA", "Das sind nicht nur wir, die was sehen.", dict(vision=True, crowd=15)),
    ("d", "NELL", "Nein. Die sehen uns auch.", dict(vision=True, crowd=15, cam="push")),
    ("a", 2.5, None, dict(cam="static", vision=True, crowd=15)),
]),

# ============================= ACT THREE ===================================
dict(id=13, loc="peperoom", slug="INT. WOHNUNG SAHIN — PEPES ZIMMER — NACHT · 21:14",
     act="AKT DREI", beats=[
    ("a", 4.2, None, dict(cam="push", fade_in=1.0, figs=[("PEPE", 0.44, 0.6)])),
    ("a", 4.0, None, dict(cam="static", figs=[("PEPE", 0.44, 0.6)], lamps_out=[2])),
    ("a", 4.5, None, dict(cam="push", vision=True, lo=0.72, lamps_out=[2, 3])),
    ("d", "PEPE", "Der Laternenmann.", dict(vision=True, lo=0.72, whisper=True)),
    ("a", 3.0, None, dict(cam="static")),
]),

dict(id=14, loc="kiosk", slug="INT. WOHNUNG SAHIN — NACHT · 21:31", beats=[
    ("a", 2.6, None, dict(cam="handheld")),
    ("d", "TAREK", "Pepe? — Pepe!"),
    ("d", "TAREK", "Sein Bett ist leer. Seine Schuhe sind weg. Die Dose ist weg."),
    ("d", "TAREK", "Vor 'ner Viertelstunde! Zwanzig Minuten!"),
    ("d", "TAREK", "Ich hab gesagt, er soll nicht stören, ich hab gesagt, er soll —"),
    ("d", "JUNO", "Ruf die anderen. Sofort."),
    ("d", "JUNO", "Tarek. Welche Straße ist dunkel?"),
    ("a", 2.4, None, dict(cam="push")),
    ("d", "TAREK", "Uhlengasse.", dict(whisper=True, cam="push")),
]),

dict(id=15, loc="street", slug="EXT. HOLLERBRUNN — VERFOLGUNG — NACHT", beats=[
    ("a", 5.0, None, dict(cam="handheld", figs=[("JUNO", 0.36, .95), ("TAREK", 0.52, 1.0)])),
    ("a", 4.0, None, dict(cam="handheld", figs=[("JUNO", 0.30, .95), ("TAREK", 0.46, 1.0), ("BASTI", 0.62, .93)])),
    ("d", "BASTI", "Wie viele Straßen?", dict(cam="handheld")),
    ("d", "JUNO", "Eine.", dict(cam="handheld")),
    ("a", 3.6, None, dict(cam="handheld", flash="engine")),
    ("d", "NELL", "Krammer hat aufgemacht, bevor ich geklopft hab!", dict(cam="handheld")),
    ("a", 3.0, None, dict(cam="handheld")),
]),

dict(id=16, loc="uhlen", slug="EXT. UHLENGASSE — NACHT", beats=[
    ("a", 9.0, None, dict(cam="static", lamps_out=[1, 2, 3, 4, 5], lo=0.52)),
    ("d", "TAREK", "PEPE!", dict(lamps_out=[1, 2, 3, 4, 5], lo=0.52)),
    ("d", "JUNO", "Pepe, komm zu mir. Sofort. Bitte.",
     dict(lamps_out=[1, 2, 3, 4, 5], lo=0.52, figs=[("PEPE", 0.50, 0.52)], collapse=True)),
    ("d", "PEPE", "Aber —", dict(lamps_out=[1, 2, 3, 4, 5], lo=0.52)),
    ("d", "KOSTA", "Nicht rennen.", dict(lamps_out=[1, 2, 3, 4, 5], lo=0.52, collapse=True)),
    ("d", "TAREK", "Was?!", dict(lamps_out=[1, 2, 3, 4, 5], lo=0.52, collapse=True)),
    ("d", "KOSTA", "Wenn ihr rennt, blinzelt ihr.",
     dict(lamps_out=[1, 2, 3, 4, 5], lo=0.52, collapse=True, cam="push")),
    ("a", 3.4, None, dict(cam="static", lamps_out=[1, 2, 3, 4, 5], lo=0.52, collapse=True)),
    ("d", "JUNO", "Licht. Er kommt nicht durch Licht. Wir bauen ihm einen Gang.",
     dict(lamps_out=[1, 2, 3, 4, 5], lo=0.52, collapse=True)),
    ("d", "NELL", "Ich hab sie.", dict(lamps_out=[1, 2, 3, 4, 5], lo=0.52, collapse=True)),
    ("a", 4.0, None, dict(cam="handheld", lamps_out=[1, 2, 3, 4, 5], lo=0.52, flash="torch")),
    ("a", 4.0, None, dict(cam="handheld", lamps_out=[1, 2, 3, 4, 5], lo=0.52, flash="engine")),
    ("a", 5.0, None, dict(cam="handheld", lamps_out=[1, 2, 3, 4, 5], lo=0.52, flash="flare",
                          figs=[("PEPE", 0.50, 0.52)])),
    ("d", "BASTI", "Ich guck ihn nicht an. Ich guck ihn nicht an. Ich guck ihn nicht an.",
     dict(lamps_out=[1, 2, 3, 4, 5], lo=0.52, flash="flare", cam="handheld")),
    ("d", "NELL", "Guck ihn an. Wenn du wegguckst, weißt du nicht, wo er ist.",
     dict(lamps_out=[1, 2, 3, 4, 5], lo=0.52, flash="flare", cam="handheld")),
    ("d", "TAREK", "Pepe. Ich bin's. Ich komm zu dir. Ich komm zu dir, ja?",
     dict(lamps_out=[1, 2, 3, 4, 5], lo=0.52, flash="flare",
          figs=[("PEPE", 0.50, 0.55)], cam="handheld")),
    ("d", "PEPE", "Tarek, mir ist kalt.",
     dict(lamps_out=[1, 2, 3, 4, 5], lo=0.52, flash="flare",
          figs=[("PEPE", 0.50, 0.58)], cam="push")),
    ("a", 3.0, None, dict(cam="handheld", lamps_out=[1, 2, 3, 4, 5], lo=0.50, flash="flare",
                          figs=[("PEPE", 0.50, 0.58)])),
    ("a", 3.2, None, dict(cam="handheld", lamps_out=[0, 1, 2, 3, 4, 5], lo=0.50,
                          figs=[("PEPE", 0.50, 0.58)], collapse=True, flash="die")),
    ("a", 3.4, None, dict(cam="static", lamps_out=[0, 1, 2, 3, 4, 5], lo=0.50, lo_near=True,
                          figs=[("PEPE", 0.50, 0.58)], collapse=True, blink=True)),
    ("d", "TAREK", "PEPE!", dict(lamps_out=[0, 1, 2, 3, 4, 5], lo=0.50, shout=True, collapse=True)),
    ("a", 3.0, "SCHAUFENSTER: sein Spiegelbild kommt an.",
     dict(cam="static", lamps_out=[0, 1, 2, 3, 4, 5], collapse=True, mirror="PEPE")),
    ("a", 4.0, "STRASSE: leer. Eine Murmel rollt gegen den Bordstein.",
     dict(cam="static", lamps_out=[0, 1, 2, 3, 4, 5], collapse=True)),
    ("a", 3.0, None, dict(cam="static", lamps_out=[0, 1, 2, 3, 4, 5], collapse=True)),
]),

# ============================== ACT FOUR ===================================
dict(id=17, loc="uhlen", slug="EXT. UHLENGASSE — NACHT · 22:03", act="AKT VIER", beats=[
    ("a", 5.0, None, dict(cam="static", lamps_out=[0, 1, 2, 3, 4, 5], flash="engine", collapse=True)),
    ("d", "NELL", "Sagen wir mal, wir wissen ein Ding. Es kann kein Licht überqueren.",
     dict(lamps_out=[0, 1, 2, 3, 4, 5], flash="engine")),
    ("d", "JUNO", "Nein. Es kann kein Nachtglaslicht überqueren. Die Fackel hat es getrunken.",
     dict(lamps_out=[0, 1, 2, 3, 4, 5], flash="engine")),
    ("d", "JUNO", "Nie. Elif ist an der siebenundvierzig verschwunden, und die war seit Montag ab.",
     dict(lamps_out=[0, 1, 2, 3, 4, 5], flash="engine")),
    ("d", "BASTI", "Dann schrauben wir sie wieder dran.",
     dict(lamps_out=[0, 1, 2, 3, 4, 5], flash="engine", cam="push")),
    ("d", "KOSTA", "Nein, das ist richtig. Wo ist der alte Kopf von der siebenundvierzig?",
     dict(lamps_out=[0, 1, 2, 3, 4, 5], flash="engine")),
    ("d", "JUNO", "Im Bauhof. Mit den anderen. In Kisten, in Stroh, im Lieferwagen von meiner Mutter.",
     dict(lamps_out=[0, 1, 2, 3, 4, 5], flash="engine")),
    ("d", "JUNO", "Basti.", dict(lamps_out=[0, 1, 2, 3, 4, 5], flash="engine")),
    ("d", "BASTI", "…Meine Mutter hat einen Schlüssel im Flur. An einem Haken.",
     dict(lamps_out=[0, 1, 2, 3, 4, 5], flash="engine")),
    ("a", 2.6, None, dict(cam="push", lamps_out=[0, 1, 2, 3, 4, 5], flash="engine")),
    ("d", "BASTI", "Ich hol ihn.", dict(lamps_out=[0, 1, 2, 3, 4, 5], flash="engine", cam="push")),
]),

dict(id=18, loc="bauhof", slug="EXT. BAUHOF STADTWERKE — NACHT", beats=[
    ("a", 4.0, None, dict(cam="handheld", figs=[("BASTI", 0.42, 1.0)])),
    ("a", 3.4, None, dict(cam="push")),
    ("a", 3.6, "Neun Holzkisten. Stroh.", dict(cam="push")),
    ("a", 4.0, "Auf der Latte, geschablonert: 47.", dict(cam="push")),
]),

dict(id=19, loc="lantern", slug="EXT. UHLENGASSE — LATERNE 47 — NACHT", beats=[
    ("a", 3.4, None, dict(cam="handheld")),
    ("d", "KOSTA", "Der neue Kopf passt nicht auf die alte Fassung. Die Gewinde sind anders."),
    ("d", "TAREK", "Dann geht's nicht."),
    ("d", "KOSTA", "Dann gehen wir an der Fassung vorbei."),
    ("d", "NELL", "Sie wusste es. Als sie uns die gegeben hat. Sie wusste es schon."),
    ("a", 4.0, None, dict(cam="static", lamps_out=[4, 5], collapse=True)),
    ("d", "JUNO", "Wie lange?", dict(lamps_out=[3, 4, 5], collapse=True)),
    ("d", "KOSTA", "Zwei Minuten.", dict(lamps_out=[3, 4, 5], collapse=True)),
    ("d", "KOSTA", "Dann eine.", dict(lamps_out=[2, 3, 4, 5], collapse=True, cam="push")),
]),

dict(id=20, loc="window", slug="EXT. UHLENGASSE — SCHAUFENSTER", beats=[
    ("a", 4.0, None, dict(cam="push", mirror="PEPE")),
    ("d", "TAREK", "Pepe. Pepe, guck mich an. Ja. Genau so.", dict(mirror="PEPE")),
    ("d", "TAREK", "Wir holen dich da raus. Nicht irgendwann. Jetzt gleich.", dict(mirror="PEPE")),
    ("d", "TAREK", "Also glaub mir einfach diesmal, ja?", dict(mirror="PEPE")),
    ("a", 2.6, None, dict(cam="push", mirror="PEPE")),
    ("d", "TAREK", "Ich hab gesagt, du sollst nicht stören.", dict(mirror="PEPE")),
    ("d", "TAREK", "Das war das Letzte, was ich zu dir gesagt hab, und das war gelogen.",
     dict(mirror="PEPE")),
    ("d", "TAREK", "Du störst nie. Du hast noch nie in deinem Leben gestört —", dict(mirror="PEPE")),
    ("d", "KOSTA", "JUNO. JETZT.", dict(vo=True, shout=True)),
]),

dict(id=21, loc="lantern", slug="EXT. UHLENGASSE — LATERNE 47 — WEITER", beats=[
    ("a", 3.0, None, dict(cam="handheld", lamps_out=[0, 1, 2, 3, 4, 5], flash="engine", collapse=True)),
    ("d", "KOSTA", "Wenn ich das abklemme, ist es dunkel. Bis es an ist.",
     dict(lamps_out=[0, 1, 2, 3, 4, 5], flash="engine", collapse=True)),
    ("d", "JUNO", "Wie lange dunkel?", dict(lamps_out=[0, 1, 2, 3, 4, 5], flash="engine", collapse=True)),
    ("d", "KOSTA", "Ein paar Sekunden.", dict(lamps_out=[0, 1, 2, 3, 4, 5], flash="engine", collapse=True)),
    ("d", "NELL", "Ein paar Sekunden sind viel.",
     dict(lamps_out=[0, 1, 2, 3, 4, 5], flash="engine", lo=0.62, collapse=True)),
    ("d", "JUNO", "Alle Hände dran. Wenn's dunkel wird, keiner blinzelt. Wir gucken ihn an.",
     dict(lamps_out=[0, 1, 2, 3, 4, 5], flash="engine", lo=0.62, collapse=True)),
    ("d", "BASTI", "Wir gucken ihn an.",
     dict(lamps_out=[0, 1, 2, 3, 4, 5], flash="engine", lo=0.62, collapse=True)),
    ("d", "TAREK", "Wir gucken ihn an.",
     dict(lamps_out=[0, 1, 2, 3, 4, 5], flash="engine", lo=0.62, collapse=True)),
    ("d", "KOSTA", "Drei. Zwei —",
     dict(lamps_out=[0, 1, 2, 3, 4, 5], flash="engine", lo=0.62, collapse=True, cam="push")),
    ("a", 4.5, None, dict(cam="static", flash="black", lo=0.5, collapse=True, marbles=True)),
    ("d", "JUNO", "Jetzt.", dict(flash="black", lo=0.5, whisper=True, collapse=True, marbles=True)),
    ("a", 2.2, None, dict(cam="static", flash="black", lo=0.5, collapse=True, marbles=True)),
    ("a", 5.0, None, dict(cam="crane", flash="ignite", lamps_in=True, ring=True)),
    ("a", 3.0, "EIN BILD LANG: das Licht geht durch ihn hindurch. Er ist aus Glas.",
     dict(cam="static", lo=0.52, lo_glass=True)),
    ("a", 4.0, None, dict(cam="pull")),
]),

dict(id=22, loc="uhlen", slug="EXT. UHLENGASSE — WEITER", beats=[
    ("a", 5.0, None, dict(cam="push", figs=[("PEPE", 0.50, 0.5)])),
    ("d", "PEPE", "Du hast geredet. Die ganze Zeit.", dict(figs=[("PEPE", 0.50, 0.5)])),
    ("d", "TAREK", "Ja. Ja, hab ich."),
    ("d", "PEPE", "Man hört nichts da drin. Aber man sieht dich.", dict(cam="push")),
    ("a", 4.0, None, dict(cam="static")),
    ("d", "KOSTA", "Na super."),
]),

dict(id=23, loc="dawn", slug="EXT. UHLENGASSE — MORGENGRAUEN", beats=[
    ("a", 6.0, None, dict(cam="pan_r", fade_in=1.6)),
    ("d", "BASTI", "Ich hab den Bauhof-Schlüssel geklaut und einen Laternenmast umgebaut."),
    ("d", "BASTI", "Und ich fühl mich komisch gut dabei."),
    ("d", "NELL", "Willkommen."),
    ("d", "JUNO", "Und wir müssen jemandem erzählen, dass —"),
    ("d", "TAREK", "Wem denn? Meine Eltern wissen nicht, dass Pepe weg war."),
    ("d", "TAREK", "Es ist ein Foto von einem leeren Stuhl, Juno, und er sieht das nicht."),
    ("a", 4.0, None, dict(cam="static")),
    ("d", "JUNO", "Dann sind wir's."),
    ("d", "NELL", "Dann sind wir's."),
]),

dict(id=24, loc="dawn", slug="EXT. UHLENGASSE — WEITER", beats=[
    ("a", 5.0, None, dict(cam="push")),
    ("a", 5.0, None, dict(cam="push", vision=True, mirror="ELIF")),
    ("d", "ELIF", "„Ihr habt eine vergessen.\"", dict(vision=True, mirror="ELIF", mouthed=True)),
    ("d", "JUNO", "Was?", dict(cam="push")),
    ("d", "JUNO", "Tarek. Der Plan von achtzehnhundertvierundneunzig. Der Original-Plan."),
    ("d", "TAREK", "Der ist in meiner Tasche, wieso —"),
    ("d", "JUNO", "Zähl sie.", dict(cam="push")),
    ("a", 6.0, "NACHTLATERNEN DER STADT HOLLERBRUNN — einhundertundzwölf",
     dict(cam="push", plan=True)),
    ("d", "TAREK", "Es sind hundertelf. Überall steht hundertelf. In der Satzung steht hundertelf.",
     dict(plan=True)),
    ("d", "NELL", "In der Satzung steht, wie viele brennen dürfen.", dict(plan=True)),
    ("d", "JUNO", "Nicht, wie viele es gibt.", dict(plan=True, cam="push")),
    ("a", 7.0, None, dict(cam="crane")),
    ("a", 8.0, None, dict(cam="crane", vision=True, crowd=120, final=True)),
    ("a", 3.0, None, dict(cam="static", vision=True, crowd=120, final=True, lo=0.80)),
    ("a", 2.0, None, dict(flash="black")),
    ("a", 5.0, None, dict(t="endcard")),
]),
]


# --------------------------------------------------------------------------
ACTION_SCALE = 0.52
CPS = 17.0          # German speech, characters per second
PAD = 0.11          # breath after each line
MIN_LINE = 1.30


def line_duration(text):
    return max(MIN_LINE, len(text) / CPS) + PAD


def build_timeline():
    """Flatten SCENES into absolute-timed shots."""
    shots, t = [], 0.0
    for sc in SCENES:
        for i, beat in enumerate(sc["beats"]):
            fx = dict(beat[3]) if len(beat) > 3 else {}
            if beat[0] == "d":
                dur = line_duration(beat[2])
                shot = dict(kind="d", speaker=beat[1], text=beat[2])
            else:
                dur = float(beat[1]) * ACTION_SCALE
                shot = dict(kind="a", caption=beat[2])
            shot.update(scene=sc["id"], loc=sc["loc"], slug=sc.get("slug"),
                        act=sc.get("act") if i == 0 else None,
                        first=(i == 0), t0=t, t1=t + dur, dur=dur, fx=fx, idx=len(shots))
            shots.append(shot)
            t += dur
    return shots, t


if __name__ == "__main__":
    sh, total = build_timeline()
    print(f"{len(sh)} shots, {total/60:.0f}:{total%60:04.1f}")
    from collections import defaultdict
    per = defaultdict(float)
    for s in sh:
        per[s["scene"]] += s["dur"]
    for k in sorted(per, key=lambda k: [x["scene"] for x in sh].index(k)):
        print(f"  scene {k:>2}: {per[k]:6.1f}s")
