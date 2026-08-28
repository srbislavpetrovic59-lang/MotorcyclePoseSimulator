Pregledao sam detaljnije delove oko 10 s i 20 s. I nalaz je zanimljiv: ne bih još dodavao novi fizički uslov. Log pokazuje da imamo fundamentalniji problem.

Oko 10 s, kada je trebalo da bude pravi SHIFT_UP, detektor je upravo pre toga već emitovao lažni SHIFT_DOWN u 9.657 s. Zatim se pravi pokret oko 10 s dešava dok je stanje već resetovano: ugao ide 148 → 149 → 153.7 → 151.1 → 152.1 → 155.9, a forward povremeno prelazi prag, ali nema dovoljno konzistentne sekvence da se registruje UP.

Još jasnije je oko 20 s. Neposredno pre planiranog SHIFT_DOWN, detektor zaključava:

pending=['UP']
history=['UP']

i u 19.657 s emituje SHIFT_UP — upravo suprotan smer od onoga što si nameravao.

Dakle, naš direction-lock je uspešno rešio oscilovanje, ali je otkrio njegovu manu:

zaključavamo prvi trend prerano.

Na primer oko 19.36–19.53 s imamo otprilike:

162.7
158.9   → zaključan UP
150.0
145.4

A stvarno kretanje je očigledno nastavilo snažno naniže. Detektor više ne sme da promeni odluku jer smo mu upravo zabranili.

Zato ne bih sada dodavao još pragova. Sledeći mali korak treba da bude: ne zaključavati prvi kandidat, nego tek potvrđen kandidat.

I opet prvo crveni test. Dodaj:

def test_single_pending_candidate_does_not_lock_direction():
    detector = GearShiftDetector()


    detector._pending_zones = ["UP"]


    detector._add_shift_candidate("DOWN")


    assert detector._pending_zones == ["UP", "DOWN"]

Očekujem crveno, jer naš trenutni helper čim vidi bilo šta u _pending_zones, odbija novi kandidat.

Za sada samo ovaj test. Pokreni:

python -m pytest tests/analizer/test_gear_analyzer.py

Javi zelen/crven. Posle toga ćemo odlučiti koliko potvrda treba pre zaključavanja — bez nagađanja pragova unapred.