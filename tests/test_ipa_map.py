import pytest
from ipa_features.ipa_map import ipa_parser, ph_element, ph_base, ph_consonant, ph_vowel, ph_diacritic, ph_ligature, ph_boundary, ph_stress

def test_ph_element_classify():
    # Test base consonant
    assert isinstance(ph_element('p').classify(), ph_consonant)
    # Test base vowel
    assert isinstance(ph_element('o').classify(), ph_vowel)
    # Test diacritic
    assert isinstance(ph_element('ʰ').classify(), ph_diacritic)
    # Test ligature
    assert isinstance(ph_element('͡').classify(), ph_ligature)
    # Test boundary
    assert isinstance(ph_element('.').classify(), ph_boundary)
    # Test stress
    assert isinstance(ph_element("ˈ").classify(), ph_stress)
    
def test_ipa_parser_simple():
    # Test basic segment
    assert ipa_parser("pʰ") == [
        [ph_element('p'), ph_element('ʰ')]
    ]
    
    # Test multiple segments and whitespace handling
    assert ipa_parser(" \tpʰæt kːaʧ\n suto \r\n  ") == [
        [ph_element('p'), ph_element('ʰ')],
        [ph_element('æ')],
        [ph_element('t')],
        [ph_element(' ')],
        [ph_element('k'), ph_element('ː')],
        [ph_element('a')],
        [ph_element('ʧ')],
        [ph_element(' ')],
        [ph_element('s')],
        [ph_element('u')],
        [ph_element('t')],
        [ph_element('o')]
    ]
    
    # Test left and right diacritics and primary stress
    assert ipa_parser("ⁿaˈʧ̥ukʰⁿaˈʧ̥") == [
        [ph_element('ⁿ'), ph_element('a')],
        [ph_element('ˈ')],
        [ph_element('ʧ'), ph_element('̥')],
        [ph_element('u')],
        [ph_element('k'), ph_element('ʰ')],
        [ph_element('ⁿ'), ph_element('a')],
        [ph_element('ˈ')],
        [ph_element('ʧ'), ph_element('̥')]
    ]
    
    # Test syllable and foot boundary characters
    assert ipa_parser("ˌ‖|ᶬhi.toˡˈ|ᵐtə̃") == [
        [ph_element('ˌ')],
        [ph_element('‖')],
        [ph_element('|')],
        [ph_element('ᶬ'), ph_element('h')],
        [ph_element('i')],
        [ph_element('.')],
        [ph_element('t')],
        [ph_element('o'), ph_element('ˡ')],
        [ph_element('ˈ')],
        [ph_element('|')],
        [ph_element('ᵐ'), ph_element('t')],
        [ph_element('ə'), ph_element('̃')]
    ]
    
    # Test invalid characters
    with pytest.raises(ValueError):
        ipa_parser("Ђ")

def test_ipa_parser_invalid_sequences():
    # Test invalid Phon IPA sequences
    with pytest.raises(ValueError):
        ipa_parser("ʰp")
        ipa_parser("pⁿ")
        ipa_parser(" pˈ")

def test_ipa_parser_role_switchers():
    # Test role-switched diacritics
    assert ipa_parser("ʰ̵toᵐ̵ pⁿ̵oˢ") == [
        [ph_element('ʰ'), ph_element('̵'), ph_element('t')],
        [ph_element('o'), ph_element('ᵐ'), ph_element('̵')],
        [ph_element(' ')],
        [ph_element('p'), ph_element('ⁿ'), ph_element('̵')],
        [ph_element('o'), ph_element('ˢ')]
    ]

def test_ipa_parser_compound_phones():
    # Test compound phones and ligatures
    assert ipa_parser("t͡ʃo͡ʊ t͡sʧ") == [
        [ph_element('t'), ph_element('͡'), ph_element('ʃ')],
        [ph_element('o'), ph_element('͡'), ph_element('ʊ')], 
        [ph_element(' ')],
        [ph_element('t'), ph_element('͡'), ph_element('s')],
        [ph_element('ʧ')]
    ]