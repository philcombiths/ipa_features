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
 - Add support for compound phones
 - Consider using Phon's Phone.java class
 - Reconsider relevance of tier, parent, position attributes throughout.

"""
import os
from typing import List

import pandas as pd

pkg_dir = os.path.dirname(__file__)
data_src = os.path.join(pkg_dir, 'IPA_Symbol_Table.csv')
def ipa_reference(data = data_src, index_col='Symbol'):
    """
    Reads a CSV file containing IPA symbols and their corresponding information
    and returns a pandas DataFrame with the data.

    Parameters:
        data (str): The path to the CSV file. Defaults to the `data_src` variable
            defined in this module. Must contain a specified index column.

    Returns:
        pandas.DataFrame: A DataFrame with the IPA symbols as the index and their
            corresponding information as columns.
    """
    ipa_df = pd.read_csv(data, index_col=index_col)
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
        # Initialize attributes
        if string.isspace():
            self.string = ' '
            self.symbol = ' '
            self.display = ' '
            self.description = 'Word boundary'
            self.name = 'Whitespace'
            self.type = 'Suprasegmental'
            self.role = 'boundary'
        else:
            self.string=string.strip()
            assert len(self.string)==1, f'ph_element string ({self.string}) must be a single character'
            self.tier=tier
            self.parent=parent
            self.position=position
            self.subclass=None
            try:
                self.series=ipa_df.loc[self.string] # Get pd.Series for the given string
            except KeyError:
                print(f'Warning: {self.string} not found in IPA_Symbol_Table.csv')
                self.series=None
                self.symbol=self.string
            self.symbol=self.series.name
            self.description=self.series.get('Description')
            self.display = self.series.get('Symbol-Display')
            self.name=self.series.get('Name')
            self.unicode=self.series.get('Unicode')
            self.type=self.series.get('Type')
            self.role=self.series.get('Role')

    # Built-in methods
    def __eq__(self, other):
        if isinstance(other, ph_element):
            return all(
                (
                    self.string == other.string,
                    self.symbol == other.symbol,
                    self.type == other.type,
                    self.role == other.role,
                    # add if equality to be specific to instance
                    # self.tier == other.tier,
                    # self.parent == other.parent, 
                    # self.position == other.position
                )
            )
        return NotImplemented


    def __ne__(self, other):
        if isinstance(other, ph_element):
            return all(
                (
                    self.string != other.string,
                    self.symbol != other.symbol,
                    self.type != other.type,
                    self.role != other.role,
                    # add if equality to be specific to instance
                    # self.tier != other.tier,
                    # self.parent != other.parent, 
                    # self.position != other.position
                )
            )
        return NotImplemented
    
    
    def __str__(self):
        return self.display
    
    
    def __repr__(self):
        return f"{type(self).__name__}(string={self.string}, tier={self.tier}, parent={self.parent}, position={self.position}, subclass={self.subclass})"
    
    
    def __len__(self):
        return len(self.string)
    
    
    def __getitem__(self, key: int) -> str: # To be tested. Should only permit number indexing
        # TODO: Implement position and parent information
        try:
            return ph_element(self.string[key])
        except TypeError as exc:
            if key in self.string:
                return ph_element(key)
            else:
                raise KeyError from exc
    
    # Class methods
    def classify(self):
        if self.role=='base':
            # TODO: Add support for compound phones. Currently classified as base.
            if self.type in ['Consonant', 'Implosive', 'Click']:
                return ph_consonant(self.string, tier=self.tier, parent=self.parent, position=self.position)
            if self.type=='Vowel':
                return ph_vowel(self.string, tier=self.tier, parent=self.parent, position=self.position)
        elif self.role in ['diacritic_right', 'diacritic_left']:
            return ph_diacritic(self.string, tier=self.tier, parent=self.parent, position=self.position)
        elif self.role=='compound_right':
            return ph_ligature(self.string, tier=self.tier, parent=self.parent, position=self.position)
        elif self.role=='boundary':
            return ph_boundary(self.string, tier=self.tier, parent=self.parent, position=self.position)
        elif self.role=='stress':
            return ph_stress(self.string, tier=self.tier, parent=self.parent, position=self.position)
        else:
            print('WARNING: ph_element unable to be classified')
            return self

## Marked for deletion
# class ph_suprasegmental(ph_element):
#     def __init__(self, string, tier='actual', parent=None, position=None): 
#         """
#         Generates a suprasegmental element.

#         Parameters:
#             string (str): A string of IPA characters in unicode utf-8, corresponding 
#                 to a single phoneme (including compound/combined phones and attached 
#                 diacritics)
#             tier (str): Designation as transcription target or transcription actual
#                 using Phon tier terminology. Of ['target', 'actual']. Default is 
#                 'actual'.
#             position (int): Position index
#         """
#         super().__init__(string, tier=tier, parent=parent, position=position)
#         self.subclass='ph_suprasegmental'
#         self.series = None
#         if self.string.isspace():
#             self.symbol = ' '
#             self.display = ' '
#             self.description = 'Word boundary'
#             self.name = 'Whitespace'
#             self.type = 'Suprasegmental'
#             self.role = 'suprasegmental'


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
        self.subclass='ph_base'


class ph_consonant(ph_base):
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
        super().__init__(string, tier=tier, parent=parent, position=position)
        self.subclass='ph_consonant'
        self.voice=self.series.get('Voice')
        self.place=self.series.get('Place')
        self.manner=self.series.get('Manner')
        self.sonority=self.series.get('Sonority')
        self.eml = self.series.get('EML')

class ph_vowel(ph_base):
    def __init__(self, string, tier='actual', parent=None, position=None):
        """
        Generates a vowel.

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
        self.subclass='ph_vowel'
        self.vowel_characteristics=None # To be implemented from Series


class ph_diacritic(ph_element):
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
        super().__init__(string, tier=tier, parent=parent, position=position)
        self.subclass='ph_diacritic'
        self.role_switcher=False # To be implemented (followed by role_switcher then True)
        self.attach_direction=None # To be implemented
        self.base=None # To be implemented
        
class ph_ligature(ph_element):
    # TODO: Consider as a subclass of ph_diacritic instead
    def __init__(self, string, tier='actual', parent=None, position=None): 
        """
        Generates a ligature or combining phonetic segment.

        Parameters:
            string (str): A string of IPA characters in unicode utf-8, corresponding 
                to a combining IPA element
            tier (str): Designation as transcription target or transcription actual
                using Phon tier terminology. Of ['target', 'actual']. Default is 
                'actual'.
            position (int): Position index
        """
        super().__init__(string, tier=tier, parent=parent, position=position)
        self.subclass='ph_ligature'
        self.role_switcher=False # To be implemented (followed by role_switcher then True)
        self.attach_direction='right' # To be implemented
        self.base=None # To be implemented (how to do compound base?)


class ph_boundary(ph_element):
    def __init__(self, string, tier='actual', parent=None, position=None): 
        """
        Generates a word, syllable, foot, or intonation boundary element.

        Parameters:
            string (str): A string of IPA characters in unicode utf-8, corresponding 
                to a combining IPA element.
            tier (str): Designation as transcription target or transcription actual
                using Phon tier terminology. Of ['target', 'actual']. Default is 'actual'
        """
        super().__init__(string, tier=tier, parent=parent, position=position)
        self.subclass='ph_boundary'
        
class ph_stress(ph_element):
    def __init__(self, string, tier='actual', parent=None, position=None): 
        """
        Generates a stress element.

        Parameters:
            string (str): An IPA character in unicode utf-8, corresponding 
                to a stress marker.
            tier (str): Designation as transcription target or transcription actual
                using Phon tier terminology. Of ['target', 'actual']. Default is 
                'actual'.
            position (int): Position index
        """
        super().__init__(string, tier=tier, parent=parent, position=position)
        self.subclass='ph_stress'


class ph_segment(ph_element):
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
        super().__init__(string, tier=tier, parent=parent, position=position)
        self.subclass='ph_segment'
        self.base=None # To be implemented
        self.diacritics=None # To be implemented
        self.right_diacritics=None # To be implemented
        self.left_diacritics=None # To be implemented
        self.stress=None # To be implemented
        self.syllable=None # To be implemented
        self.word=None # To be implemented

    # To Do:
    # def strip():
    # def get_base():
    # def get_diacritics():

def ipa_parser(input: str) -> List[List[ph_element]]:
    """
    Parse a string of IPA characters into component segments.
    
    More Details:
    Take a string with multiple IPA input and break up into ph_segment components.
    Keep a memory of encountered segments until the next base segment is reached or
    end of input. Then store completed segment to memory and reset segment_memory.

    Args:
        input_str (str): A string of IPA characters.

    Returns:
        list: A list of ph_segment objects representing the parsed segments.

    """
    # Initialize variables
    memory: List[List[ph_element]] = []
    segment_memory: List[ph_element] = []
    last_char_memory: str = ""
    has_base: bool = False
    word_count: int = 1
    
    segment_enders: List[str] = ['base', 'diacritic_left', 'boundary', 'stress']
    
    # Parse input character by character
    for i, char in enumerate(input.strip()): # i is for unimplemented position counter
        pass
        if i == 32:
            pass
        if char.isspace():
            if last_char_memory.isspace():
                continue
            else:
                memory.append(segment_memory) # Also starts new segment
                segment_memory = []
                has_base = False
                word_count += 1
                memory.append([ph_boundary(' ')]) # space indicates word boundary
                last_char_memory = char
                continue
        
        if char in ipa_df.index:
            ph = ph_element(char)
                
            # If boundary or stress marker, append directly to memory without assigning to a segment.
            if ph.role in ['boundary', 'stress']:
                memory.append(segment_memory) # Also starts new segment
                segment_memory = []
                memory.append([ph])
                #memory.append(ph.symbol) # debugging
                has_base = False
                last_char_memory = char
                continue
            
            # If no base glyph yet, add to segment_memory
            if not has_base:
                segment_memory.append(ph)
                #segment_memory.append(ph.symbol) # debugging
                if ph.role == 'base':
                    has_base = True
                last_char_memory = char
                continue
            
            # If base glyph already exists
            else:
                # Determine if it's the end of a segment, then add to memory and start new segment
                if ph.role in segment_enders:
                    memory.append(segment_memory)
                    segment_memory = [ph]
                    #segment_memory = [ph.symbol] # debugging
                    has_base = True
                    last_char_memory = char
                    continue
                    
                # If not end of segment, add to segment_memory
                else:
                    segment_memory.append(ph)
                    #segment_memory.append(ph.symbol) # debugging
                    last_char_memory = char
                    continue
            
            if ph.role == 'diacritic_left' or ph.role == 'diacritic_right':
                ## Candidate for deletion. No special actions needed for diacritics
                # implement actions for diacritics
                # keep segment in memory
                pass

            # TODO: Implement handling of role-switched diacritics
            if ph.role == 'diacritic_role-switcher':
                # implement actions for diacritic_role-switcher
                pass
            
            # TODO: Implement handling of compound phones and ligatures
        else:
            raise ValueError (f"Error: {char} not in reference ipa_df")
    memory.append(segment_memory) # Store final segment
    debug = [[i.symbol for i in row] for row in memory] # debug
    return memory

if __name__ == "__main__":
    result=ph_element('s')
    result2 = ph_element('̪')
    result3 = ph_element(' ')
    test0 = 'pʰ'
    test1 = 'pʰæt'
    test2 = '၏' # illegal characters
    test3 = 'k̪ʰaˈʧu.ʧaː'
    test4 = 'k̪ʰⁿaˈʧ̥uᵊ.ã̬̝ˡː'
    test5 = 'k̪ʰⁿaˈʧ̥uᵊ.ã̬̝ˡː     pʰæt\nkʰaʧ suto'
    
    output = ipa_parser(test5)
    pass
