# -*- coding:utf-8 -*-
"""
python version: 3.6+
ipa_map version: 0.1

Created on Saturday, Oct 10, 2022
Updated on Tuesday, January 2, 2024
$author: Philip Combiths

Reference, extract and manipulate IPA segments from a reference spreadsheet.

This script provides a framework for working with IPA segments and their
associated information. It defines classes for representing different types
of segments and provides a function for reading the IPA symbol table from a
CSV file.


Notes:
    A work in progress. ph_element is a working class with information 
    extracted from reference sheet for a given IPA character or character
    combination. Can also classify as consonant or vowel.

To Do:
 - Address problem with empty circle character in diacritic cells (e.g.,  ◌͜ )
 - Consider using Phon's Phone.java class
 - Reconsider relevance of tier attribute.

"""
import os

import pandas as pd

pkg_dir = os.path.dirname(__file__)
data_src = os.path.join(pkg_dir, 'IPA_Symbol_Table.csv')
def ipa_reference(data = data_src):
    """
    Reads a CSV file containing IPA symbols and their corresponding information
    and returns a pandas DataFrame with the data.

    Parameters:
        data (str): The path to the CSV file. Defaults to the `data_src` variable
            defined in this module.

    Returns:
        pandas.DataFrame: A DataFrame with the IPA symbols as the index and their
            corresponding information as columns.
    """
    ipa_df = pd.read_csv(data, index_col='Symbol')
    return ipa_df

# Create subsets of IPA sumbols. Currently not used.
ipa_df = ipa_reference()
consonants=ipa_df[(ipa_df['Type']=='Consonant')]
vowels=ipa_df[(ipa_df['Type']=='Vowel')]
ligatures=ipa_df[(ipa_df['Description']=='Affricate or double articulation')]
non_base_symbols=ipa_df[(ipa_df['Role']!='base')]
all_combining_symbols=ipa_df[(ipa_df['Role']!='diacritic_right') | (ipa_df['Role']!='diacritic_left')]
consonants2=ipa_df[(ipa_df['Role']=='base') & (ipa_df['Type']!='Vowel')]

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
        try:
            self.string=string
            self.tier=tier
            self.parent=parent
            self.position=position
            self.series=ipa_df.loc[[self.string]] # Get the row for the given string
            self.symbol=self.series.index[0]
            self.description=self.series['Description'].iloc[0]
            self.display = self.series['Symbol-Display'].iloc[0]
            self.name=self.series['Name'].iloc[0]
            self.unicode=self.series['Unicode'].iloc[0]
            self.type=self.series['Type'].iloc[0]
            self.role=self.series['Role'].iloc[0] # key for parsing
            self.voice=self.series['Voice'].iloc[0]
            self.place=self.series['Place'].iloc[0]
            self.manner=self.series['Manner'].iloc[0]
            self.sonority=self.series['Sonority'].iloc[0]
        except KeyError:
            self.series = None
            self.symbol = None
            self.description = None
            self.name = None
            self.unicode = None
            self.type = None
            self.role = None
            self.voice = None
            self.place = None
            self.manner = None
            self.sonority = None
            
    def ph_element_classify(self):
        if self.role=='base':
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
    
    # To Do
    # Take a string with multiple IPA input and break up into ph_segment components

# Define an IPA parser
def ipa_parser(input):
    """
    Take a string with multiple IPA input and break up into ph_segment components
    """
    # keep a memory of encountered segments until the next base segment is reached or end of input.
    # Then store completed segment to memory and reset segment_memory   
    memory = []
    segment_memory = []
    has_base = False
    segment_enders = ['base', 'diacritic_left', 'suprasegmental']
    for i, char in enumerate(input):
        if char in ipa_df.index:
            ph = ph_element(char)
            # If suprasegmental, append directly to memory without assigning to a segment.
            if ph.role == 'suprasegmental':
                memory.append(ph)
                #memory.append(ph.symbol) # debugging
                continue
            # If no base glyph yet, add to segment_memory
            if not has_base:
                segment_memory.append(ph)
                #segment_memory.append(ph.symbol) # debugging
                has_base = True
                continue
            # If base glyph already exists, determine if it's the end of a segment
            elif has_base:
                if ph.role in segment_enders:
                    memory.append(segment_memory)
                    segment_memory = [ph]
                    #segment_memory = [ph.symbol] # debugging
                    has_base = False

                else:
                    segment_memory.append(ph)
                    #segment_memory.append(ph.symbol) # debugging
                    continue
                
                # prepend any unattached left_diacritic characters already passed in iterator.
                # then continue with the next character
                pass
            
            if ph.role == 'diacritic_left' or ph.role == 'diacritic_right':
                # implement actions for diacritics
                # keep segment in memory
                pass

            if ph.role == 'diacritic_role-switcher':
                # implement actions for diacritic_role-switcher
                pass
            
            # TODO: Implement handling of compound phones and ligatures
        else:
            raise ValueError (f"Error: {char} not in reference ipa_df")
    memory.append(segment_memory) # Store final segment
    
    return memory
if __name__ == "__main__":
    result=ph_element('s')
    result2 = ph_element('̪')
    test0 = 'pʰ'
    test1 = 'pʰæt'   
    test2 = '၏'
    test3 = 'k̪ʰaˈʧu.ʧaː'
    test4 = 'k̪ʰⁿaˈʧ̥uᵊ.ã̬̝ˡː'
    

    ipa_parser(test4)
