import csv
from fpdf import FPDF
from pdf2image import convert_from_path
import os
from tqdm import tqdm
import json
import cv2
import numpy as np
import datetime
import random
import string

# This is an on-purpose bug
rooth_path = "/home/your_user_name/change_this_Berta"

DSET_IMGS_FOLDER = os.path.join(os.getcwd(), "funsd_structure", "images")
DSET_ANNOTATIONS_FOLDER = os.path.join(os.getcwd(), "funsd_structure", "annotations")
DSET_GROUND_TRUTH_FOLDER = os.path.join(os.getcwd(), "funsd_structure", "ground_truth")

PDF_DOCS_FOLDER = os.path.join(os.getcwd(), "synthetic_pdf_docs")
PNG_DOCS_FOLDER = os.path.join(os.getcwd(), "synthetic_png_docs")
BADGES_FOLDER = os.path.join(os.getcwd(), "badges")
STAMPS_FOLDER = os.path.join(os.getcwd(), "stamps")
SIGNATURES_FOLDER = os.path.join(os.getcwd(), "signatures")
NAMES_TXT = os.path.join(os.getcwd(), "names.txt")
FAMILY_NAMES_TXT = os.path.join(os.getcwd(), "family_names.txt")
SCHOOLS_JSON = os.path.join(rooth_path, "schools.json")
SUBJECTS_SEMANTIC_JSON = os.path.join(os.getcwd(), "subjects.json")

STUDENTS = 20
# ACADEMIC_YEARS = ['3º de la ESO', '4º de la ESO', '1º de Bachillerato', '2º de Bachillerato']
EDUCATION_LEVEL = ['EDUCACIÓN SECUNDARIA OBLIGATORIA']
ACADEMIC_YEARS = ['3º de la ESO']
SCHOOLS = ['Recuerdo']
JUST_TABLE = False

""" A4 is the default '.pdf' format output in FPDF
Millimeters are the default unit in FPDF. This means the default output is 210x297 mm
The '.png' output version of the '.pdf' is 1654x2339 px """

MM_2_PXS = 7.876

# In default units ([mm])
W = 210
H = 297

LEFT_INDENT = 10
RIGHT_INDENT = 15
MULTI_CELL_W = W - RIGHT_INDENT - LEFT_INDENT

EXTRA_SPACES_Q = 1
EXTRA_SPACES_A = 2

DOCS_Z_FILL = 4

EVAL_FACTOR = 0.125
TRAIN_FACTOR = 1 - EVAL_FACTOR

MEAN_DIS_TRAIN = 45
STD_DEV_DIS_TRAIN = 24
MEAN_DIS_EVAL = 45
STD_DEV_DIS_EVAL = 24


class PDF(FPDF):


    def table(self, headings, rows, col_widths=(42, 39, 35, 40)):

        self.set_font('helvetica', size=12)

        for col_width, heading in zip(col_widths, headings):
            self.cell(col_width, 7, heading, border=1, align="C")
        self.ln()
        for row in rows:
            widths = [self.get_string_width(column) for column in row]
            self.cell(col_widths[0], 6, row[0], border="LR")
            self.cell(col_widths[1], 6, row[1], border="LR")
            self.cell(col_widths[2], 6, row[2], border="LR", align="R")
            self.cell(col_widths[3], 6, row[3], border="LR", align="R")
            self.ln()
        self.cell(sum(col_widths), 0, "", border="T")

        #TODO: do something with those widths

    
    def json_table(self, subjects_semantic: dict, x: float):

        table = self.school["table"]

        # '+1' because of headers row
        rows = len(table["row_questions"]) + 1
        columns = len(table["column_questions"])
        grades = []
        subjects = []

        available_subjects = list(subjects_semantic)
        # Remove the "media" element from the list for now
        available_subjects.pop(-1)

        for row in range(rows):
            self.cell(w=x, h=5, txt="")
            for column in range(columns):
                if row == 0:

                    # Write column question
                    cell_widht = table["column_sizes"][column]
                    height = 6
                    text = table["column_questions"][column]["text"]
                    size = table["sizes"]["column_questions"]
                    style = table["styles"]["column_questions"]
                    self.set_font('helvetica', size=size, style=style)
                    align = table["aligns"]["column_questions"]

                    # TODO set the table in the middle
                    # self.set_in_the_middle(str(1))
                    
                    coords, _, _ = self._get_coordinates(message=text, text_pos_in_cell=align, cell_width=cell_widht)
                    self.update_json(coords, text=text, label='other')
                    
                    self.cell(w=cell_widht, h=height, txt=text, border=1, align=align)

                else:

                    # Table body
                    cell_widht = table["column_sizes"][column]
                    height = 6

                    # Row questions
                    if column == 0:
                        
                        # label = 'question'
                        # label = table["row_questions"][row-1]["text"]
                        
                        if row == rows - 1:
                            label = "media"
                        
                        else:
                            label = available_subjects.pop(random.randint(0, len(available_subjects) - 1))
                        
                        subjects.append(label)

                        synonyms_num = len(subjects_semantic[label])
                        synonym_i = random.randint(0, synonyms_num)
                        text = subjects_semantic[label][synonym_i - 1]
                        style = table["styles"]["row_questions"]
                        size = table["sizes"]["row_questions"]
                        
                        try:
                            align = table["row_questions"][row-1]["align_exception"]
                            
                        # TODO look for the exception (or right way to do this)
                        except:
                            align = table["aligns"]["row_questions"]
                        
                        # TODO how should we collect this info in the '.json'?
                        try:
                            mean = eval(table["row_questions"][row-1]["mean_value"])
                        # TODO look for the exception (or right way to do this)
                        except:
                            mean = False
                        
                        self.set_font('helvetica', size=size, style=style)

                    # Cells
                    else:

                        # label = 'answer'
                        label = "".join([table["row_questions"][row-1]["text"], "_answer"])

                        if mean:
                            text = str(np.mean(np.asarray(grades)))

                        else:

                            if table['cells'] == 'alpha_numeric':

                                numeric = random.randint(0, 10)
                                alpha = get_alpha_grade(numeric_grade=numeric)
                                text = "".join([alpha, str(numeric)])

                            else:

                                numeric = random.randint(0, 10)
                                text = str(numeric)
                            
                            grades.append(numeric)

                        align = table["aligns"]["cells"]
                        size = table["sizes"]["cells"]
                        style = table["styles"]["cells"]
                        self.set_font('helvetica', size=size, style=style)

                    coords, _, _ = self._get_coordinates(message=text, text_pos_in_cell=align, cell_width=cell_widht)
                    self.update_json(coords, text=text, label=label)

                    self.cell(w=cell_widht, h=height, txt=text, border=1, align=align)

            self.ln()

        grades_one_year = self.generate_ground_truth_dict(grades=grades, subjects=subjects)

        return grades_one_year


    def adhoc_header(self):

        v_space_dict = {
            'badge_v_space': 0,
            'info_v_space': 0,
            'title_v_space': 0,
            'extra_v_space': 0
        }

        rect_v_space = []
        rect_y_origin = []

        if self.header_badge:

            y_badge_raw_origin = self.get_y()

            # TODO Hardcoded values
            v_space_badge = 20
            h_space_badge = 16
            h_space = 0.25 * v_space_badge
            v_space = 0.4 * h_space

            img_path = os.path.join(BADGES_FOLDER, "".join([self.school['nickname'], "_badge.png"]))
            self.image(img_path, self.get_x() + h_space, y_badge_raw_origin + v_space, h=v_space_badge, w=h_space_badge)
            
            rect_v_space.append(v_space_badge + 2 * v_space)
            v_space_dict['badge_v_space'] = v_space_badge + 2 * v_space
            rect_y_origin.append(y_badge_raw_origin)

            h_displacement = LEFT_INDENT + h_space_badge + 2 * h_space

        else:

            h_displacement = 0

        if self.header_info:

            self.set_font('helvetica', 'B', size=12)
            ln_factor = 1.4
            
            for i, school_data in enumerate(self.header_info_to_include):

                if self.school[school_data] != '-':
                    
                    # if type(self.school[school_data]) == list:

                    if school_data == "location":

                        message = self.compose_text(self.school[school_data], keys_list=self.header_info_keys_to_include,
                                                    index=i, special_char=', ', keys=True)
                        self.set_x(h_displacement)
                        coords, message_width, message_height = self._get_coordinates(message=message)
                        ln = message_height/ln_factor

                        self.cell(message_width, message_height, message)
                        self.update_json(coords, message, label='other')
                        self.ln(ln)
                    
                    else:

                        if self.header_info_keys_to_include[i]:
                            other = "".join([self.header_info_keys_to_include[i], ": ", str(self.school[school_data])])
                        else:
                            other = str(self.school[school_data])

                        self.set_x(h_displacement)
                        coords, message_width, message_height = self._get_coordinates(message=other)
                        ln = message_height/ln_factor

                        self.cell(message_width, message_height, other)
                        self.update_json(coords, other, label='other')
                        self.ln(ln)

                self.set_font('helvetica', size=10)
            
            n = len(self.header_info_to_include)
            h_lead = (- message_height) * (n - 1)
            header_info_v_space = n * message_height + h_lead
            v_space_dict['info_v_space'] = header_info_v_space
                    
                
            rect_v_space.append(header_info_v_space)
            rect_y_origin.append(200)


        if self.header_title:

            self.set_font('helvetica', 'B', 15)
            self.cell(80)
            header_message = 'Boletín de Notas'

            coords, message_width, message_height = self._get_coordinates(message=header_message)
            
            self.cell(message_width, message_height, header_message, align='C')
            self.update_json(coords, header_message, label='other')
            self.ln()

            rect_v_space.append(coords[3] / MM_2_PXS)
            rect_y_origin.append(coords[1])

            v_space_dict['title_v_space'] = (coords[3] - coords[1]) / MM_2_PXS
        
        if self.header_rect:
            
            texts_height = self.sum_dict_distances(v_space_dict, sum_except='badge_v_space')
            y_rect_0 = min(rect_y_origin)

            if v_space_dict['badge_v_space'] > texts_height:
                h_rect = v_space_dict['badge_v_space']
            else:
                h_rect = texts_height

            self.rect(x=10, y=y_rect_0, w=185, h=h_rect, style = '')
        
        self.set_y(max(rect_v_space) + min(rect_y_origin))

    
    def body(self, subjects_semantic: dict, x, y):

        grades_per_year = []

        for i, school_data in enumerate(self.texts_to_include):

            other, text_class, style, size, align = self.compose_text(self.school[school_data])

            if text_class == 'relevant':

                self.relevant_statement(message=other, size=size, style=style)
                self.move_abscissa(displacement=8)
            
            elif text_class == 'regular':

                self.regular_statement(message=other, size=size, style=style, align=align)
                self.move_abscissa(displacement=8)

            # TODO Hardcoded value
            if i+1 == 4:

                self.move_abscissa(y)
                grades_one_year = self.json_table(subjects_semantic, x)
                grades_per_year.append(grades_one_year)
                self.move_abscissa(displacement=8)

        return grades_per_year

    def body_just_table(self, subject_semantic: dict, x, y):

        grades_per_year = []

        self.move_abscissa(y)
        grades_one_year = self.json_table(subject_semantic, x)
        grades_per_year.append(grades_one_year)

        self.move_abscissa(displacement=8)
        
        # TODO this is madddd. Pls what I want is the table + some random text
        other, text_class, style, size, align = self.compose_text(self.school['text_5'])

        if text_class == 'relevant':

            self.relevant_statement(message=other, size=size, style=style)
            self.move_abscissa(displacement=8)
        
        elif text_class == 'regular':

            self.regular_statement(message=other, size=size, style=style, align=align)
            self.move_abscissa(displacement=8)

        return grades_per_year


    # def footer(self):

    #         self.set_y(-15)
    #         self.set_font('helvetica', 'I', 8)
    #         self.cell(0, 10, "".join(["Page ", str(self.page_no()), "/{nb}"]), align='C')


    def contextual_information(self, data: dict, extra_data: dict):
        
        data.update(extra_data)

        for datum in data:

            self.set_font('helvetica', size=12)
            question = "".join([datum, ":", " " * EXTRA_SPACES_Q])
            coords, message_width, message_height = self._get_coordinates(message=question)

            self.cell(message_width, message_height, question)
            self.update_json(coords, question, label='question', link_to=1)
            
            self.set_font('helvetica', 'I', 12)
            
            answer = data[datum]
            answer = "".join([answer, " " * EXTRA_SPACES_A])
            coords, message_width, message_height = self._get_coordinates(message=answer)

            self.cell(message_width, message_height, answer)
            self.update_json(coords, answer, label='answer', link_to=-1)
            self.ln()

    
    def relevant_statement(self, message: str, size: int = 16, style: str = 'B'):
        
        self.set_font('helvetica', style, size=size)
        other = message
        self.set_in_the_middle(other)
        coords, message_width, message_height = self._get_coordinates(message=other)

        self.cell(message_width, message_height, other)
        self.update_json(coords, other, label='other')

    
    def regular_statement(self, message: str, size: int = 10, style: str = '', align: str = 'L'):
        
        self.set_font('helvetica', style, size=size)
        other = message
        coords, message_width, message_height = self._get_coordinates(message=other)

        # self.cell(message_width, message_height, other, align=align)
        self.multi_cell(w=MULTI_CELL_W, txt=other)
        self.update_json(coords, other, label='other')


    def set_in_the_middle(self, text: str = None, width: float = None):

        if text:

            text_length = self.get_string_width(text)
            indentation = (W - text_length)/2 - LEFT_INDENT
            self.cell(indentation)
        
        elif width:

            indentation = width
            self.cell(indentation)


    def set_meta_data(self):

        pass

    def signature(self):
        
        self.set_y(self.get_y() + 10)
        self.set_x(95)
        self.set_font('helvetica', size=10)
        info_about_head = ''.join(['Jefatura de Estudios del C. ', self.school['name']])

        coords, message_width, message_height = self._get_coordinates(message=info_about_head)
        self.update_json(coords, info_about_head, label='other')

        self.cell(message_width, message_height, info_about_head, align='L')
        self.ln()

        signature_v_space = 30
        signature_h_space = 30
        self.set_x(95 + (self.get_string_width(head_studies) - signature_h_space) * 0.5)
        img_path = os.path.join(SIGNATURES_FOLDER, "signature_002.png")
        self.image(img_path, x=self.get_x(), y=self.get_y(), w=signature_v_space, h=signature_h_space)


        self.set_y(self.get_y() + signature_v_space)
        self.set_x(95)

        coords, message_width, message_height = self._get_coordinates(message=head_studies)
        self.update_json(coords, head_studies, label='other')
        
        self.cell(message_width, message_height, head_studies, align='L')
        self.ln()

        now = datetime.datetime.now()
        today = "".join([str(now.day), " del ", str(now.month), " de ", str(now.year)])
        date_and_place = "".join(['Madrid, a ', today])
        self.set_x(95)
        self.set_font('helvetica', 'I',size=10)

        coords, message_width, message_height = self._get_coordinates(message=date_and_place)
        self.update_json(coords, date_and_place, label='other')

        self.cell(message_width, message_height, date_and_place, align='L')


    def update_json(self, coords: list, text: str, label: str, link_to: int = None):

        words = []

        word_x0 = coords[0]
        word_y0 = coords[1]
        word_yf = coords[3]
        x_progress = 0

        total_lenght_px = coords[2] - coords[0]
        words_length_mm = 0

        for word in text.split():
            
            words_length_mm += self.get_string_width(word)
        
        spaces_length_mm = ((total_lenght_px) / MM_2_PXS) - words_length_mm
        spaces_fraction_length_mm = spaces_length_mm / len(text.split())

        for i, word in enumerate(text.split()):

            if i == 0 and len(text.split()) > 1:
                space_factor = 1.2

            else:
                space_factor = 1

            word_x0 += x_progress
            word_xf = word_x0 + int((self.get_string_width(word) + spaces_fraction_length_mm * space_factor) * MM_2_PXS)
            word_bbox = [word_x0, word_y0, word_xf, word_yf]
            word_dict = {
                "box": word_bbox,
                "text": word
            }

            x_progress = word_xf - word_x0
            
            words.append(word_dict)
        
        if link_to:
            linking_value = [self.id_counter, self.id_counter + link_to]
        else:
            linking_value = []

        append_dict = {
            "box": coords,
            "text": text,
            "label": label,
            "words": words,
            "linking": linking_value,
            "id": self.id_counter
        }
        
        self.png_list.append(append_dict)
        self.id_counter += 1

    
    def _get_coordinates(self, message: str, message_height: int = 6, text_pos_in_cell: str = 'L', cell_width: float = 0):

        message_width = self.get_string_width(message)
        
        if text_pos_in_cell == 'C':

            indentation = (cell_width - message_width)/2
            x_0 = self.get_x() + indentation

        elif text_pos_in_cell == 'R':

            space_widht = self.get_string_width(" ")
            indentation = cell_width - (message_width + space_widht)
            x_0 = self.get_x() + indentation

        else:
            space_widht = self.get_string_width(" ")
            x_0 = self.get_x() + space_widht

        y_0 = self.get_y()
        x_f = int((x_0 + message_width) * MM_2_PXS)
        y_f = int((y_0 + message_height) * MM_2_PXS)
        x_0 = int(x_0 * MM_2_PXS)
        y_0 = int(y_0 * MM_2_PXS)
        coordinates = [x_0, y_0, x_f, y_f]
        
        return coordinates, message_width, message_height

    
    def move_abscissa(self, displacement: float):

        current_y_pos = self.get_y()
        self.set_y(current_y_pos + displacement)


    def school_setter(self, school, secretary, student):
        
        # TODO include the head of studies info here too 
        # (and any other piece of info related to the school)
        self.school = school
        self.secretary_name = secretary
        self.student_name = student

    
    def year_setter(self, year):
        
        self.academic_year = year
        # TODO update the natural year properly
        now = datetime.datetime.now()
        self.natural_year = str(now.year)
        # TODO hardcoded programme
        self.academic_programme = 'ESO'

    
    def png_dict_setter(self, png_dict: dict):

        self.png_dict = png_dict
        self.png_list = []
        self.id_counter = 0


    def header_features_setter(self, header_rect: bool = True, header_badge: bool = True, header_title: bool = True, header_info: bool = True):
        
        self.header_rect = header_rect
        self.header_badge = header_badge
        self.header_title = header_title
        self.header_info = header_info
        # TODO read 'header_info_to_include' and 'header_info_keys_to_include' from '.json' file
        self.header_info_to_include = ['name', 'location', 'phone_number', 'web', 'email']
        self.header_info_keys_to_include = [False, False, 'Teléfono', 'Web', 'eMail']


    def body_features_setter(self):

        self.texts_to_include = ['text_1', 'text_2', 'text_3', 'text_4', 'text_5', 'text_6']


    def png_dict_getter(self):

        aux_dict = {
            "form": self.png_list
        }

        self.png_dict.update(aux_dict)
        return self.png_dict


    def compose_text(self, fragments_list: list, keys_list: list = [], index: int = None, special_char: str = ' ', keys: bool = False):

        # TODO document this function
        if keys:
            if keys_list[index]:
                text = keys_list[index]
            else:
                text = ""
        else:
            text = ""

        text_dictionary = fragments_list

        text_class = None
        style = None
        size = None
        align = None
        gaps = []

        for text_fragment in text_dictionary:
            
            # Extract appart info such as style, size or alignment from the '.json'
            if text_fragment == 'style':
                style = text_dictionary[text_fragment]
            elif text_fragment == 'size':
                size = text_dictionary[text_fragment]
            elif text_fragment == 'align':
                align = text_dictionary[text_fragment]
            elif text_fragment == 'class':
                text_class = text_dictionary[text_fragment]
            elif text_fragment == 'gaps':
                
                for gap in text_dictionary[text_fragment]:

                    # Given a 'str', append the value of the variable with the same name as the 'str'
                    string = "".join(['self.', gap])
                    gaps.append(eval(string))

            # TODO addapt the function. Final ',' or '.' are supposed to be in the '.json'
            else: 
                text = "".join([text, str(text_dictionary[text_fragment]), special_char])

        # If there is any gap ('{}') in the '.json' to fill the text, fill it
        if gaps != []:
            text = text.format(*gaps)

        if size:
            return text, text_class, style, size, align
        else:
            return text
    
    def sum_dict_distances(self, dist_dict: dict, sum_except: str):
        
        sum = 0
        
        for distance_key in dist_dict:
            
            if distance_key != sum_except:
                sum += dist_dict[distance_key]

        return sum

    def generate_ground_truth_dict(self, grades: list, subjects: list):

        gt_dict = {}

        for subject, grade in zip(subjects, grades):
            
            gt_dict[subject] = {}
            gt_dict[subject]["grade"] = grade

        return gt_dict


""" 
...............................
...............................
The Method functions start here
...............................
...............................

"""


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


def load_names(*, txt_path: str):

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
        student_profile (dict): A dict wit the header info.
    """
    
    student_name = get_name(names=names, family_names=family_names)
    
    dni = ''.join([str(random.randrange(0, 99999999)).zfill(8), " - ", random.choice(string.ascii_uppercase)])
    
    student_profile = {
        'Nombre': student_name,
        'Documento Nacional de Identidad': dni
    }
    
    return student_profile, student_name


def load_school_info():

    with open(SCHOOLS_JSON, 'r') as json_file:
        data = json_file.read()

    schools_info = json.loads(data)
    schools_list = schools_info["schools"]

    return schools_list


def load_subjects_semantinc():

    with open(SUBJECTS_SEMANTIC_JSON, 'r') as subjects_json_file:
        data = subjects_json_file.read()

    subjects_semantic = json.loads(data)
    subjects_semantic = subjects_semantic["subjects"]

    return subjects_semantic


def get_alpha_grade(*, numeric_grade: int):

    if numeric_grade < 5:
        alpha = "Suspenso: "
    elif numeric_grade < 7:
        alpha = "Bien: "
    elif numeric_grade < 9:
        alpha = "Notable: "
    else: 
        alpha = "Sobresaliente: "
    
    return alpha


def get_displacement(*, mean: float, std_dev: float, length: int):

    dis_array = np.random.normal(mean, std_dev, size=(1, length))
    dis_array = [coord if coord >= 0 else 0 for coord in dis_array[0]]
    
    return dis_array


def get_table_displacements():

    train_table_metrics = {}
    eval_table_metrics = {}

    train_samples_num = int(TRAIN_FACTOR * STUDENTS)
    train_table_metrics['x_table_displacement'] = get_displacement(mean=MEAN_DIS_TRAIN, std_dev=STD_DEV_DIS_TRAIN, length=train_samples_num)
    train_table_metrics['y_table_displacement'] = get_displacement(mean=MEAN_DIS_TRAIN, std_dev=STD_DEV_DIS_TRAIN, length=train_samples_num)
    eval_table_metrics['x_table_displacement'] = get_displacement(mean=MEAN_DIS_EVAL, std_dev=STD_DEV_DIS_EVAL, length=STUDENTS-train_samples_num)
    eval_table_metrics['y_table_displacement'] = get_displacement(mean=MEAN_DIS_EVAL, std_dev=STD_DEV_DIS_EVAL, length=STUDENTS-train_samples_num)

    x_displacement = train_table_metrics['x_table_displacement']
    x_displacement.extend(eval_table_metrics['x_table_displacement'])
    y_displacement = train_table_metrics['y_table_displacement']
    y_displacement.extend(eval_table_metrics['y_table_displacement'])

    return train_table_metrics, eval_table_metrics, x_displacement, y_displacement


if __name__ == '__main__':
    
    names = load_names(txt_path=NAMES_TXT)
    family_names = load_names(txt_path=FAMILY_NAMES_TXT)
    schools_list = load_school_info()
    subjects_semantic = load_subjects_semantinc()

    dataset_metrics = {}
    
    train_table_metrics, eval_table_metrics, x_displacement, y_displacement = get_table_displacements()

    dataset_metrics["train"] = train_table_metrics
    dataset_metrics["eval"] = eval_table_metrics

    for school in schools_list:
        
        head_studies = create_head_studies_profile(names=names, family_names=family_names)
        secretary_name = create_secretary_profile(names=names, family_names=family_names)

        for student in tqdm(range(STUDENTS)):

            pdf_instance = PDF()
            student_profile, student_name = create_student_profile(names=names, family_names=family_names)
            pdf_instance.school_setter(school, secretary_name, student_name)
            pdf_instance.header_features_setter(header_rect=True, header_badge=True, header_title=False, header_info=True)
            pdf_instance.body_features_setter()
            list_of_dicts = []

            for academic_year in ACADEMIC_YEARS:
                
                pdf_instance.year_setter(academic_year)

                extra_info_dict = {'Curso': academic_year}
                png_dict = {}

                pdf_instance.png_dict_setter(png_dict=png_dict)
                pdf_instance.add_page()
                pdf_instance.set_font("helvetica", size=14)
                pdf_instance.move_abscissa(displacement=5)

                if JUST_TABLE:
                    grades_per_year = pdf_instance.body_just_table(subjects_semantic, x_displacement[student], y_displacement[student])

                else:

                    pdf_instance.adhoc_header()
                    pdf_instance.move_abscissa(displacement=5)
                    grades_per_year = pdf_instance.body(subjects_semantic, x_displacement[student], y_displacement[student])
                    # TODO Hardcoded Education Level
                    pdf_instance.move_abscissa(displacement=10)
                    # pdf_instance.contextual_information(student_profile, extra_info_dict)
                    pdf_instance.signature()
                
                dictionary = pdf_instance.png_dict_getter()
                list_of_dicts.append(dictionary)
                
            pdf_name = os.path.join(PDF_DOCS_FOLDER, "".join([str(student).zfill(DOCS_Z_FILL), ".pdf"]))
            pdf_instance.set_meta_data()
            
            try:
                pdf_instance.output(pdf_name)

            except FileNotFoundError:
                os.makedirs (PDF_DOCS_FOLDER)
                pdf_instance.output(pdf_name)

            # Convert '.pdf' to '.png'
            # TODO is there any other more efficient way?
            images = convert_from_path(pdf_name)

            pngs_folder = os.path.join(PNG_DOCS_FOLDER, str(student).zfill(DOCS_Z_FILL))

            for i, image in enumerate(images):

                image_copy = np.asarray(image)
                image_copy = cv2.cvtColor(image_copy, cv2.COLOR_BGR2RGB)

                # show_image(img=image_copy)
                png_number = str(i).zfill(DOCS_Z_FILL)
                image_path = os.path.join(pngs_folder, "".join([png_number, '.png']))
                
                dict = list_of_dicts[i]

                try:
                    image.save(image_path)
                    save_layout(img=image_copy, img_name=png_number, path=pngs_folder, dict=dict)
                    generate_json(json_path=pngs_folder, json_number=png_number, dict=dict)

                except FileNotFoundError:
                    os.makedirs (pngs_folder)
                    image.save(image_path)
                    save_layout(img=image_copy, img_name=png_number, path=pngs_folder, dict=dict)
                    generate_json(json_path=pngs_folder, json_number=png_number, dict=dict)

                """
                Also, save in the funsd fashion the '.png' and '.json' (with labels)
                In addition, save a '.json' with the ground truth
                """
                
                student_number = str(student).zfill(DOCS_Z_FILL)
                id = "".join([student_number, '_', str(i)])
                
                # Save the image
                image_path_funsd_fashion = os.path.join(DSET_IMGS_FOLDER, "".join([id, '.png']))
                image.save(image_path_funsd_fashion)

                # Save the '.json' with labels
                generate_json(json_path=DSET_ANNOTATIONS_FOLDER, json_number=id, dict=dict)

                # Save the '.json' with ground truth
                generate_json(json_path=DSET_GROUND_TRUTH_FOLDER, json_number=id, dict=grades_per_year[i])

        # TODO remove this 'break'    
        break

    generate_json(json_path=os.getcwd(), json_number="dataset_metrics", dict=dataset_metrics)
