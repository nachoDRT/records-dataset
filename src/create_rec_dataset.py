from pdf2image import convert_from_path
import os
from tqdm import tqdm
import cv2
import numpy as np
import copy
import schools_records as sr
from pdf_records import Pdf_records

ENGLISH = False

if ENGLISH:
    LANGUAGE = "eng"
    ACADEMIC_YEARS = ['3rd highschool year']

else:
    LANGUAGE = "esp"
    ACADEMIC_YEARS = ['3º de la ESO']

PDF_DOCS_FOLDER = os.path.join(os.getcwd(), "synthetic_pdf_docs")
PNG_DOCS_FOLDER = os.path.join(os.getcwd(), "synthetic_png_docs")

DSET_IMGS_FOLDER = os.path.join(os.getcwd(), "ffundacion", "images")
DSET_ANNOTATIONS_FOLDER = os.path.join(os.getcwd(), "ffundacion", "annotations")
DSET_GROUND_TRUTH_FOLDER = os.path.join(os.getcwd(), "ffundacion", "ground_truth")

STUDENTS = 10
# ACADEMIC_YEARS = ['3º de la ESO', '4º de la ESO', '1º de Bachillerato', '2º de Bachillerato']
EDUCATION_LEVEL = ['EDUCACIÓN SECUNDARIA OBLIGATORIA']
SCHOOLS = ['Recuerdo']
JUST_TABLE = False

DOCS_Z_FILL = 4

if __name__ == '__main__':
    
    # TODO en lugar de pasarle el NAMES_TXT, pásale si quieres nombre o apellidos como una string
    names = sr.load_names(info_to_load="first_names", lang=LANGUAGE)
    family_names = sr.load_names(info_to_load="family_names", lang=LANGUAGE)
    schools_list = sr.load_school_info(lang=LANGUAGE)
    subjects_semantic = sr.load_subjects_semantinc(lang=LANGUAGE)

    dataset_metrics = {}
    
    # Generate hyper-parameters for the dataset
    train_table_metrics, eval_table_metrics, x_displacement, y_displacement = sr.get_table_displacements(num_students=STUDENTS)
    train_alpha_numeric_proportion, eval_alpha_numeric_proportion, alpha_num = sr.get_alpha_numeric_proportion(num_students=STUDENTS)

    dataset_metrics["train"] = train_table_metrics
    dataset_metrics["train"]["alph_num_proportion"] = train_alpha_numeric_proportion

    dataset_metrics["eval"] = eval_table_metrics
    dataset_metrics["eval"]["alph_num_proportion"] = eval_alpha_numeric_proportion

    grades_per_subject_metrics = {}

    for label in list(subjects_semantic):
        grades_per_subject_metrics[label] = []

    for school in schools_list:
        
        head_studies = sr.create_head_studies_profile(names=names, family_names=family_names)
        secretary_name = sr.create_secretary_profile(names=names, family_names=family_names)

        for student in tqdm(range(STUDENTS)):

            pdf_instance = Pdf_records()
            student_profile, student_name = sr.create_student_profile(names=names, family_names=family_names)
            pdf_instance.school_setter(school, secretary_name, student_name)
            pdf_instance.header_features_setter(header_rect=True, header_badge=True, header_title=False, header_info=True, lang=LANGUAGE)
            pdf_instance.body_features_setter()
            pdf_instance.random_subjects_setter(copy.deepcopy(subjects_semantic))
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
                    grades_per_year = pdf_instance.body_just_table(subjects_semantic, x_displacement[student], y_displacement[student], alpha_num[student])

                else:

                    pdf_instance.adhoc_header()
                    pdf_instance.move_abscissa(displacement=5)
                    grades_per_year = pdf_instance.body(subjects_semantic, x_displacement[student], y_displacement[student], alpha_num[student], LANGUAGE)
                    # TODO Hardcoded Education Level
                    # pdf_instance.contextual_information(student_profile, extra_info_dict)
                    pdf_instance.signature(lang=LANGUAGE, head_studies=head_studies)
                
                grades_per_subject_metrics = sr.update_grades_per_subject_metrics(metrics=grades_per_subject_metrics, new_grades=grades_per_year[0])
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
                    sr.save_layout(img=image_copy, img_name=png_number, path=pngs_folder, dict=dict)
                    sr.generate_json(json_path=pngs_folder, json_number=png_number, dict=dict)

                except FileNotFoundError:
                    os.makedirs(pngs_folder)
                    image.save(image_path)
                    sr.save_layout(img=image_copy, img_name=png_number, path=pngs_folder, dict=dict)
                    sr.generate_json(json_path=pngs_folder, json_number=png_number, dict=dict)

                """
                Also, save in the funsd fashion the '.png' and '.json' (with labels)
                In addition, save a '.json' with the ground truth
                """
                
                student_number = str(student).zfill(DOCS_Z_FILL)
                id = "".join([student_number, '_', str(i)])
                
                # Save the image
                image_path_funsd_fashion = os.path.join(DSET_IMGS_FOLDER, "".join([id, '.png']))
                try:
                    image.save(image_path_funsd_fashion)
                except FileNotFoundError:
                    os.makedirs(DSET_IMGS_FOLDER)
                    os.makedirs(DSET_ANNOTATIONS_FOLDER)
                    os.makedirs(DSET_GROUND_TRUTH_FOLDER)
                    image.save(image_path_funsd_fashion)
                    # Save the '.json' with labels
                    sr.generate_json(json_path=DSET_ANNOTATIONS_FOLDER, json_number=id, dict=dict)
                    # Save the '.json' with ground truth
                    sr.generate_json(json_path=DSET_GROUND_TRUTH_FOLDER, json_number=id, dict=grades_per_year[i])


                # Save the '.json' with labels
                sr.generate_json(json_path=DSET_ANNOTATIONS_FOLDER, json_number=id, dict=dict)

                # Save the '.json' with ground truth
                sr.generate_json(json_path=DSET_GROUND_TRUTH_FOLDER, json_number=id, dict=grades_per_year[i])

        # TODO remove this 'break'    
        break
    
    dataset_metrics['grades_per_subjects'] = grades_per_subject_metrics
    sr.compute_metrics(metrics=dataset_metrics)
    sr.generate_json(json_path=os.getcwd(), json_number="dataset_metrics", dict=dataset_metrics)
