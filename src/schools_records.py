import csv
import os
from tqdm import tqdm
import json
import cv2
import numpy as np
import random
import string
import matplotlib.pyplot as plt
import copy
from statistics import mean


EVAL_FACTOR = 0.2
TRAIN_FACTOR = 1 - EVAL_FACTOR

EVAL_FACTOR = 0.2
TRAIN_FACTOR = 1 - EVAL_FACTOR

MEAN_DIS_TRAIN = 40
STD_DEV_DIS_TRAIN = 10

MEAN_DIS_EVAL = 60
STD_DEV_DIS_EVAL = 15

MEAN_DIS_TRAIN_Y = 1
STD_DEV_DIS_TRAIN_Y = 5

MEAN_DIS_EVAL_Y = 2
STD_DEV_DIS_EVAL_Y = 5


def load_data_from_csv(csv_filepath: str):

    headings, rows = [], []
    with open(csv_filepath, encoding="utf8") as csv_file:
        for row in csv.reader(csv_file, delimiter=","):
            if not headings:
                headings = row
            else:
                rows.append(row)

    return headings, rows


def generate_json(*, json_path: str, json_number: str, dict: dict):

    json_object = json.dumps(dict, indent=4)
    json_name = os.path.join(json_path, "".join([json_number, ".json"]))

    with open(json_name, "w") as outfile:
        outfile.write(json_object)


def show_image(*, img: np.array):

    scale_percent = 40

    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    dim = (width, height)

    image_copy = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

    cv2.imshow("Image", image_copy)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def save_layout(*, img: np.array, img_name: str, path: str, dict: dict):

    list_of_dicts = dict['form']

    for text_dict in list_of_dicts:

        coords = text_dict['box']
        start_point =  (coords[0], coords[1])
        end_point = (coords[2], coords[3])
        color = (0, 0, 255)
        cv2.rectangle(img, start_point, end_point, color, 1)

        for word_dict in text_dict['words']:
            
            coords = word_dict['box']
            start_point =  (coords[0], coords[1])
            end_point = (coords[2], coords[3])
            color = (120, 120, 0)
            cv2.rectangle(img, start_point, end_point, color, 1)

    img_name = ''.join([img_name, '_layout.png'])
    img_path = os.path.join(path, img_name)
    cv2.imwrite(filename=img_path, img=img)


def modify_path_bc_lang(*, info: str, lang: str, file_type: str):

    # Modify path according to language
    if lang == "eng":
        info_to_load = "".join([info, "_english"])

    elif lang == "esp":
        info_to_load = "".join([info, "_spanish"])
    
    else:
        warn_message = "".join(["WARNING: ", lang, "is not implemented yet."])
        print(warn_message)

    path = os.path.join(os.getcwd(), "".join([info_to_load, ".", file_type]))
    
    return path


def load_school_info(*, lang: str):

    # Modify path according to language
    info_to_load = "schools"
    schools_json_path = modify_path_bc_lang(info=info_to_load, lang=lang, file_type="json")

    with open(schools_json_path, 'r') as json_file:
        data = json_file.read()

    schools_info = json.loads(data)
    schools_list = schools_info["schools"]

    return schools_list


def load_subjects_semantinc(*, lang: str):

    # Modify path according to language
    info_to_load = "subjects"
    subjects_semantic_json = modify_path_bc_lang(info=info_to_load, lang=lang, file_type="json")

    with open(subjects_semantic_json, 'r') as subjects_json_file:
        data = subjects_json_file.read()

    subjects_semantic = json.loads(data)
    subjects_semantic = subjects_semantic["subjects"]

    return subjects_semantic


def load_names(*, info_to_load: str, lang: str):

    txt_path = modify_path_bc_lang(info=info_to_load, lang=lang, file_type="txt")

    names = []
    with open(txt_path, 'r') as f:
        csvreader = csv.reader(f, delimiter=' ')
        for row in csvreader:
            names.append(row[0])

    return names


def get_name(*, names: list = None, family_names: list = None):
    
    name = random.choice(names)
    family_name_1 = random.choice(family_names)
    family_name_2 = random.choice(family_names)
    persons_name = ''.join([name, " ", family_name_1, " ", family_name_2])

    return persons_name


def create_head_studies_profile(*, names: list = None, family_names: list = None):

    person_name = get_name(names=names, family_names=family_names)
    return person_name
    
    
# TODO Ask Boal how to manage the arguments in 'create_secretary_profile'.
# The arguments do nothing in this functions, instead they are parsed to another one.
def create_secretary_profile(*, names: list = None, family_names: list = None):
    
    person_name = get_name(names=names, family_names=family_names)
    return person_name



def create_student_profile(*, names: list = None, family_names: list = None):

    """ Create a dictionary with the header information of the student.

    Args:
        names (list, optional): A list with usual names in Spain. Defaults to None.
        family_names (list, optional): A list with usual family names in Spain. Defaults to None.

    Returns:
        student_profile (dict): A dict with the header info.
    """
    
    student_name = get_name(names=names, family_names=family_names)
    
    dni = ''.join([str(random.randrange(0, 99999999)).zfill(8), " - ", random.choice(string.ascii_uppercase)])
    
    student_profile = {
        'Nombre': student_name,
        'Documento Nacional de Identidad': dni
    }
    
    return student_profile, student_name


def get_alpha_grade(*, numeric_grade: int, lang: str):

    if lang == "eng":
        if numeric_grade < 5:
            alpha = "Fail: "
        elif numeric_grade < 7:
            alpha = "Pass: "
        elif numeric_grade < 9:
            alpha = "Good: "
        else: 
            alpha = "Outstanding: "
    
    elif lang == "esp":
        if numeric_grade < 5:
            alpha = "Suspenso: "
        elif numeric_grade < 7:
            alpha = "Bien: "
        elif numeric_grade < 9:
            alpha = "Notable: "
        else: 
            alpha = "Sobresaliente: "
    
    else:
        warn_message = "".join(["WARNING: ", lang, "is not implemented yet."])
        print(warn_message)

    return alpha


def get_displacement(*, mean: float, std_dev: float, length: int, lim_sup: float = None):

    dis_array = np.random.normal(mean, std_dev, size=(1, length))
    dis_array = [coord if coord >= 0 else 0.1 for coord in dis_array[0]]

    if lim_sup:
        dis_array = [coord if coord <= lim_sup else lim_sup for coord in dis_array]
    
    return dis_array


def get_table_displacements(*, num_students: int):

    train_table_metrics = {}
    eval_table_metrics = {}

    train_samples_num = int(TRAIN_FACTOR * num_students)
    # TODO 'lim_sup' should be f(total_table_width)
    train_table_metrics['x_table_displacement'] = get_displacement(mean=MEAN_DIS_TRAIN, std_dev=STD_DEV_DIS_TRAIN, length=train_samples_num, lim_sup=92)
    train_table_metrics['y_table_displacement'] = get_displacement(mean=MEAN_DIS_TRAIN_Y, std_dev=STD_DEV_DIS_TRAIN_Y, length=train_samples_num)
    eval_table_metrics['x_table_displacement'] = get_displacement(mean=MEAN_DIS_EVAL, std_dev=STD_DEV_DIS_EVAL, length=num_students-train_samples_num, lim_sup=92)
    eval_table_metrics['y_table_displacement'] = get_displacement(mean=MEAN_DIS_EVAL_Y, std_dev=STD_DEV_DIS_EVAL_Y, length=num_students-train_samples_num)

    x_displacement = copy.deepcopy(train_table_metrics['x_table_displacement'])
    x_displacement.extend(eval_table_metrics['x_table_displacement'])
    y_displacement = copy.deepcopy(train_table_metrics['y_table_displacement'])
    y_displacement.extend(eval_table_metrics['y_table_displacement'])

    return train_table_metrics, eval_table_metrics, x_displacement, y_displacement


def get_alpha_numeric_proportion(*, num_students: int):

    train_samples_num = int(TRAIN_FACTOR * num_students)
    train_alpha_numeric_proportion = [random.choice([True, False]) for _ in range(train_samples_num)]
    eval_alpha_numeric_proportion = [random.choice([True, False]) for _ in range(num_students-train_samples_num)]
    
    alpha_num = copy.deepcopy(train_alpha_numeric_proportion)
    alpha_num.extend(eval_alpha_numeric_proportion)

    return train_alpha_numeric_proportion, eval_alpha_numeric_proportion, alpha_num


def create_table_position_plots(*, train_data: list, eval_data: list):

    axis = 'x'

    for train, test in zip(train_data, eval_data):

        plt.clf()
        plt.style.use("ggplot")

        if axis == 'x':
            _, bins = np.histogram(train, bins=10, range=(0,100))
            fig, (ax1, ax2) = plt.subplots(2, sharex=True)
            orientation = "horizontal"
            compare = "vertical"

            ax1_x_label = ""
            ax1_y_label = "Number of samples"
            ax2_x_label = "Displacement [mm]"
            ax2_y_label = "Number of samples"

        else:
            _, bins = np.histogram(train, bins=10, range=(0,20))
            fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
            orientation = "vertical"
            compare = "horizontal"

            ax1_x_label = "Number of samples"
            ax1_y_label = "Displacement [mm]"
            ax2_x_label = "Number of samples"
            ax2_y_label = ""
        
        fig.suptitle("".join(['Table position: ', orientation, ' comparison']), fontsize=14)

        ax1.set_title("Train dataset", fontsize=10)
        ax2.set_title("Eval. dataset", fontsize=10)

        ax1.hist(train, bins=bins, orientation=compare)
        ax2.hist(test, bins=bins, orientation=compare, color='green')

        ax1.set_xlabel(ax1_x_label, fontsize=8)
        ax1.set_ylabel(ax1_y_label, fontsize=8)
        ax2.set_xlabel(ax2_x_label, fontsize=8)
        ax2.set_ylabel(ax2_y_label, fontsize=8)


        plt.savefig(os.path.join(os.getcwd(), "".join([axis, "_table_pos.png"])))
        plt.close()

        axis = 'y'


# TODO
def create_num_subjects_per_doc_plot():
    pass

# TODO
def create_subjects_histogram():
    pass

def create_grades_per_subject_plot(*, data: dict):

    plt.clf()
    plt.style.use("ggplot")

    x = []
    y = []
    area = []
    x_tics = []

    for i, label in enumerate(data):

        x.append(i)
        y.append(mean(data[label]))
        area.append(len(data[label]))
        x_tics.append(label)

        if len(list(data))-1 == i+1:
            break

    colors = np.random.rand(len(x_tics))
    plt.xticks(x, x_tics, rotation = 90)
    plt.title('Mean-Grade per subject')
    plt.ylabel('Grades')
    plt.scatter(x, y, s=area, c=colors, alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(os.getcwd(), "grades_per_subject.png"))
    plt.close()

def compute_metrics(*, metrics: dict):

    table_train = [metrics["train"]["x_table_displacement"], metrics["train"]["y_table_displacement"]]
    table_eval = [metrics["eval"]["x_table_displacement"], metrics["eval"]["y_table_displacement"]]

    create_table_position_plots(train_data=table_train, eval_data=table_eval)
    create_grades_per_subject_plot(data=metrics["grades_per_subjects"])
    create_subjects_histogram()
    create_num_subjects_per_doc_plot()

def update_grades_per_subject_metrics(*, metrics: dict, new_grades: dict):

    for label in new_grades:
        metrics[label].append(new_grades[label]["grade"])

    return metrics