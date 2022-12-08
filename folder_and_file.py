import os


# Creat folder from list
def creat_folder(path, list_folder):
    for folder in list_folder:
        folder_path = os.path.join(path, folder)
        if not os.path.exists(folder_path):

            os.makedirs(folder_path)
        else:
            print("folder have exist.")

def delete_all_file(path):
    try:

        for file_name in os.listdir(path):
            # construct full file path
            # print(file_name)
            file = os.path.join(path, file_name)
            if os.path.isfile(file):
                print('Deleting file:', file)
                os.remove(file)
    except:
        print("Delete all file error!")

if __name__ == '__main__':
    labels = ['A','B','C','D','Đ','E','G','H','I','K','L','M','N','O','P','Q','R','S','T','U','V','X','Y',"SAC","HUYEN", "HOI","NGA","NANG","CACH","CHAM", "HI","ILY","MU","RAU"]
    print(len(labels))
    path_dir = dir_path = os.path.dirname(os.path.realpath(__file__))
    creat_folder(path_dir + "/train",labels)
    # delete_all_file(path_dir + "/data")