# Leave one compound out for testing/validation?
## DataFlowSort.py
## Moves files into a structure that works with data flow, 


##Backgroung from https://data.broadinstitute.org/bbbc/BBBC021/

# #NOTE: When evaluating accuracy of MOA classification, it is critical to ensure that the cross-validation is set up correctly. 
# #MOA classification is the task of classifying the MOA of an unseen compound. 
# #Therefore, the evaluation should be a leave-one-compound-out cross validation: 
# #in each iteration, hold out one compound (all replicates and at all concentrations), train on the remaining, and test on the held out compound.

import csv
import os
import shutil
import numpy as np
import random

class LeaveOneOut:
    
    def __init__(self,
                labels_path = '/home/jovyan/scratch-shared/Ebba/KinaseInhibitorData/dataframe.csv',
                output_dir = '/home/jovyan/scratch-shared/Ebba/Kinase_Leave_One_Out',
                image_dir= '/home/jovyan/scratch-shared/Ebba/KinaseInhibitorData/MiSyHo299',
                image_name ='/%s.png', #Where %s is the image number,
                validation_set_size  = 0.20, #Percentage written as decimal,
                include_groups = ['control', 'TK','CMGC','AGC'], #Empty for everything included,
                include_index = 10,
                class_index = 5,
                well_index = 3,
                leave_out_index = 6,
                image_number_index = 1,
                name_to_leave_out = "" ,
                k_fold = "4",
                output_size = 1 # Percentage of original total size that should be used,
                ):
        self.labels_path = labels_path
        self.output_dir = output_dir
        self.image_dir = image_dir
        self.image_name  = image_name
        self.validation_set_size = validation_set_size
        self.included_groups = include_groups
        self.include_index = include_index
        self.class_index =  class_index 
        self.well_index =  well_index
        self.leave_out_index =  leave_out_index
        self.image_number_index = image_number_index
        self.name_to_leave_out =      name_to_leave_out
        self.output_size = output_size
        self.k_fold = int(k_fold)
        self.k_folds = {1:['CBK293871', 'CBK289742', 'CBK293861', 'CBK288271', 'CBK278067', 'CBK200518C', 'CBK293879', 'CBK288256', 'CBK288268', 'CBK290998', 'CBK293860G', 'CBK288311', 'CBK290756'],
2:['CBK293884', 'CBK277983', 'CBK290822G', 'CBK293876', 'CBK277987', 'CBK290852', 'CBK200981', 'CBK290815', 'CBK290649', 'CBK288297', 'CBK288310', 'CBK293911', 'CBK290956'],
3:['CBK277992', 'CBK290253', 'CBK278049G', 'CBK278131', 'CBK277927', 'CBK293904', 'CBK288292', 'CBK290830', 'CBK293875', 'CBK278001', 'CBK289902', 'CBK041209', 'CBK288314'],
4:['CBK288316', 'CBK290917', 'CBK288321', 'CBK288351C', 'CBK288330G', 'CBK290480', 'CBK277980', 'CBK040864', 'CBK288328', 'CBK290797', 'CBK277959', 'CBK293858C', 'CBK278129'],
5:['CBK288257', 'CBK293174', 'CBK277991', 'CBK290853', 'CBK040892', 'CBK288327', 'CBK290997C', 'CBK277977', 'CBK293908', 'CBK290859', 'CBK288279C', 'CBK277936', 'CBK290484'],
6:['CBK290196C', 'CBK293887', 'CBK041242C', 'CBK293852', 'CBK278057', 'CBK288269', 'CBK278013', 'CBK288270', 'CBK290224', 'CBK288350', 'CBK293891', 'CBK293867', 'CBK290561'],
7:['CBK290987', 'CBK288253C', 'CBK278119G', 'CBK013405', 'CBK290845', 'CBK293859', 'CBK278127', 'CBK277962', 'CBK040896', 'CBK278128G', 'CBK293881', 'CBK288278', 'CBK293865'],
8:['CBK293863', 'CBK278063', 'CBK289985', 'CBK290589', 'CBK288254', 'CBK290836', 'CBK293163', 'CBK278084', 'CBK293898', 'CBK290823', 'CBK290752', 'CBK290269', 'CBK290585'],
9:['CBK290869', 'CBK288326C', 'CBK290847', 'CBK278056', 'CBK290995', 'CBK290855', 'CBK288272', 'CBK288321G', 'CBK288323', 'CBK289904', 'CBK041168', 'CBK290022', 'CBK290454C'],
10:['CBK277968', 'CBK290267', 'CBK278016', 'CBK290877', 'CBK290206', 'CBK290915', 'CBK041143', 'CBK288255', 'CBK289937', 'CBK277922C', 'CBK288335', 'CBK293864', 'CBK201383'],
}


    def main(self):
        print("starting levave on out")

        with open(self.labels_path, 'r') as read_obj:
            csv_reader = csv.reader(read_obj, delimiter=";")
            csv_list = list(csv_reader)
            header = csv_list.pop(0) #remove header

            train_rows, validation_rows, test_rows = self.get_randomized_sets_leave_one_out(csv_list, included_groups=self.included_groups )
            
            if os.path.exists(self.output_dir) and os.path.isdir(self.output_dir):
                shutil.rmtree(self.output_dir)

            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
                print("made the output dir")

            with open(self.output_dir + "/Labels.csv", 'w', newline = '') as new_labels_file:
                wr = csv.writer(new_labels_file, delimiter=",")
                wr.writerow(header)
                wr.writerows(train_rows)
                wr.writerows(validation_rows)
                wr.writerows(test_rows)

            for row in train_rows:
                if row != header:
                    self.sort_into_class_folders(row, "Train")
            for row in validation_rows:
                if row != header:
                    self.sort_into_class_folders(row, "Validation")
            for row in test_rows:
                if row != header:
                    self.sort_into_test_folder(row, "Test")
            
        print("Finished leave one out")
    
    def run(self):
        self.main()

    def update_settings(self,
                labels_path = '/home/jovyan/scratch-shared/Ebba/KinaseInhibitorData/dataframe.csv',
                output_dir = '/home/jovyan/scratch-shared/Ebba/Kinase_Leave_One_Out',
                image_dir= '/home/jovyan/scratch-shared/Ebba/KinaseInhibitorData/MiSyHo299',
                image_name ='/%s.png', #Where %s is the image number,
                validation_set_size  = 0.20, #Percentage written as decimal,
                include_groups = ['control', 'TK','CMGC','AGC'], #Empty for everything included,
                include_index = 10,
                class_index = 5,
                well_index = 3,
                leave_out_index = 6,
                image_number_index = 1,
                name_to_leave_out = "CBK013405" ,
                k_fold = 1,
                k_folds = {},
                output_size = 1 # Percentage of original total size that should be used,
                ):
        self.labels_path = labels_path
        self.output_dir = output_dir
        self.image_dir = image_dir
        self.image_name  = image_name
        self.validation_set_size = validation_set_size
        self.included_groups = include_groups
        self.include_index = include_index
        self.class_index =  class_index 
        self.well_index =  well_index
        self.leave_out_index =  leave_out_index
        self.image_number_index = image_number_index
        self.name_to_leave_out =      name_to_leave_out
        self.output_size = output_size
        self.k_fold = int(k_fold)
        self.k_folds = {1:['CBK293871', 'CBK289742', 'CBK293861', 'CBK288271', 'CBK278067', 'CBK200518C', 'CBK293879', 'CBK288256', 'CBK288268', 'CBK290998', 'CBK293860G', 'CBK288311', 'CBK290756'],
2:['CBK293884', 'CBK277983', 'CBK290822G', 'CBK293876', 'CBK277987', 'CBK290852', 'CBK200981', 'CBK290815', 'CBK290649', 'CBK288297', 'CBK288310', 'CBK293911', 'CBK290956'],
3:['CBK277992', 'CBK290253', 'CBK278049G', 'CBK278131', 'CBK277927', 'CBK293904', 'CBK288292', 'CBK290830', 'CBK293875', 'CBK278001', 'CBK289902', 'CBK041209', 'CBK288314'],
4:['CBK288316', 'CBK290917', 'CBK288321', 'CBK288351C', 'CBK288330G', 'CBK290480', 'CBK277980', 'CBK040864', 'CBK288328', 'CBK290797', 'CBK277959', 'CBK293858C', 'CBK278129'],
5:['CBK288257', 'CBK293174', 'CBK277991', 'CBK290853', 'CBK040892', 'CBK288327', 'CBK290997C', 'CBK277977', 'CBK293908', 'CBK290859', 'CBK288279C', 'CBK277936', 'CBK290484'],
6:['CBK290196C', 'CBK293887', 'CBK041242C', 'CBK293852', 'CBK278057', 'CBK288269', 'CBK278013', 'CBK288270', 'CBK290224', 'CBK288350', 'CBK293891', 'CBK293867', 'CBK290561'],
7:['CBK290987', 'CBK288253C', 'CBK278119G', 'CBK013405', 'CBK290845', 'CBK293859', 'CBK278127', 'CBK277962', 'CBK040896', 'CBK278128G', 'CBK293881', 'CBK288278', 'CBK293865'],
8:['CBK293863', 'CBK278063', 'CBK289985', 'CBK290589', 'CBK288254', 'CBK290836', 'CBK293163', 'CBK278084', 'CBK293898', 'CBK290823', 'CBK290752', 'CBK290269', 'CBK290585'],
9:['CBK290869', 'CBK288326C', 'CBK290847', 'CBK278056', 'CBK290995', 'CBK290855', 'CBK288272', 'CBK288321G', 'CBK288323', 'CBK289904', 'CBK041168', 'CBK290022', 'CBK290454C'],
10:['CBK277968', 'CBK290267', 'CBK278016', 'CBK290877', 'CBK290206', 'CBK290915', 'CBK041143', 'CBK288255', 'CBK289937', 'CBK277922C', 'CBK288335', 'CBK293864', 'CBK201383'],
}



    def sort_into_class_folders(self, row, category): #where category is train, validation or test
        current_path = self.image_dir + self.image_name  % str(row[self.image_number_index])
    
        dir_path = self.output_dir+"/"  + category +"/" + str(row[self.class_index]) 
        target_path = dir_path +"/" +str(row[self.image_number_index]) + ".png"

        if(str(row[self.image_number_index]) == ''):
            return

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(str(row))
        shutil.copyfile(current_path, target_path)

    def sort_into_test_folder(self, row, category): #where category is train, validation or test
        current_path = self.image_dir + self.image_name  % str(row[self.image_number_index])
    
        dir_path = self.output_dir+"/"  + category + "/" +category #dataflow needs a subfolder, but test subfolder should not be class
        target_path = dir_path +"/" +str(row[self.image_number_index]) + ".png"

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(str(row))
        shutil.copyfile(current_path, target_path)

    def sort_into_one_folder(self, row):
        current_path = self.image_dir + self.image_name  % str(row[self.image_number_index])
    
        dir_path = self.output_dir + "/images"
        target_path = dir_path +"/" +str(row[self.image_number_index]) + ".png"

        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(str(row))
        shutil.copyfile(current_path, target_path)


    def get_training_validation_rows(self,compound_dictionary, control = False):
        well_training_rows = []
        well_validation_rows = []
        well_test_rows = []

        well_keys = np.array(list(compound_dictionary.keys()))
        data_size =len(well_keys)
        if(data_size == 1):
            raise Exception("Note enough data to have both a validation and a training entry. Key: " + str(well_keys))


        validation_set_size = int(data_size * self.validation_set_size)
        if validation_set_size <= 0 :
            validation_set_size = 1

        training_set_size = int(data_size -validation_set_size)
        indices = np.arange(data_size)
        np.random.shuffle(indices)
        well_validation_keys = well_keys[indices[:validation_set_size]]
        if control: 
            well_test_keys = well_keys[indices[validation_set_size:2*validation_set_size]]
            well_training_keys = well_keys[indices[2*validation_set_size:]]
        else: 
            well_training_keys = well_keys[indices[validation_set_size:]]
            well_test_keys = []

        for key in well_training_keys:
            well_training_rows.append(compound_dictionary[key])
        for key in well_validation_keys:
            well_validation_rows.append(compound_dictionary[key])
        for key in well_test_keys:
            well_test_rows.append(compound_dictionary[key])

        if(control):
            well_training_rows = [item for dictionary in well_training_rows for sublist in dictionary.values() for item in sublist]
            well_validation_rows = [item for dictionary in well_validation_rows for sublist in dictionary.values() for item in sublist]
            well_test_rows = [item for dictionary in well_test_rows for sublist in dictionary.values() for item in sublist]
        else:
            well_training_rows = [item for sublist in well_training_rows for item in sublist]
            well_validation_rows = [item for sublist in well_validation_rows for item in sublist]
            well_test_rows = [item for sublist in well_test_rows for item in sublist]
        
        return well_training_rows, well_validation_rows, well_test_rows

    def get_randomized_sets_leave_one_out(self, csv_list, included_groups):

        nested_dict = {}
        test_rows = []
        validation_rows = []
        train_rows = []
        included_rows = []

        for entry in csv_list:
            class_for_row = entry[self.class_index] 
            leave_out_entry = entry[self.leave_out_index]
            include_entry = entry[self.include_index]
            well = entry[self.well_index]
            if len(included_groups)==0 or include_entry in included_groups :
                if class_for_row not in nested_dict:
                    nested_dict[class_for_row] = {}
                if leave_out_entry not in nested_dict[class_for_row]:
                    nested_dict[class_for_row][leave_out_entry] = {}
                if well not in nested_dict[class_for_row][leave_out_entry]:
                    nested_dict[class_for_row][leave_out_entry][well] = []
                nested_dict[class_for_row][leave_out_entry][well].append(entry)

        print(self.k_folds.keys())
        leave_out = self.k_folds[self.k_fold]
        for class_for_row in nested_dict:
            compound_dict = nested_dict[class_for_row]
            if class_for_row == 'control':
                new_training_rows, new_validation_rows, new_test_rows = self.get_training_validation_rows(compound_dict, control= True)
                train_rows.append(new_training_rows) 
                validation_rows.append(new_validation_rows)
                test_rows.append(new_test_rows)
            else:
                for leave_out_entry in compound_dict:
                    if leave_out_entry in leave_out:
                        test_rows = test_rows +list(compound_dict[leave_out_entry].values())
                    else:
                        new_training_rows, new_validation_rows, _ = self.get_training_validation_rows(compound_dict[leave_out_entry])
                        train_rows.append(new_training_rows) 
                        validation_rows.append(new_validation_rows)

        train_rows = [item for sublist in train_rows for item in sublist]
        validation_rows = [item for sublist in validation_rows for item in sublist]
        test_rows = [item for sublist in test_rows for item in sublist]

        return train_rows, validation_rows,test_rows

if __name__ == "__main__":
    LeaveOneOut().main()
