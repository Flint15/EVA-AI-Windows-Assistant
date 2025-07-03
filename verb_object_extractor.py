from typing import Union
import spacy
import string
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info('nlp data loading...')

nlp = spacy.load('en_core_web_sm')

logger.info('nlp data was loaded!')

class Extractor():
    def __init__(self):
        pass

    def extract_verb_object(self, command: str) -> tuple:
        """
        Extracts the main verb and its direct object from the command
        """
        doc = nlp(command)
        
        verb = None
        obj = None

        for token in doc:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                verb = token
                break  # Assume one main verb per command

        for token in doc:
            if token.dep_ == 'prt' and token.head.text == verb:
                verb = f'{verb} {token.text}'

        # Next, look for the direct object associated with the found verb
        if verb:
            for token in doc:
                if token.dep_ in ("dobj", "obj") and token.head == verb:
                    obj = token
                    break

        verb, obj = verb.text if verb else None, obj.text if obj else None

        if verb and obj != None:
            logger.info(f'Verb - "{verb}" and Object - "{obj}" were successfully define and extracted!')
            
            return verb, obj

        logger.info(f'Verb - "{verb}" and Object - "{obj}" weren\'t defined')

        return ('Verb and Object weren\'t defined', None)
