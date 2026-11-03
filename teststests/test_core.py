import numpy as np

from ehkscci.core import features, score, wasserstein
from ehkscci.bench import circle, tau0, auc


def test_score_nominal_nul():
    z = circle(10)
    nominal = features(z, tau0(z))

    resultat = score(nominal, nominal)

    assert abs(resultat["total"]) < 1e-12


def test_transport():
    cout = np.array([[0.0, 1.0], [1.0, 0.0]])

    distance = wasserstein(
        [0.8, 0.2],
        [0.3, 0.7],
        cout,
    )

    assert abs(distance - 0.5) < 1e-10


def test_auc():
    assert auc([3, 4], [1, 2]) == 1.0
    assert auc([1], [1]) == 0.5
