'''
ATTRIBUTION: Code by Olga Botvinnik
https://github.com/olgabot/kvector
'''
import six
import pandas as pd

DNA = 'ACGT'

def homer_motif_reader(handle, residues=DNA):
    """Read homer motifs output and return tuples of motif_id, motif_pwm

    Parameters
    ----------
    handle : file
        A Python opened file object
    residues : str
        Name of the residues
    """
    names = list(residues)
    record_id, record = None, ''
    for line in handle:
        if line.startswith('>'):
            new_record_id = line.lstrip('>').strip()
            if record_id is None:
                record_id = new_record_id
            if len(record) > 0:
                pwm = pd.read_table(six.StringIO(record), header=None,
                                    names=names)
                yield record_id, pwm
                record = ''
                record_id = new_record_id
        else:
            record += line


def read_motifs(filename, residues=DNA):
    """Wrapper to read a homer motif file

    Parameters
    ----------
    filename : str
        Name of the motif file to open
    residues : str

    Returns
    -------
    motifs : pandas.Series
        A series of dicts holding the name of the motif

    """
    with open(filename) as f:
        motifs = pd.Series(dict(homer_motif_reader(f, residues=residues)))
    return motifs

