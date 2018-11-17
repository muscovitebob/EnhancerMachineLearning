import pandas as pd
import io

class cbust_result:
    '''
    This class represents cbust output and provides methods to filter it. Only f1 and f3 type output is supported.
    '''
    def __init__(self, **kwargs):
        '''
        Input must be a dictionary
        :param cbust_output_filepath: output matrix that is in the f1 or f3 matrix formats
        :param jaspar_matrix_filepath: path to the original motif matrix used for cluster discovery as input to cbust
        '''
        self.input_matrix_type = kwargs.get("input_matrix_type")
        self.cbust_output_filepath = kwargs.get("cbust_output_filepath")
        self.jaspar_matrix_filepath = kwargs.get("jaspar_matrix_filepath")

        if self.input_matrix_type == "f1":
            self._from_f1(self.cbust_output_filepath)
        elif self.input_matrix_type == "f3":
            self._from_f3(self.cbust_output_filepath)
        else:
            raise NotImplementedError

        self.motif_names = list(self.f3_cbust_matrix.columns)[4:]
        self.jaspar_matrix_dict = self._read_jaspar_to_dict_of_names_and_pandas(self.jaspar_matrix_filepath)

    def _from_f3(self, f3_output_filepath):
        self.f3_cbust_matrix = pd.read_csv(f3_output_filepath, error_bad_lines=False, sep='\t', skiprows=3,
                                          skipfooter=9, engine='python')
        self.cbust_run_info = pd.read_csv(f3_output_filepath, error_bad_lines=False)[-8:]
        self.motif_names = list(self.f3_cbust_matrix.columns)[4:]

    def _from_f1(self, f1_output_filepath):
        '''
        LOGIC: We read a huge f1 file in line by line. We detect where matrices start and end.
        We pass the positions to an assistant function, which reads everything between these positions
        into a pandas data frame using pd.read_csv. The assistant function takes the matrix name out and adds it
        and the contents to a dict of all the matrices read so far.
        TODO: implement the description
        :param f1_output_filepath:
        :return:
        '''
        with open(f1_output_filepath, "r") as f1_file:
            in_matrix = False
            for line in f1_file:
                if line == "\n":
                    continue
                elif line.startswith(">"):
                    in_matrix = True
                    startpos = f1_file.tell()
                    continue
                elif line.isdigit() and in_matrix == True:
                    continue
                elif line == "\n" and in_matrix == True:
                    endpos = f1_file.tell()
                    in_matrix = False
                    self._pull_matrix_from_positions(startpos, endpos, f1_output_filepath)
                else:
                    continue


    def _pull_matrix_from_positions(self, startpos, endpos, f1_output_filepath):
        '''
        TODO: implement
        :param startpos:
        :param endpos:
        :return:
        '''
        self.f1_matrix_dict = {}
        current_matrix = pd.read_csv(f1_output_filepath, error_bad_lines=False, sep='\t',
                                     skiprows=startpos-1,
                                     skipfooter=endpos, engine='python')




    def calculate_reliable_motif_dict(self, motif_threshold, cluster_threshold):
        '''
        Getter for the reliable motif dictionary.
        :param motif_threshold: motif score to take equal or over
        :param cluster_threshold: cluster score to take equal or over
        :return: reliable motif dictionary
        '''
        return self._create_reliable_motif_dict(
            self._retrieve_reliable_motifs(motif_threshold, cluster_threshold)
        )

    @staticmethod
    def write_reliable_motif_matrix(reliable_motif_dict, motif_matrix_filename):
        '''
        Writes the reliable motif dictionary to a jaspar motif matrix file
        :param reliable_motif_dict:
        :return: nothing; writes to disk
        '''
        # caveat: the new matrix file is written using cbust internal identifiers (which are shortened motif names)
        # not the identifier used in the original jaspar matrix. Should be sufficiently unique anyway.
        with open(motif_matrix_filename, "w") as motif_matrix:
            for motif_name, motif in reliable_motif_dict.items():
                motif_matrix.write(">" + str(motif_name) + "\n")
                for row_number in range(0, len(motif)):
                    current_row = motif.iloc[row_number]
                    for nucleotide_column in range(0, 4):
                        if nucleotide_column <= 2:
                            motif_matrix.write(str(current_row[nucleotide_column]) + "\t")
                        else:
                            motif_matrix.write(str(current_row[nucleotide_column]) + "\t\n")
        motif_matrix.close()

    @property
    def get_jaspar_input_dict(self):
        '''
        Getter for the input motif matrix that was originally fed to clusterbuster, in a dict format
        :return:
        '''
        return self.jaspar_matrix_dict

    @property
    def get_cbust_f3_matrix(self):
        '''
        Getter for the full clusterbuster -f 3 matrix
        :return:
        '''
        return self.f3_cbust_matrix

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
        cluster_reduced = self.f3_cbust_matrix.loc[self.f3_cbust_matrix['# Score'] >= cluster_threshold]
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



