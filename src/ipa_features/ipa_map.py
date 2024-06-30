# -*- coding:utf-8 -*-
"""
python version: 3.6+
ipa_map version: 0.2

Created on Oct 10, 2022
Updated on Jun 30, 2024
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
import logging
import os
from typing import List

import pandas as pd

from ipa_features.logging_config import setup_logging

_logger = logging.getLogger(__name__)
setup_logging(logging.DEBUG)

pkg_dir = os.path.dirname(__file__)
data_src = os.path.join(pkg_dir, "IPA_Symbol_Table.csv")


def ipa_reference(data=data_src, index_col="Symbol"):
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
    ipa_map_df = pd.read_csv(data, index_col=index_col)
    return ipa_map_df


ipa_df = ipa_reference()

# # Create subsets of IPA symbol map. Currently not used.
# consonants = ipa_df[(ipa_df["Type"] == "Consonant")]
# vowels = ipa_df[(ipa_df["Type"] == "Vowel")]
# ligatures = ipa_df[(ipa_df["Description"] == "Affricate or double articulation")]
# non_base_symbols = ipa_df[(ipa_df["Role"] != "base")]
# all_combining_symbols = ipa_df[
#     (ipa_df["Role"] != "diacritic_right") | (ipa_df["Role"] != "diacritic_left")
# ]
# consonants2 = ipa_df[(ipa_df["Role"] == "base") & (ipa_df["Type"] != "Vowel")]


class PhoElement:
    """
    Represents a phonetic element.

    Attributes:
        - string: A single string IPA character or combined character in unicode utf-8.
        - subclass: The subclass of the element.
        - series: The corresponding series in the IPA_Symbol_Table.csv file.
        - role: The role of the element, specific to this package, such as 'base', 'boundary', etc.
        - display: The display string of the element, extracted from Phon.
        - description: The description of the element, extracted from Phon.
        - name: The name of the element, extracted from Phon.
        - type: The type of the element, extracted from Phon.
        - symbol: The symbol of the element, used as index in ipa_df.
        - unicode: The unicode value(s) of the element, extracted from Phon.
        TODO: Implement these dummy attributes:
            - tier: Designated Phon transcription tier. Should be one of ['target', 'actual'].
                    Default is 'actual'. Not implemented.
            - parent: The parent element. Not implemented.
            - position: The position of the element. Not implemented.
            - role_switcher: A boolean that indicates if the role should be switched to the opposite
                             direction. Not implemented.
            - attach_direction: A string, 'right', or 'left', indicating if the element should be
                                attached to the right or left of the base. Not implemented.
    """

    def __init__(self, string, tier="actual", parent=None, position=None):
        # Initialize attributes
        if string.isspace():
            self.string = " "
            self.symbol = " "
            self.display = " "
            self.description = "Word boundary"
            self.name = "Whitespace"
            self.type = "Suprasegmental"
            self.role = "boundary"
            self.subclass = None
        else:
            self.string = string.strip()
            assert (
                len(self.string) == 1
            ), f"ph_element string ({self.string}) must be a single character"
            self.tier = tier
            self.parent = parent
            self.position = position
            self.subclass = None
            try:
                self.series = ipa_df.loc[
                    self.string
                ]  # Get pd.Series for the given string
            except KeyError:
                print(f"Warning: {self.string} not found in IPA_Symbol_Table.csv")
                self.series = None
                self.symbol = self.string
            self.symbol = self.series.name
            self.description = self.series.get("Description")
            self.display = self.series.get("Symbol-Display")
            self.name = self.series.get("Name")
            self.unicode = self.series.get("Unicode")
            self.type = self.series.get("Type")
            self.role = self.series.get("Role")

    def __str__(self):
        return self.display

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}"
            f"(string={self.string!r}, "
            f"tier={self.tier!r}, "
            f"parent={self.parent!r}, "
            f"position={self.position!r}, "
            f"subclass={self.subclass!r})"
        )

    def __len__(self):
        return len(self.string)

    def __eq__(self, other):
        if isinstance(other, PhoElement):
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
        if isinstance(other, PhoElement):
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

    def __getitem__(
        self, key: int
    ) -> str:  # To be tested. Should only permit number indexing
        # TODO: Implement position and parent information
        try:
            return PhoElement(self.string[key])
        except TypeError as exc:
            if key in self.string:
                return PhoElement(key)
            else:
                raise KeyError from exc

    # Class methods
    def classify(self):
        if self.role == "base":
            # TODO: Add support for compound phones. Currently classified as base.
            if self.type in ["Consonant", "Implosive", "Click"]:
                return PhoConsonant(
                    self.string,
                    tier=self.tier,
                    parent=self.parent,
                    position=self.position,
                )
            if self.type == "Vowel":
                return PhoVowel(
                    self.string,
                    tier=self.tier,
                    parent=self.parent,
                    position=self.position,
                )
        elif self.role in ["diacritic_right", "diacritic_left"]:
            return PhoDiacritic(
                self.string, tier=self.tier, parent=self.parent, position=self.position
            )
        elif self.role == "compound_right":
            return PhoLigature(
                self.string, tier=self.tier, parent=self.parent, position=self.position
            )
        elif self.role == "boundary":
            return PhoBoundary(
                self.string, tier=self.tier, parent=self.parent, position=self.position
            )
        elif self.role == "stress":
            return PhoStress(
                self.string, tier=self.tier, parent=self.parent, position=self.position
            )
        else:
            print("WARNING: ph_element unable to be classified")
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


class PhoBase(PhoElement):
    def __init__(self, string, tier="actual", parent=None, position=None):
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
        self.subclass = "ph_base"


class PhoConsonant(PhoBase):
    def __init__(self, string, tier="actual", parent=None, position=None):
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
        self.subclass = "ph_consonant"
        self.voice = self.series.get("Voice")
        self.place = self.series.get("Place")
        self.manner = self.series.get("Manner")
        self.sonority = self.series.get("Sonority")
        self.eml = self.series.get("EML")


class PhoVowel(PhoBase):
    def __init__(self, string, tier="actual", parent=None, position=None):
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
        self.subclass = "ph_vowel"
        self.vowel_characteristics = None  # To be implemented from Series


class PhoDiacritic(PhoElement):
    def __init__(self, string, tier="actual", parent=None, position=None):
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
        self.subclass = "ph_diacritic"
        self.role_switcher = (
            False  # To be implemented (followed by role_switcher then True)
        )
        self.attach_direction = None  # To be implemented
        self.base = None  # To be implemented


class PhoLigature(PhoElement):
    # TODO: Consider as a subclass of ph_diacritic instead
    def __init__(self, string, tier="actual", parent=None, position=None):
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
        self.subclass = "ph_ligature"
        self.role_switcher = (
            False  # To be implemented (followed by role_switcher then True)
        )
        self.attach_direction = "right"  # To be implemented
        self.base = None  # To be implemented (how to do compound base?)


class PhoBoundary(PhoElement):
    def __init__(self, string, tier="actual", parent=None, position=None):
        """
        Generates a word, syllable, foot, or intonation boundary element.

        Parameters:
            string (str): A string of IPA characters in unicode utf-8, corresponding
                to a combining IPA element.
            tier (str): Designation as transcription target or transcription actual
                using Phon tier terminology. Of ['target', 'actual']. Default is 'actual'
        """
        super().__init__(string, tier=tier, parent=parent, position=position)
        self.subclass = "ph_boundary"


class PhoStress(PhoElement):
    def __init__(self, string, tier="actual", parent=None, position=None):
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
        self.subclass = "ph_stress"


class PhoSegment(PhoElement):
    def __init__(self, string, tier="actual", parent=None, position=None):
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
        self.subclass = "ph_segment"
        self.base = None  # To be implemented
        self.diacritics = None  # To be implemented
        self.right_diacritics = None  # To be implemented
        self.left_diacritics = None  # To be implemented
        self.stress = None  # To be implemented
        self.syllable = None  # To be implemented
        self.word = None  # To be implemented

    # To Do:
    # def strip():
    # def get_base():
    # def get_diacritics():


def ipa_parser(input_str: str) -> List[List[PhoElement]]:
    """
    Parse a string of IPA characters into component segments.

    Details:
    Take a string with multiple IPA input and break up into ph_segment components.
    Keep a memory of encountered segments until the next base segment is reached or
    end of input. Then store completed segment to memory and reset segment_memory.

    Args:
        input_str (str): A string of IPA characters.

    Returns:
        list: A list of ph_segment objects representing the parsed segments.

    """
    # Initialize variables
    transcript_memory: List[List[PhoElement]] = []
    seg_memory: List[PhoElement] = []
    last_char_memory: str = ""
    has_base: bool = False
    word_count: int = 1
    segment_enders: List[str] = ["base", "diacritic_left", "boundary", "stress"]
    _logger.info("Initializing variables")

    # Parse input character by character
    for i, char in enumerate(
        input_str.strip()
    ):  # i is unimplemented position counter / used for debugging
        _logger.info("Parsing character %s: %s", i, char)
        if char.isspace():
            if last_char_memory.isspace():
                continue
            transcript_memory.append(seg_memory)  # Also starts new segment
            seg_memory = []
            has_base = False
            word_count += 1
            transcript_memory.append([PhoBoundary(" ")])  # space indicates word boundary
            last_char_memory = char
            continue

        if char in ipa_df.index:
            ph = PhoElement(char)
            _logger.info("\tph_element object created for %s", char)
            # If boundary or stress marker, append directly to memory without assigning to a segment.
            if ph.role in ["boundary", "stress"]:
                if not has_base:
                    transcript_memory.append([ph])  # Store as own segment directly.
                    _logger.info("\tBoundary/stress stored to memory")
                else:
                    transcript_memory.append(seg_memory)  # End last segment and store
                    _logger.info("\tBoundary/stress indicates end of last segment")
                    has_base = False
                    seg_memory = []
                    _logger.info("****Segment memory cleared.****")
                    transcript_memory.append([ph])  # Store as own segment directly
                    _logger.info("\tBoundary/stress stored to memory")
                last_char_memory = char
                continue

            # If no base glyph yet, add to segment_memory
            if not has_base:
                seg_memory.append(ph)
                if ph.role == "base":  # if base, set has_base to True
                    has_base = True
                last_char_memory = char
                _logger.info("\tAdded to segment memory")
                continue

            # If base for the segment already exists, check if end of the segment
            if ph.role in segment_enders:
                transcript_memory.append(seg_memory)
                _logger.info("\tPrevious segment complete. Added to memory.")
                seg_memory = [ph]
                _logger.info("****Segment memory cleared.****")
                _logger.info("\tCharacter: %s added to segment memory.", char)
                has_base = ph.role == "base"  # Simplified if-statement
                last_char_memory = char
                continue

            # If not end of segment, add to seg_memory
            seg_memory.append(ph)
            last_char_memory = char
            _logger.info("\tAdded to existing segment memory.")
            continue

            # TODO: Implement handling of role-switched diacritics
            # if ph.role == "diacritic_role-switcher":
            #     # implement actions for diacritic_role-switcher
            #     pass

            # TODO: Implement handling of compound phones and ligatures
            # Code goes here
            
        _logger.error("Error: %s not in reference ipa_df", char)
        raise ValueError(f"Error: {char} not in reference ipa_df")

    transcript_memory.append(seg_memory)  # Store final segment
    _logger.info("\tComplete segment stored to memory.")
    memory_debug = [[i.symbol for i in row] for row in transcript_memory]
    _logger.debug("Memory dump: %s", memory_debug)
    return transcript_memory


if __name__ == "__main__":
    result1 = PhoElement("s")
    result2 = PhoElement("̪")
    result3 = PhoElement(" ")
    test0 = "pʰ"
    test1 = "pʰæt"
    test2 = "၏"  # illegal characters
    test5 = "k̪ʰⁿaˈʧ̥uᵊ.ã̬̝ˡː     pʰæt\nkʰaʧ suto"
    test6 = "kʰⁿaˈʧ̥u"
    test7 = "ⁿaˈʧ̥ukʰⁿaˈʧ̥"
    test8 = "ˌ‖|ᶬhi.toˡˈ|ᵐtə̃"

    output = ipa_parser(test8)
    pass
