import h5py
import glob 
import os 

PATH_FILE = os.getcwd()
DATA_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "datos","empleo"))
OUTPUT_PATH = os.path.abspath(os.path.join(PATH_FILE, "..", "output"))

paises = [i.split("/")[-1] for i in glob.glob(DATA_PATH + "/*")]

complexity_empleo = h5py.File(os.path.join(OUTPUT_PATH, 'complexity_empleo.hdf5'),'w')


for pais in paises:
    file_path_name = glob.glob(os.path.join(DATA_PATH,pais,"output")+"/*.h5")[0]
    h5fr = h5py.File(file_path_name,'r') 

    for obj in h5fr.keys():
        h5fr.copy(obj, complexity_empleo)

complexity_empleo.close()