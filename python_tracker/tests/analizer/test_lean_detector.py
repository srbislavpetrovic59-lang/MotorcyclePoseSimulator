import pytest
import math

from pose.analyzers.lean_detector import LeanDetector


def test_neutral_lean_is_zero():
    detector = LeanDetector()

    detector.calibrate(-5.5)

    assert detector.update(-5.5) == pytest.approx(0.0)

def test_lean_left_is_negative():
    detector = LeanDetector()
    detector.calibrate(-5.5)

    assert detector.update(-20.0) == pytest.approx(-14.5)


def test_lean_right_is_positive():
    detector = LeanDetector()
    detector.calibrate(-5.5)

    assert detector.update(20.0) == pytest.approx(25.5)


def test_small_lean_is_ignored():
    detector = LeanDetector()
    detector.calibrate(-5.5)

    assert detector.update(-4.0) == pytest.approx(0.0)
    assert detector.update(-7.0) == pytest.approx(0.0)

def test_lean_dead_zone_boundary():
    detector = LeanDetector()
    detector.calibrate(-5.5)

    # Tacno na granici
    assert detector.update(-8.5) == pytest.approx(0.0)
    assert detector.update(-2.5) == pytest.approx(0.0)

    # Neposredno izvan granice
    assert detector.update(-8.6) == pytest.approx(-3.1)
    assert detector.update(-2.4) == pytest.approx(3.1)

def test_lean_hysteresis():
    detector = LeanDetector()
    detector.calibrate(0.0)

    assert detector.update(2.9) == pytest.approx(0.0)

    # Aktiviranje
    assert detector.update(3.1) == pytest.approx(3.1)

    # Ostaje aktivan unutar histerezne zone
    assert detector.update(2.9) == pytest.approx(2.9)

    # Deaktiviranje
    assert detector.update(1.9) == pytest.approx(0.0)

def test_lean_direction_change_requires_activation():
    detector = LeanDetector()
    detector.calibrate(0.0)

    # Aktiviramo levi nagib.
    assert detector.update(-10.0) == pytest.approx(-10.0)

    # Povratak ka sredini, ali jos uvek aktivan.
    assert detector.update(-2.5) == pytest.approx(-2.5)

    # Prelazak na desnu stranu ne sme odmah
    # aktivirati desni nagib.
    assert detector.update(2.5) == pytest.approx(0.0)

    # Desni nagib se aktivira tek iznad 3 stepena.
    assert detector.update(3.5) == pytest.approx(3.5)

def test_direct_lean_direction_change():
    detector = LeanDetector()
    detector.calibrate(0.0)

    # Levi nagib
    assert detector.update(-15.0) == pytest.approx(-15.0)
    assert detector._direction == -1

    # Direktan prelazak u desni nagib
    assert detector.update(12.0) == pytest.approx(12.0)
    assert detector._direction == 1

    # Povratak u neutralni polozaj
    assert detector.update(0.0) == pytest.approx(0.0)
    assert detector._direction == 0

def test_normalized_lean():
    detector = LeanDetector()
    detector.calibrate(0.0)

    assert detector.update_normalized(-15.0) == pytest.approx(-0.5)
    assert detector.update_normalized(15.0) == pytest.approx(0.5)

    assert detector.update_normalized(-30.0) == pytest.approx(-1.0)
    assert detector.update_normalized(30.0) == pytest.approx(1.0)

    # Ogranicenje izlaza
    assert detector.update_normalized(-45.0) == pytest.approx(-1.0)
    assert detector.update_normalized(45.0) == pytest.approx(1.0)

def test_normalized_lean_respects_dead_zone():
    detector = LeanDetector()
    detector.calibrate(-5.5)

    # Mali pokreti ne smeju izazvati skretanje.
    assert detector.update_normalized(-4.0) == pytest.approx(0.0)
    assert detector.update_normalized(-7.0) == pytest.approx(0.0)

    # Veci nagib aktivira upravljanje.
    assert detector.update_normalized(-11.5) == pytest.approx(-0.2)

    # Histereza zadrzava aktivan nagib.
    assert detector.update_normalized(-8.0) == pytest.approx(-2.5 / 30.0)

    # Povratak u neutralni polozaj.
    assert detector.update_normalized(-5.5) == pytest.approx(0.0)

def test_normalized_lean_is_smoothed():
    detector = LeanDetector()
    detector.calibrate(0.0)

    # Pocetno neutralno stanje.
    assert detector.update_smoothed(0.0) == pytest.approx(0.0)

    # Nagli nagib od 30 stepeni.
    # Normalizovan signal je 1.0,
    # ali filtrirani izlaz raste postepeno.
    assert detector.update_smoothed(30.0) == pytest.approx(0.25)

    # Sledeci uzorak istog nagiba.
    assert detector.update_smoothed(30.0) == pytest.approx(0.4375)

def test_smoothed_lean_returns_to_zero():
    detector = LeanDetector()
    detector.calibrate(0.0)

    # Vozac se naginje udesno.
    for _ in range(10):
        detector.update_smoothed(30.0)

    # Vozac se vraca u neutralni polozaj.
    for _ in range(30):
        result = detector.update_smoothed(0.0)

    # Upravljački signal treba potpuno da se umiri.
    assert result == pytest.approx(0.0, abs=0.001)

def test_smoothed_lean_snaps_to_zero():
    detector = LeanDetector()
    detector.calibrate(0.0)

    # Aktiviramo nagib.
    for _ in range(10):
        detector.update_smoothed(30.0)

    # Vracamo se u neutralni polozaj.
    for _ in range(30):
        result = detector.update_smoothed(0.0)

    # Signal mora biti tacno nula.
    assert result == 0.0
    assert detector._smoothed_lean == 0.0

def test_smoothed_lean_changes_direction():
    detector = LeanDetector()
    detector.calibrate(0.0)

    # Postepeno uspostavljamo levi nagib.
    for _ in range(10):
        left = detector.update_smoothed(-30.0)

    assert left < -0.9

    # Vozac naglo prelazi u desni nagib.
    first_right = detector.update_smoothed(30.0)

    # Filter jos pamti prethodni levi nagib.
    assert left < first_right < 0.0

    # Posle vise uzoraka signal prelazi udesno.
    for _ in range(10):
        right = detector.update_smoothed(30.0)

    assert right > 0.0
    assert right <= 1.0

def test_time_based_smoothing():
    detector = LeanDetector()
    detector.calibrate(0.0)

    # dt = 0.1 s, tau = 0.1 s
    # alpha = 1 - exp(-1)

    result = detector.update_smoothed(
        30.0,
        dt=0.1,
    )

    expected = 1.0 - math.exp(-1.0)

    assert result == pytest.approx(expected)

def test_smoothing_is_independent_of_fps():
    detector_10fps = LeanDetector()
    detector_30fps = LeanDetector()

    detector_10fps.calibrate(0.0)
    detector_30fps.calibrate(0.0)

    # Isti nagib tokom jedne sekunde.

    for _ in range(10):
        result_10fps = detector_10fps.update_smoothed(
            30.0,
            dt=0.1,
        )

    for _ in range(30):
        result_30fps = detector_30fps.update_smoothed(
            30.0,
            dt=1.0 / 30.0,
        )

    assert result_10fps == pytest.approx(
        result_30fps,
        abs=1e-6,
    )

def test_smoothing_ignores_nonpositive_dt():
    detector = LeanDetector()
    detector.calibrate(0.0)

    # Uspostavljamo filtrirani nagib.
    initial = detector.update_smoothed(
        30.0,
        dt=0.1,
    )

    # Nema proteklog vremena.
    result_zero = detector.update_smoothed(
        -30.0,
        dt=0.0,
    )

    assert result_zero == pytest.approx(initial)

    # Negativno vreme takodje ne menja izlaz.
    result_negative = detector.update_smoothed(
        -30.0,
        dt=-0.1,
    )

    assert result_negative == pytest.approx(initial)

def test_smoothing_limits_large_dt():
    detector = LeanDetector()
    detector.calibrate(0.0)

    # Kamera radi normalno.
    initial = detector.update_smoothed(
        0.0,
        dt=0.033,
    )

    assert initial == pytest.approx(0.0)

    # Kamera zastaje na pola sekunde.
    result = detector.update_smoothed(
        30.0,
        dt=0.5,
    )

    # Posle zastoja ne zelimo gotovo
    # trenutnu maksimalnu komandu.
    assert result <= 0.5

def test_reset_clears_lean_but_preserves_calibration():
    detector = LeanDetector()
    detector.calibrate(-5.5)

    # Aktiviramo nagib.
    detector.update_smoothed(-35.5, dt=0.1)

    assert detector._smoothed_lean < 0.0
    assert detector._direction == -1

    # Simuliramo gubitak pracenja.
    detector.reset()

    assert detector._smoothed_lean == 0.0
    assert detector._direction == 0
    assert detector._neutral_angle == pytest.approx(-5.5)

    # Nakon povratka pracenja, neutralni polozaj
    # i dalje odgovara prethodnoj kalibraciji.
    assert detector.update_smoothed(-5.5, dt=0.033) == 0.0

def test_reset_starts_smoothing_from_zero():
    detector = LeanDetector()
    detector.calibrate(0.0)

    # Prethodno smo bili nagnuti ulevo.
    for _ in range(10):
        detector.update_smoothed(-30.0, dt=0.1)

    assert detector._smoothed_lean < -0.9

    # Gubitak pracenja.
    detector.reset()

    # Prvi novi frejm pokazuje desni nagib.
    result = detector.update_smoothed(30.0, dt=0.1)

    expected = 1.0 - math.exp(-1.0)

    assert result == pytest.approx(expected)
    assert detector._direction == 1

def test_recalibration_resets_smoothed_lean():
    detector = LeanDetector()
    detector.calibrate(0.0)

    # Aktiviramo desni nagib.
    for _ in range(10):
        detector.update_smoothed(30.0, dt=0.1)

    assert detector._smoothed_lean > 0.9
    assert detector._direction == 1

    # Nova kalibracija.
    detector.calibrate(-5.5)

    assert detector._neutral_angle == pytest.approx(-5.5)
    assert detector._direction == 0
    assert detector._smoothed_lean == 0.0

    # Novi neutralni polozaj ne izaziva skretanje.
    assert detector.update_smoothed(
        -5.5,
        dt=0.033,
    ) == 0.0