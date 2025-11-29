from verdandi.util.text import summary_to_category


def test_category_mapping():
    assert summary_to_category("❤️ Fromage") == "heart"
    assert summary_to_category("Soirée couple") == "heart"
    assert summary_to_category("❤️ Diner en amoureux") == "heart"
    assert summary_to_category("Diner") == "tablewear"
    assert summary_to_category("Dîner") == "tablewear"
    assert summary_to_category("Concert") == "music"
    assert summary_to_category("🧑🏽‍⚕") == "medical"
