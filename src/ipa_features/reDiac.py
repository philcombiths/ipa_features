"""
Generate regex pattern to locate diacritics.
    Derived from PhonoErrorPatterns\diacritics.py
Created on Saturday, October 1, 2022
@author: Philip Combiths
"""

import csv
from tokenize import StringPrefix
import regex as re
import os
import pandas.io.clipboard as pyperclip
from regex_find_generator import regex_find_generator

def reDiac(diacritic_key="Phon", to_clipboard=False): 
    """   
    Generate regex pattern to locate diacritics.
    
    Args:
        diacritic_key : str in ['Phon', 'unicode_blocks', 'all'] to specify key type
            for generation of diacritic regex pattern. Default='Phon'
        to_clipboard (bool, optional): Copy resultant pattern as string to
        clipboard. Defaults to False.
            
    Requires:
        regex module as re
    
    Returns:
        compiled regex pattern
    
    *Revised from PhonDPA\auxiliary.py
    """   
    
    # For UnicodeBlocks
    unicodeBlockList = [r'\p{InCombining_Diacritical_Marks_for_Symbols}',
                        r'\p{InSuperscripts_and_Subscripts}',
                        r'\p{InCombining_Diacritical_Marks}',
                        r'\p{InSpacing_Modifier_Letters}',
                        r'\p{InCombining_Diacritical_Marks_Extended}'
                        r'\p{InCombining_Diacritical_Marks_Supplement}']
    additionalChars = [r'ᴸ', r'ᵇ', r':', r'<', r'←', r'=', r"'", r"‚", r"ᵊ"]
    
    # For Phon
    regex_special_chars = ['*', '+', '^','$', '.','|', #'\\',
                           '?', '{', '}', '[', ']', '(', ')'] 
    with open("phon_diacritics.csv", mode="r", encoding='utf-8') as f:
        file = csv.reader(f)
        phon_diacritics = [x[0] for x in file]
        
    phon_diacritics = ["\\"+x if x in regex_special_chars else x for x in phon_diacritics]
    
    # Apply specified diacritics key
    if diacritic_key == "Phon":
        pattern = r'(' + r'|'.join(phon_diacritics) + r')'
    if diacritic_key == "unicode_blocks":
        pattern = r'(' + r'|'.join(unicodeBlockList+additionalChars) + r')'
    if diacritic_key == "all":
        pattern = r'(' + r'|'.join(phon_diacritics+unicodeBlockList+additionalChars) + r')'
    pattern_compiled = re.compile(pattern)
    # Copy uncompiled regex search string to clipboard
    if to_clipboard:
        pyperclip.copy(pattern)
    # Return compiled regex search  
    return pattern_compiled
