from verdandi.util.text import summary_to_category


def test_category_mapping():
    assert "heart" == summary_to_category("❤️ Fromage")
    assert "heart" == summary_to_category("Soirée couple")
    assert "heart" == summary_to_category("❤️ Diner en amoureux")
    assert "tablewear" == summary_to_category("Diner")
    assert "tablewear" == summary_to_category("Dîner")
    assert "music" == summary_to_category("Concert")
    assert "medical" == summary_to_category("🧑🏽‍⚕")
