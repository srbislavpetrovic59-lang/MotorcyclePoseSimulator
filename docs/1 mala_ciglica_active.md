Da — pošto je još dan, iskoristimo ga za još jedan kvalitetan live set merenja, ali sada ciljano.

Ne bih sada dirao detector. Snimio bih samo sirove metrike za tri odvojena scenarija, jer će nam to kasnije dati mnogo bolju kalibraciju:

A) 5 s FOOTPEG
   3 s NAPRED do menjača, bez šaltanja
   5 s FOOTPEG


B) 5 s FOOTPEG
   pravi SHIFT_UP
   5 s FOOTPEG


C) 5 s FOOTPEG
   pravi SHIFT_DOWN
   5 s FOOTPEG

U logu neka ostanu:
left_foot_forward, left_foot_drop, left_foot_angle, plus visibility.

Vreme mi posle napiši samo približno, npr.:

napred: 10–13 s
shift up: 20–23 s
shift down: 30–33 s

Najvažnije: radi sve sa istim položajem kamere, istim svetlom i patikama, jer onda ćemo moći direktno da uporedimo koliko se left_foot_forward menja kod samog prilaska menjaču, a koliko kod pravog UP/DOWN pokreta.

Ako hoćeš, možemo odmah da uradimo jedan kontinuirani snimak od oko 40 sekundi sa sva tri scenarija.

Pasted text(20260826-153247).txt
Document
napred nazad: 10 ;  shift up: 20s;    shift down 30s

Ovaj snimak je veoma koristan, jer sada imamo sva tri scenarija u istim uslovima.

Kod običnog napred–nazad oko 10 s, left_foot_forward se menja dosta jako — ide od približno 0.005 do 0.038. Dakle sama amplituda forward pomeranja jeste dobar signal da je noga napustila miran položaj, ali nije dovoljna da kaže da li je to bio shift ili samo prilazak menjaču.

Kod pravog SHIFT_UP oko 20 s forward ide približno do 0.040, a ugao se penje do oko 162°. Kod SHIFT_DOWN oko 30 s forward ide još više, do oko 0.047, dok ugao pada čak do oko 145–146°. Dakle sada već imamo dosta lep fizički obrazac:

FOOTPEG / mirno
    ↓
left_foot_forward se značajno promeni
    ↓
ako angle ide nagore → SHIFT_UP kandidat
ako angle ide nadole → SHIFT_DOWN kandidat
    ↓
povratak noge → potvrda

To je mnogo bolji model nego sadašnji „trenutni ugao određuje smer“.

Još jedna važna stvar: visibility kod SHIFT_DOWN dela pada na oko 0.77–0.82, dok je ranije oko 0.9. To znači da ćemo morati da budemo tolerantni prema visibility-ju; ne bih stavljao visok prag tipa 0.9, jer bismo baš pravi shift-down mogli da odbacimo. U logu stvarno ima uspešan SHIFT_DOWN oko 32.6 s uz visibility oko 0.77–0.80.

I potvrđuje se da trenutna logika još pravi lažne događaje — npr. oko 10.45 s, kada si radio samo napred–nazad, ona emituje SHIFT_UP. To je upravo ono što novi „forward + trend“ model treba da spreči.

Po meni imamo dovoljno dnevnih merenja. Sledeći korak više nije live snimanje, nego da u kod uvedemo dve stvari: foot_moved_forward kao uslov za početak kandidata i trend ugla kroz nekoliko frejmova za određivanje UP ili DOWN.

Tu bih sutra krenuo test-first, malim korakom.