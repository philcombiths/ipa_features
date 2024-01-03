# -*- coding:utf-8 -*-
"""
python version: 3.6+
ipa_map version: 0.1

Created on Saturday, Oct 10, 2022
Updated on Tuesday, January 2, 2024
$author: Philip Combiths

Reference, extract and manipulate IPA segments from a reference spreadsheet.

Notes:
    A work in progress. ph_element is a working class with information 
    extracted from reference sheet for a given IPA character or character
    combination. Can also classify as consonant or vowel.

    Reconsider relevance of tier attribute.
"""
import os

import pandas as pd

pkg_dir = os.path.dirname(__file__)
data_src = os.path.join(pkg_dir, 'IPA_Symbol_Table.csv')
def ipa_ref(data = data_src):
    ipa_df = pd.read_csv(data, index_col='Symbol')
    return ipa_df

ipa_ref = ipa_ref()
consonants=ipa_ref[(ipa_ref['Type']=='Consonant')]
vowels=ipa_ref[(ipa_ref['Type']=='Vowel')]
ligatures=ipa_ref[(ipa_ref['Description']=='Affricate or double articulation')]
non_base_symbols=ipa_ref[(ipa_ref['Base-Diacritic']!='base')]
all_combining_symbols=ipa_ref[(ipa_ref['Base-Diacritic']!='diacritic_right') | (ipa_ref['Base-Diacritic']!='diacritic_left')]
consonants=ipa_ref[(ipa_ref['Base-Diacritic']=='base') & (ipa_ref['Type']!='Vowel')]

class ph_element:
    def __init__(self, string, tier='actual', parent=None, position=None): 
        """
        Generates a segment

        Parameters:
            string (str): A single string IPA character or combined chaaracter 
            in unicode utf-8
            tier (str): Designation as transcription target or transcription actual
                using Phon tier terminology. Of ['target', 'actual']. Default is 
                'actual'.
            position (int): Position index
        """
        self.string=string
        self.tier=tier
        self.parent=parent
        self.position=position
        self.series=ipa_ref.loc[[self.string]]
        self.symbol=self.series.index[0]
        self.description=self.series['Description'].iloc[0]
        self.name=self.series['Name'].iloc[0]
        self.unicode=self.series['Unicode'].iloc[0]
        self.type=self.series['Type'].iloc[0]
        self.base_diacritic=self.series['Base-Diacritic'].iloc[0]
        self.voice=self.series['Voice'].iloc[0]
        self.place=self.series['Place'].iloc[0]
        self.manner=self.series['Manner'].iloc[0]
        self.sonority=self.series['Sonority'].iloc[0]

    def ph_element_classify(self):
        if self.base_diacritic=='base':
            self = ph_base(
                self.string, tier=self.tier, parent=self.parent, position=self.position)
        else:
            self = ph_diacritic(
                self.string, tier=self.tier, parent=self.parent, position=self.position)
        return self
    

class ph_base(ph_element):
    def __init__(self, string, tier='actual', parent=None, position=None): 
        """
        Generates a base phonetic segment.

        Parameters:
            string (str): A string of IPA characters in unicode utf-8, corresponding 
                to a single phoneme (including compound/combined phones and attached 
                diacritics)
            tier (str): Designation as transcription target or transcription actual
                using Phon tier terminology. Of ['target', 'actual']. Default is 
                'actual'.
            position (int): Position index
        """
        super().__init__(string, tier=tier, parent=parent, position=position)
        self.string=string
        self.tier=tier
        self.parent=parent
        self.position=position


class consonant(ph_base):
    def __init__(self, string, tier='actual', parent=None, position=None): 
        """
        Generates a base consonant.

        Parameters:
            string (str): A string of IPA characters in unicode utf-8, corresponding 
                to a single phoneme (including compound/combined phones and attached 
                diacritics)
            tier (str): Designation as transcription target or transcription actual
                using Phon tier terminology. Of ['target', 'actual']. Default is 
                'actual'.
            position (int): Position index
        """
    
        self.string=string
        self.tier=tier
        self.parent=parent
        self.position=position


class ph_diacritic(ph_base):
    def __init__(self, string, tier='actual', parent=None, position=None): 
        """
        Generates a diacritic or combining phonetic segment.

        Parameters:
            string (str): A string of IPA characters in unicode utf-8, corresponding 
                to a combining IPA element
            tier (str): Designation as transcription target or transcription actual
                using Phon tier terminology. Of ['target', 'actual']. Default is 
                'actual'.
            position (int): Position index
        """
        self.string=string
        self.tier=tier
        self.parent=parent
        self.position=position

class ph_segment:
    def __init__(self, string, tier='actual', parent=None, position=None): 
        """
        Generates a segment.

        Parameters:
            string (str): A string of IPA characters in unicode utf-8, corresponding 
                to a single phoneme (including compound/combined phones and attached 
                diacritics)
            tier (str): Designation as transcription target or transcription actual
                using Phon tier terminology. Of ['target', 'actual']. Default is 
                'actual'.
            position (int): Position index
        """
        self.string=string
        self.tier=tier
        self.parent=parent
        self.position=position
        if isinstance(self, ph_segment):
            self.type = "segment"
    # To Do:
    # def strip():
    # def get_base():
    # def get_diacritics():


if __name__ == "__main__":
    result=ph_element('s')
    print(result.ph_element_classify())
    pass