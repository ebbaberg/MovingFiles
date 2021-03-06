## DataFlowSort.py
## Moves files into a structure that works with data flow, 

import csv
import os
import shutil
import numpy as np

LABELS_PATH = '/home/jovyan/kensert_CNN/bbbc021_labels.csv'
OUTPUT_DIR = '/home/jovyan/scratch-shared/Ebba/All'
IMAGE_DIR= '/home/jovyan/kensert_CNN/images_bbbc021'
IMAGE_NAME ='/bbbc021_%s.png' #Where %s is the image number
VALIDATION_SET_SIZE = 0.20 #Percentage written as decimal
TEST_SET_SIZE = 0.15
#INCLUDED_CLASSES = ['Aurora kinase inhibitors', 'Eg5 inhibitors'] #Empty for all classes included
INCLUDED_CLASSES = [] #Empty for all classes included
OUTPUT_SIZE = 1 # Percentage of original total size that should be used, written as a decimal 0-1.


##Assumes row structure is ['image_number', 'compound', 'concentration', 'moa', 'plate', 'well', 'replicate']
def sort_into_class_folders(row, category): #Where category is train, validation or test
    if(str(row[3]) == 'moa') :     #Ignore header
        print("reached header!!!!")
        return
    current_path = IMAGE_DIR + IMAGE_NAME  % str(row[0])
   
    dir_path = OUTPUT_DIR+"/"  + category +"/" + str(row[3]) 
    target_path = dir_path +"/" +str(row[0]) + ".png"

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(str(row))
    shutil.copyfile(current_path, target_path)

def sort_into_test_folder(row, category): #Where category is train, validation or test
    if(str(row[3]) == 'moa') :     #Ignore header
        print("reached header!!!!")
        return
    current_path = IMAGE_DIR + IMAGE_NAME  % str(row[0])
   
    dir_path = OUTPUT_DIR+"/"  + category + "/" +category #dataflow needs a subfolder, but test subfolder should not be class
    target_path = dir_path +"/" +str(row[0]) + ".png"

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(str(row))
    shutil.copyfile(current_path, target_path)

def sort_into_one_folder(row):
    if(str(row[3]) == 'moa') :     #Ignore header
        print("reached header!!!!")
        return
    current_path = IMAGE_DIR + IMAGE_NAME  % str(row[0])
   
    dir_path = OUTPUT_DIR + "/Images"
    target_path = dir_path +"/" +str(row[0]) + ".png"

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
        print(str(row))
    shutil.copyfile(current_path, target_path)

def get_randomized_sets(csv_list, classes_to_include):
    # Choose 3 random sets for training, validation and test
    included_rows = []

    if(len(classes_to_include)==0):
        included_rows = csv_list 
    else:
        for entry in csv_list:
            if(entry[3] in classes_to_include):
                included_rows.append(entry)

    data_size = int(len(included_rows ) * OUTPUT_SIZE)
    validation_set_size = int(data_size * VALIDATION_SET_SIZE + 1)
    test_set_size = int(data_size * TEST_SET_SIZE + 1)
    training_set_size = int(data_size -validation_set_size - test_set_size)

    indices = np.arange(data_size)
    np.random.shuffle(indices)

    train_row_numbers =np.array(included_rows) [indices[:training_set_size]]
    validation_rows=np.array(included_rows) [indices[training_set_size:training_set_size + validation_set_size]]
    test_rows = np.array(included_rows) [indices[training_set_size + validation_set_size:training_set_size + validation_set_size + test_set_size]]
    return train_row_numbers, validation_rows,test_rows

print("Starting moving files program")

with open(LABELS_PATH, 'r') as read_obj:
    # pass the file object to reader() to get the reader object
    csv_reader = csv.reader(read_obj, delimiter=";")
    csv_list = list(csv_reader)
    header = ['image_number', 'compound', 'concentration', 'moa', 'plate', 'well', 'replicate']
    if(str(csv_list[0][3]) == 'moa'):
        csv_list.pop(0) #Remove header

    classes_to_include = INCLUDED_CLASSES
    train_rows, validation_rows, test_rows = get_randomized_sets(csv_list, classes_to_include=classes_to_include )
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print("Made the output dir")

    with open(OUTPUT_DIR + "/Labels.csv", 'w', newline = '') as new_labels_file:
        wr = csv.writer(new_labels_file, delimiter=",")
        wr.writerow(header)
        wr.writerows(train_rows)
        wr.writerows(validation_rows)
        wr.writerows(test_rows)

    for row in train_rows:
        sort_into_class_folders(row, "Train")
    for row in validation_rows:
        sort_into_class_folders(row, "Validation")
    for row in test_rows:
        sort_into_test_folder(row, "Test")
    
print("Finished moving files program")