Uh, sad imamo važan trag: prethodni „zeleni“ test nas je prevario. 🙂

U stvarnom logu posle pravog SHIFT_UP u 9.391 s, rearm dolazi do frames=2 oko 10.922 s. Već na sledećem frejmu 10.969 s je rearm=False, ali _forward_offset_history nije očišćen — i dalje sadrži stare vrednosti.

Zato kasnije, dok samo sediš, dobijamo još jedan lažni:

t=11.688
GEAR SHIFT: SHIFT_UP

Zašto je naš test bio zelen? Zato što smo slali tačno:

left_foot_forward=0.035
baseline=0.035

pa je offset bio 0.0. Time smo aktivirali drugi mehanizam:

if abs(offset) < 0.002:
    self._baseline_settle_frames += 1

i on je očistio istoriju. Dakle test nije dokazao da je rearm uradio clear().

Napravimo sada ispravan test, bez baseline-settle pomoći:

def test_rearm_itself_clears_forward_offset_history():
    detector = GearShiftDetector()

    detector._state = "READY"
    detector._shift_rearm_pending = True
    detector._forward_movement_active = True
    detector._forward_baseline = 0.035
    detector._forward_offset_history = [
        -0.024,
        -0.023,
        -0.020,
    ]

    for forward in [
        0.038,
        0.039,
        0.038,
    ]:
        detector.update(
            0.120,
            155.0,
            left_foot_forward=forward,
        )

    assert detector._shift_rearm_pending is False
    assert detector._forward_offset_history == []

Ovde su offseti +0.003, +0.004, +0.003, dakle nijedan nije < 0.002. Baseline-settle ne može da nam pomogne.

Očekujem da ovaj novi test bude crven. Ako jeste, onda ćemo pogledati tačno uvlačenje rearm bloka — jer live log kaže da clear() još uvek nije na pravom mestu.

Usput, baseline ovog puta jeste stabilan (0.0299–0.0358), ali je postavljen tek u 8.359 s, dakle nakon što si već započeo pokret u 8 s. Ipak, prvi događaj je pravilno bio SHIFT_UP u 9.391 s; to ćemo rešavati tek posle ovog rearm baga.