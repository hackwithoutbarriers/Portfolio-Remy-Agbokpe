# check_images.py
import os
import json
from app import app

def check_project_images():
    """Vérifie que toutes les images des projets existent"""
    projects_file = os.path.join(app.root_path, 'data', 'projects.json')
    
    with open(projects_file, "r", encoding="utf-8") as f:
        projects = json.load(f)
    
    missing_images = []
    
    for project in projects:
        image_path = os.path.join(app.root_path, 'static', project['image'])
        if not os.path.exists(image_path):
            missing_images.append({
                'project': project['title'],
                'expected_path': image_path,
                'image_url': project['image']
            })
            print(f"❌ Image manquante: {project['title']} -> {project['image']}")
        else:
            print(f"✅ Image trouvée: {project['title']}")
    
    return missing_images

if __name__ == "__main__":
    with app.app_context():
        missing = check_project_images()
        if missing:
            print(f"\n{len(missing)} images manquantes détectées!")
        else:
            print("\n✅ Toutes les images sont présentes!")