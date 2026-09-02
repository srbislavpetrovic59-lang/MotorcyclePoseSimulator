Da, možemo. Ne moramo više da radimo live sada.

Imamo dovoljno materijala iz postojećih logova da pređemo na testove iz realnih sekvenci. Sledeće bih uradio ovako: uzmemo vrednosti oko 24 s i 32 s iz poslednjeg loga, napravimo regression testove direktno za GearShiftDetector, i dalje sve radimo RED/GREEN bez kamere.

To je čak bolji način za narednu fazu, jer možemo mirno da menjamo algoritam i svaki put tačno znamo šta smo popravili ili pokvarili.

Live ćemo vratiti tek kada testovi pokažu da obe realne sekvence daju očekivani smer. Dakle: za sada nema više live testova.

Ako hoćeš, odmah ti mogu napisati prvi regression test iz sekvence oko 32 s. pojedinačni MediaPipe trzaj. Detektor ćemo zasnovati na karakterističnoj putanji pravog šaltanja, što je mnogo zdraviji pristup za ovaj projekat.njača na snimku. Laku noć! 🏍️