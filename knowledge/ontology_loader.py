from owlready2 import *
import os

def load_knowledge(filename="Terrain.ttl"):
    """
    Memuat ontologi Terrain Theory dan mengembalikan objek ontologi.
    """
    # Cek path file (karena di Vercel path bisa tricky)
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_path, filename)
    
    print(f"📥 Loading Ontology from: {file_path}")
    
    try:
        # Load local file
        onto = get_ontology(file_path).load()
        print("✅ Ontology Loaded Successfully!")
        
        # Pre-fetch data penting untuk dropdown (Cache)
        diseases = []
        manifestation = onto.search_one(iri="*Manifestation")
        if manifestation:
            for cls in manifestation.descendants():
                if cls != manifestation:
                    diseases.append({
                        "id": cls.name, 
                        "name": cls.name.replace("_", " "),
                        "description": "" # Bisa ditambah jika ada di ontologi
                    })
        # Sortir A-Z
        diseases.sort(key=lambda x: x["name"])
        
        return {
            "onto": onto,
            "diseases_list": diseases
        }
        
    except Exception as e:
        print(f"❌ Error loading ontology: {e}")
        return None