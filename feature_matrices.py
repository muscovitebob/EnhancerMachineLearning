import cbust_result as cb

# 0 for Invasive (I), 1 for Proliferative (P) in the output file
# the immovable_data folder is where the cbust outputs too big for github are located
# pre-RSAT matrix
#feature_matrix1 = cb.cbust_result.feature_matrix_special("immovable_data/Homer_Ireg_TOTAL_cbustOut",
#                                                        "immovable_data/Homer_Preg_TOTAL_cbustOut")
#feature_matrix1.to_csv("feature_matrix_1.csv")


# Improved one by one cbuster leads to improved feature matrix (hopefully)
feature_matrix2 = cb.cbust_result.feature_matrix_special("immovable_data/I_one_by_one_cbusted.txt",
                                                         "immovable_data/P_one_by_one_cbusted.txt")

feature_matrix2.to_csv("feature_matrix_2.csv")