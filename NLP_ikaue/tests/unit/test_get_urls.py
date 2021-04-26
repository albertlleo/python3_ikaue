import pytest
import sys

sys.path.insert(1, "NLP_ikaue/src/")
from NLP_extractor import get_urls


@pytest.mark.parametrize(
    ["input_subject1","input_subject2", "expected"],
    [
        # Input 1
        (
            "camiseta negra",
            10,
            ['https://www.amazon.es/Camisetas-Negras/s?k=Camisetas+Negras', 'https://www.zara.com/es/es/mujer-camisetas-negras-l2226.html', 'https://www.laredoute.es/lndng/ctlg.aspx?artcl=camiseta-negra', 'https://www.zalando.es/ropa-de-mujer-camisetas-y-tops/_negro/']
,
        ),
        # Input 2
        (
            "falda blanca",
            10,
            ""
        ),
    ],
)

def test_get_subject(input_subject1,input_subject2, expected):
    """
    :param input_subject1: Keyword
    :param input_subject2: Number of max urls
    :param expected: list of urls
    :return: assertion test accepted
    """

    actual = get_urls(input_subject1,input_subject2)

    assert type(actual) == list #modify as desired. Dummy example. It could be assert actual == expected

