import pandas as pd
import io

class cbust_result:
    '''
    This class represents cbust output and provides methods to filter it
    '''
    def __init__(self, f3_output_filepath, jaspar_matrix_filepath):
        self.primary_cbust_matrix = pd.read_csv(f3_output_filepath, error_bad_lines=False, sep='\t', skiprows=3, skipfooter=9)
        self.cbust_run_info = pd.read_csv("cbust_example/f3results.txt", error_bad_lines=False)[-8:]
        self.motif_names = list(self.primary_cbust_matrix.columns)[4:]
        self.jaspar_matrix_dict = self._read_jaspar_to_dict_of_names_and_pandas(jaspar_matrix_filepath)
        # caveats: the identifier in the cbust matrix and the dict are not necessarily the same
        # cbust mangles motif identifiers according to its own internal rules

    def get_reliable_motif_dict(self, motif_threshold, cluster_threshold):
        '''
        Getter for the reliable motif dictionary.
        :param motif_threshold: motif score to take equal or over
        :param cluster_threshold: cluster score to take equal or over
        :return: reliable motif dictionary
        '''
        return self._create_reliable_motif_dict(
            self._retrieve_reliable_motifs(motif_threshold, cluster_threshold)
        )

    def get_jaspar_input_dict(self):
        '''
        Getter for the input motif matrix that was originally fed to clusterbuster, in a dict format
        :return:
        '''
        return self.jaspar_matrix_dict

    def get_cbust_f3_matrix(self):
        '''
        Getter for the clusterbuster
        :return:
        '''

    def _read_jaspar_to_dict_of_names_and_pandas(self, jaspar_matrix_filepath):
        '''
        Creates a dictionary with name : motif matrix of all motif matrices used in a cbust run
        :param jaspar_matrix_filepath: path to the input motif matrix list given to cbust
        :return: dictionary of name : motif matrix pairs
        '''
        jaspar_matrix_dict = dict()
        with open(jaspar_matrix_filepath) as jaspar_monolith:
            content = jaspar_monolith.read()
            one_matrix_per_string = content.split(sep=">")
            for i in range(1, len(one_matrix_per_string)):
                first = one_matrix_per_string[i]
                first1 = first.split("\n")
                jaspar_name_full = first1[0]
                jaspar_name = jaspar_name_full.split()[0]
                first2 = '\n'.join(first1[1:])
                jaspar_matrix = pd.read_table(io.StringIO(first2), sep="\t",
                                              index_col=False, header=None, names=['A', 'C', 'G', 'T'])
                jaspar_matrix_dict[jaspar_name] = jaspar_matrix
        jaspar_monolith.close()
        return jaspar_matrix_dict

    def _retrieve_reliable_motifs(self, motif_threshold, cluster_threshold):
        '''
        Returns a set of unique reliable motif identifiers, judged by score thresholds.
        :param motif_threshold: motif score to take equal or over
        :param cluster_threshold: cluster score to take equal or over
        :return: set of motif identifiers
        '''
        cluster_reduced = self.primary_cbust_matrix.loc[self.primary_cbust_matrix['# Score'] >= cluster_threshold]
        identifier_set = set()
        for i in range(0, len(cluster_reduced.index)):
            slice = cluster_reduced.iloc[i, ]
            sliceonlyscores = slice[4:]
            slicethresholded = sliceonlyscores[sliceonlyscores >= motif_threshold]
            identifier_set.update(list(slicethresholded.index))
        return identifier_set

    def _create_reliable_motif_dict(self, identifier_set):
        '''
        Creates a dictionary of reliable motif matrices using a set of motif identifiers.
        :type identifier_set set
        :return: dictionary of reliable motifs, cbust abbreviated name : data frame of the motif
        '''
        reliable_motif_dict = {}
        for key in identifier_set:
            try:
                reliable_motif_dict[key] = self.jaspar_matrix_dict.get(key)
            except Exception:
                pass
        return reliable_motif_dict

    def _write_reliable_motif_matrix(self, reliable_motif_dict):
        '''
        Writes the reliable motif dictionary to a jaspar motif matrix file
        :param reliable_motif_dict:
        :return: nothing; writes to disk
        '''
        # TO BE IMPLEMENTED








