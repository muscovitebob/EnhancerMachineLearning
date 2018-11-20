import cbust_result as cb

# 0 for Invasive (I), 1 for Proliferative (P) in the output file
feature_matrix = cb.cbust_result.feature_matrix_special("immovable_data/Homer_Ireg_TOTAL_cbustOut",
                                                         "immovable_data/Homer_Preg_TOTAL_cbustOut")

feature_matrix.to_csv("feature_matrix.csv")

