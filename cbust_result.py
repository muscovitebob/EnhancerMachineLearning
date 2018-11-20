import pandas as pd
import io

class cbust_result:
    '''
    This class represents cbust output and provides methods to filter it. Only f1 and f3 type output is supported.
    '''
    def __init__(self, cbust_output_filepath, input_matrix_type, jaspar_matrix_filepath):
        '''
        :param cbust_output_filepath: output matrix that is in the f1 or f3 matrix formats
        :param jaspar_matrix_filepath: path to the original motif matrix used for cluster discovery as input to cbust
        '''
        self.cbust_output_filepath = cbust_output_filepath
        self.input_matrix_type = input_matrix_type
        self.jaspar_matrix_filepath = jaspar_matrix_filepath

        if self.input_matrix_type == "f1":
            self.matrix_type = "f1"
            self._from_f1(self.cbust_output_filepath)
        elif self.input_matrix_type == "f3":
            self.matrix_type = "f3"
            self._from_f3(self.cbust_output_filepath)
            self.motif_names = list(self.f3_cbust_matrix.columns)[4:]
            self.jaspar_matrix_dict = self._read_jaspar_to_dict_of_names_and_pandas(self.jaspar_matrix_filepath)
        else:
            raise NotImplementedError

    def _from_f3(self, f3_output_filepath):
        self.f3_cbust_matrix = pd.read_csv(f3_output_filepath, error_bad_lines=False, sep='\t', skiprows=3,
                                          skipfooter=9, engine='python')
        self.cbust_run_info = pd.read_csv(f3_output_filepath, error_bad_lines=False)[-8:]
        self.motif_names = list(self.f3_cbust_matrix.columns)[4:]

    def _from_f1(self, f1_output_filepath):
        '''
        We read a huge f1 file in line by line. We detect where matrices start and end.
        We pass the positions to an assistant function, which reads everything between these positions
        into a pandas data frame using pd.read_csv. The assistant function takes the matrix name out and adds it
        and the contents to a dict of all the matrices read so far.
        :param f1_output_filepath:
        :return:
        '''
        name_start_stop_numlines = self._accumulate_name_start_stop(f1_output_filepath)
        for i in range(0, len(name_start_stop_numlines[0])):
            single_matrix = self._pull_matrix_from_positions(name_start_stop_numlines[1][i],
                                                             name_start_stop_numlines[2][i],
                                                             f1_output_filepath, name_start_stop_numlines[3])
            self.f1_matrix_dict[name_start_stop_numlines[0][i]] = single_matrix

    def _accumulate_name_start_stop(self, f1_output_filepath):
        '''
        We create a tuple with names and positional information on matrices in the cbust f1 file.
        :param f1_output_filepath:
        :return:
        '''
        start_list = []
        stop_list = []
        name_list = []
        self.f1_matrix_dict = {}
        with open(f1_output_filepath, "r") as f1_file:
            in_matrix = False
            file_position = 0
            for line in f1_file:
                file_position += 1
                if line == "\n" and in_matrix == True:
                    stop_list.append(file_position)
                    in_matrix = False
                    continue
                elif line.startswith(">"):
                    in_matrix = True
                    name_list.append(line)
                    continue
                elif line.startswith("#") and in_matrix == True:
                    start_list.append(file_position)
                    continue
                elif line.isdigit() and in_matrix == True:
                    continue
                else:
                    continue
        f1_file.close()
        return name_list, start_list, stop_list, file_position

    def _pull_matrix_from_positions(self, startpos, endpos, f1_output_filepath, num_lines):
        '''
        Retrieve a single matrix from a given position in file
        :param startpos:
        :param endpos:
        :return:
        '''
        cookie_cutter = lambda x: x not in range(startpos-1, endpos)
        current_matrix = pd.read_csv(f1_output_filepath, error_bad_lines=False, sep='\t',
                                     skiprows = cookie_cutter, engine='c', index_col=False, header=0)
        return current_matrix

    @staticmethod
    def feature_matrix_special(negative_filepath, positive_filepath):
        '''
        A special method to assemble a feature matrix from two different cbust input files.
        :param self:
        :param negative_filepath:
        :param positive_filepath:
        :param feature_matrix_name:
        :return:
        '''

        l_files = [negative_filepath, positive_filepath]
        d_sequence_d_motif_crmscore = {}
        s_sequence = ''
        s_motif = ''
        ic_catch_crm = False
        ic_catch_motif = False
        for ix_file, file in enumerate(l_files):
            with open(file) as f:
                for line in f:
                    if ic_catch_crm:
                        crm_score = float(line.split()[0])
                        ic_catch_crm = False
                        if d_sequence_d_motif_crmscore.get(s_sequence):
                            d_sequence_d_motif_crmscore[s_sequence][s_motif] = crm_score
                        else:
                            if ix_file == 0:
                                label = 0
                            else:
                                label = 1
                            d_sequence_d_motif_crmscore[s_sequence] = {'_label': label,
                                                                       s_motif: crm_score}
                    elif ic_catch_motif:
                        s_motif = line.split()[4]
                        ic_catch_motif = False
                        ic_catch_crm = True
                    elif line.startswith('>'):
                        s_sequence = line.split()[0][1:]
                        ic_catch_motif = True

        # create pandas data frame from dict
        return pd.DataFrame.from_dict(d_sequence_d_motif_crmscore, orient='index')

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



