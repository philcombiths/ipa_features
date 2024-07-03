import pytest
from ipa_features.ipa_map import ipa_parser, segment_generator, PhoElement, PhoBase, PhoConsonant, PhoVowel, PhoDiacritic, PhoLigature, PhoBoundary, PhoStress, PhoSegment

def test_classify():
    """Test PhoElement.classify()."""
    # Test base
    assert isinstance(PhoElement('p').classify(), PhoBase)
    assert isinstance(PhoElement('ǃ').classify(), PhoBase)
    # Test base consonant
    assert isinstance(PhoElement('p').classify(), PhoConsonant)
    assert isinstance(PhoElement('ǁ').classify(), PhoConsonant)
    # Test base vowel
    assert isinstance(PhoElement('o').classify(), PhoVowel)
    # Test diacritic
    assert isinstance(PhoElement('ʰ').classify(), PhoDiacritic)
    # Test ligature
    assert isinstance(PhoElement('͡').classify(), PhoLigature)
    # Test boundary
    assert isinstance(PhoElement('.').classify(), PhoBoundary)
    # Test stress
    assert isinstance(PhoElement("ˈ").classify(), PhoStress)

def test_segment_class(): # TODO: Compelete this
    assert segment_generator("ʧ̥")[0]
    assert segment_generator("p")
    assert segment_generator("pʰ")
    assert segment_generator("ⁿkː")
    pass

def test_ipa_parser_simple():
    """Test most Phon-compatible IPA sequences."""
    # Test basic segment
    assert ipa_parser("pʰ") == [
        [PhoElement('p'), PhoElement('ʰ')]
    ]
    
    # Test multiple segments andwhitespace handling
    assert ipa_parser("[     \tpʰæt kːaʧ\n suto \r\n  ]") == [
        [PhoElement('p'), PhoElement('ʰ')],
        [PhoElement('æ')],
        [PhoElement('t')],
        [PhoElement(' ')],
        [PhoElement('k'), PhoElement('ː')],
        [PhoElement('a')],
        [PhoElement('ʧ')],
        [PhoElement(' ')],
        [PhoElement('s')],
        [PhoElement('u')],
        [PhoElement('t')],
        [PhoElement('o')]
    ]
    
    # Test left and right diacritics and primary stress
    assert ipa_parser("/ⁿaˈʧ̥ukʰⁿaˈʧ̥/") == [
        [PhoElement('ⁿ'), PhoElement('a')],
        [PhoElement('ˈ')],
        [PhoElement('ʧ'), PhoElement('̥')],
        [PhoElement('u')],
        [PhoElement('k'), PhoElement('ʰ')],
        [PhoElement('ⁿ'), PhoElement('a')],
        [PhoElement('ˈ')],
        [PhoElement('ʧ'), PhoElement('̥')]
    ]
    
    # Test syllable and foot boundary characters
    assert ipa_parser("ˌ‖|ᶬhi.toˡˈ|ᵐtə̃") == [
        [PhoElement('ˌ')],
        [PhoElement('‖')],
        [PhoElement('|')],
        [PhoElement('ᶬ'), PhoElement('h')],
        [PhoElement('i')],
        [PhoElement('.')],
        [PhoElement('t')],
        [PhoElement('o'), PhoElement('ˡ')],
        [PhoElement('ˈ')],
        [PhoElement('|')],
        [PhoElement('ᵐ'), PhoElement('t')],
        [PhoElement('ə'), PhoElement('̃')]
    ]
    
    # Test invalid characters
    with pytest.raises(ValueError):
        ipa_parser("Ђ")

def test_ipa_parser_invalid_sequences():
    """Test invalid Phon IPA sequences. Not implemented."""
    with pytest.raises(ValueError):
        ipa_parser("ʰp")
        ipa_parser("pⁿ")
        ipa_parser(" pˈ")
        ipa_parser("ʰ̵ⁿˢ͡")

def test_ipa_parser_diacritic_role_switchers():
    """Test compound phones and ligatures. Not implemented."""
    assert ipa_parser("ʰ̵toᵐ̵ pⁿ̵oˢ") == [
        [PhoElement('ʰ'), PhoElement('̵'), PhoElement('t')],
        [PhoElement('o'), PhoElement('ᵐ'), PhoElement('̵')],
        [PhoElement(' ')],
        [PhoElement('p'), PhoElement('ⁿ'), PhoElement('̵')],
        [PhoElement('o'), PhoElement('ˢ')]
    ]
    assert ipa_parser('ʰ̵t')[0][0].role_switcher # == True
    assert ipa_parser('ʰ̵t')[0][0].attach_direction == 'left'
    assert ipa_parser('ʰ̵t')[0][0].base == PhoElement("t")

def test_ipa_parser_compound_phones():
    """Test compound phones and ligatures. Not implemented."""
    assert ipa_parser("t͡ʃo͡ʊ t͡sʧ") == [
        [PhoElement('t'), PhoElement('͡'), PhoElement('ʃ')],
        [PhoElement('o'), PhoElement('͡'), PhoElement('ʊ')], 
        [PhoElement(' ')],
        [PhoElement('t'), PhoElement('͡'), PhoElement('s')],
        [PhoElement('ʧ')]
    ]
    
def test_phosegment():
    """Test PhoSegment."""
    
    with pytest.raises(ValueError):
        PhoSegment([PhoElement('ˌ').classify()])
        
    segment1 = PhoSegment([PhoDiacritic('ᵐ'), PhoConsonant('t')])
    
    assert segment1.string == 'ᵐt'
    assert segment1.base == [PhoConsonant('t')]
    assert segment1.components == [PhoDiacritic('ᵐ'), PhoConsonant('t')]
    assert segment1.left_diacritics == [PhoDiacritic('ᵐ')]
    assert segment1.right_diacritics == []
    
    segment2_components = [
        PhoDiacritic('ᶬ'), 
        PhoConsonant('h'),
        PhoDiacritic('̪'),
        PhoDiacritic('̯'),
        PhoDiacritic('̞'),
        PhoDiacritic('ʷ'),
        PhoDiacritic('ʴ'),
        PhoDiacritic('ʲ'),
        PhoDiacritic('ː')
    ]
    segment2 = PhoSegment(segment2_components)
    assert segment2.string =='ᶬh̪̯̞ʷʴʲː'
    assert segment2.base == [PhoConsonant('h')]
    assert segment2.components == segment2_components
    assert segment2.left_diacritics == [PhoDiacritic('ᶬ')]
    assert segment2.right_diacritics == [
        PhoDiacritic('̪'),
        PhoDiacritic('̯'),
        PhoDiacritic('̞'),
        PhoDiacritic('ʷ'),
        PhoDiacritic('ʴ'),
        PhoDiacritic('ʲ'),
        PhoDiacritic('ː')
    ]

def test_segment_generator():
    """Test segment generator."""
    seg_gen1 = segment_generator("ˌ‖|ᶬhi.oˡ")
    assert next(seg_gen1) == PhoSegment([PhoDiacritic('ᶬ'), PhoConsonant('h')])
    assert next(seg_gen1) == PhoSegment([PhoVowel('i')])
    assert next(seg_gen1) == PhoSegment([PhoVowel('o'), PhoDiacritic('ˡ')])