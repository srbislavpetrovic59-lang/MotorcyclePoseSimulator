Da — ovo je pravo mesto gde metrics zaista postoji. 👍

Pošto nam vreme trenutno treba samo za live eksperiment, možemo mnogo jednostavnije nego preko FootAnalyzer-a.

U _process_pose(), odmah posle:

metrics = self._analyzer.analyze(
    frame_analysis
)

dodaj:

metrics["elapsed_time"] = time.monotonic() - self._start_time

Ali samo ako PosePipeline već ima self._start_time. Ako nema, ne dodaj još tu liniju.

Pošto želimo da vreme na overlay-u bude isto ono koje već ispisuje FootAnalyzer, čistije je ipak da ne pravimo drugi _start_time.

Najmanja i najsigurnija varijanta

U FootAnalyzer.analyze() već imaš:

elapsed = time.monotonic() - self._start_time

Na kraju FootAnalyzer.analyze() sigurno vraća neki rezultat, verovatno dictionary poput:

return {
    ...
}

Tu samo dodamo:

"elapsed_time": elapsed,

Tada će tok biti prirodan:

FootAnalyzer
     ↓
elapsed_time
     ↓
PoseAnalyzer metrics
     ↓
_process_pose()
     ↓
OverlayRenderer

i u ovom _process_pose() ne moramo ništa menjati.

Dakle, pošalji mi samo return deo iz FootAnalyzer.analyze(). Mislim da će nam trebati bukvalno jedna linija.

ok znaci bez starttime, nego elapsed, a gde da ispisuje

Da — ne pravimo novi start_time. Koristimo elapsed koji već računaš u FootAnalyzer. 👍

U FootAnalyzer.analyze() na kraju, u dictionary koji već vraćaš, dodaćemo:

"elapsed_time": elapsed,

Time će elapsed_time automatski završiti u metrics.

A ispis na slici ostaje u OverlayRenderer._draw_metrics(). Tamo dodaj, najbolje na samom početku metode:

elapsed = metrics.get("elapsed_time")


time_text = (
    f"TIME: {elapsed:.1f} s"
    if elapsed is not None
    else "TIME: --"
)


cv2.putText(
    frame,
    time_text,
    (700, 60),
    cv2.FONT_HERSHEY_SIMPLEX,
    1.5,
    (255, 255, 255),
    3,
    cv2.LINE_AA,
)

Dakle tok je:

FootAnalyzer
    elapsed
       ↓
"elapsed_time": elapsed
       ↓
PoseAnalyzer
       ↓
metrics
       ↓
OverlayRenderer
       ↓
TIME: 18.4 s

Samo nam još treba da vidimo kako tačno izgleda return na kraju FootAnalyzer.analyze(), da ti kažem gde da ubaciš "elapsed_time": elapsed bez nagađanja.




Da, baš se vidi da visibility često pada ispod praga, pa zato dobijaš drop=None i detector praktično oslepi za stopalo.

Na početku loga imaš, recimo:

heel=0.34 ankle=0.33 foot=0.31

a kasnije dugo ostaje oko ankle 0.3–0.4, foot 0.4–0.5, pa drop ostaje None.

Tek oko t≈11.7 s visibility konačno pređe prag dovoljno da dobijemo stvarne drop vrednosti i GEAR logove.

Znači sada je veći problem tracking stopala, ne logika menjača.

Ja bih sledeće uradio praktično: ne diramo detector, nego scenu. Kamera malo niže ili bliže, da stopalo zauzme veći deo slike, i da kontrast oko stopala ostane jak. Ako može, neka leva noga i menjač budu bliže centru kadra — MediaPipe obično mnogo stabilnije drži landmarke tamo nego pri dnu/ivici slike.

I još nešto: naš prag visibility >= 0.5 trenutno je dosta strog za ovu scenu. Ali ne bih ga odmah spuštao, jer bi onda dobili više pogrešnih landmarkova. Prvo bih pokušao da fizički dignemo visibility iznad 0.6.

Dakle trenutno: kamera/scena pre koda. Kad dobijemo stabilno heel/ankle/foot > 0.6, onda tek ima smisla dalje učiti shift putanju.  