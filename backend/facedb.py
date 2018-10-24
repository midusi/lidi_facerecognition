import face_recognition
import os
import settings
import numpy as np
import skimage,skimage.io,skimage.exposure
import json
from PIL import Image

class Person:
    def __init__(self,foldername,name,lastname,title,jobs,avatar):
        self.foldername=foldername
        self.name=name
        self.lastname=lastname
        self.jobs=jobs
        self.avatar=avatar
        self.title=title

    def full_name(self):
        if self.title.strip()=="":
            title=""
        else:
            title=self.title+". "

        return title + self.name + " " + self.lastname

    def description(self):
        jobs = [" • " + job for job in self.jobs]
        jobs = "\n".join(jobs)
        return jobs


def get_names_and_paths(face_database_path):
    person_folder_names = [person for person in os.listdir(face_database_path)
                           if os.path.isdir(os.path.join(face_database_path, person))]
    person_folder_names.sort()
    person_folder_paths = [os.path.join(face_database_path, person) for person in person_folder_names]
    return person_folder_names,person_folder_paths


def load_persondb(face_database_path):
    persondb= {}
    person_folder_names, person_folder_paths=get_names_and_paths(face_database_path)


    for class_id,(person_foldername,person_path) in enumerate(zip(person_folder_names,person_folder_paths)):
        with open(os.path.join(person_path, "info.json"), "r",encoding='utf-8') as json_file:
            data = json.load(json_file)
            avatar =Image.open(os.path.join(person_path,"avatar.png"))
            person = Person(person_foldername,data["name"],data["lastname"],data["title"],data["jobs"],avatar)
            persondb[class_id] = person
    return persondb


def get_images_paths(face_database_path):
    person_folder_names, person_folder_paths = get_names_and_paths(face_database_path)
    person_images_paths={}

    for id,(person,person_path) in enumerate(zip(person_folder_names,person_folder_paths)):
        for file in os.listdir(person_path):
            if (file.endswith("png") or file.endswith("jpg")) and  not file.startswith("avatar"):
                path = os.path.join(person_path, file)
                if not id in person_images_paths:
                    person_images_paths[id]=[]
                person_images_paths[id].append(path)

    return person_images_paths

def load_images_and_generate_db(persondb,person_images_paths,previous_x,previous_paths):
    n=sum([len(v) for k,v in person_images_paths.items()])
    print(f"{n} images found total.")
    y_train = np.zeros((n))
    x_train = np.zeros((n,settings.embedding_length))
    all_paths=[]

    i=0
    for id,paths in person_images_paths.items():
        name=persondb[id].name
        lastname=persondb[id].lastname
        print(f"Processing {len(paths)} images for: {lastname}, {name}.")
        for path in paths:
            try:
                index=previous_paths.index(path)
                encodings=[ previous_x[index,:] ]

            except ValueError:
                image=skimage.io.imread(path)
                # top right bottom left
                roi=[(1,image.shape[1]-1,image.shape[0]-1,1)]
                encodings = face_recognition.face_encodings(image,roi)
            n_encodings=len(encodings)
            if n_encodings>1:
                print(f"Warning: found {n_encodings} faces for image {path} (using first).")
            if n_encodings==0:
                raise Exception(f"No faces found for image {path}.")
            else:
                y_train[i] = id
                x_train[i, :] = encodings[0]
                i = i + 1
                all_paths.append(path)

    return x_train,y_train,all_paths


def update(settings):
    if os.path.exists(settings.training_data_file):
        data=np.load(settings.training_data_file)
        x_train, y_train, previous_paths = data["x_train"], data["y_train"], data["paths"]
        previous_paths=list(previous_paths)
    else:
        x_train=[]
        previous_paths=[]


    persondb=load_persondb(settings.face_database_path)
    images_paths=get_images_paths(settings.face_database_path)
    x_train,y_train,all_paths=load_images_and_generate_db(persondb,images_paths,x_train,previous_paths)
    np.savez(settings.training_data_file,x_train=x_train,y_train=y_train,paths=all_paths)
    return persondb,x_train,y_train

if __name__ == '__main__':
    update(settings)