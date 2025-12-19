from owlready2 import *
import os

def load_knowledge(filename="Terrain.ttl"):
    """
    Memuat ontologi Terrain Theory dengan teknik 'Sanitasi In-Memory'
    agar tidak error saat membaca @base di lingkungan Vercel.
    """
    # 1. Tentukan path file asli
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_path, filename)
    
    print(f"📥 Loading Ontology from: {file_path}")
    
    try:
        # --- TEKNIK BYPASS ERROR PARSING ---
        # Baca konten file asli sebagai teks
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.readlines()
            
        # Filter/Hapus baris yang mengandung '@base' karena ini penyebab error di Vercel
        # Kita simpan hasilnya ke string baru
        clean_lines = [line for line in raw_content if not line.strip().startswith("@base")]
        clean_content = "".join(clean_lines)
        
        # Simpan file bersih ini ke folder sementara (/tmp) yang bisa ditulisi oleh Vercel
        tmp_path = "/tmp/clean_terrain.ttl"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(clean_content)
            
        print("🧹 Sanitasi Ontologi Selesai (Baris @base dihapus di memori)")
        
        # -----------------------------------

        # Load file sementara yang sudah bersih
        onto = get_ontology(tmp_path).load()
        print("✅ Ontology Loaded Successfully!")
        
        # Pre-fetch data penting untuk dropdown (Cache)
        diseases = []
        # Cari kelas Manifestation (pastikan wildcard * bekerja)
        manifestation = onto.search_one(iri="*Manifestation")
        
        if manifestation:
            for cls in manifestation.descendants():
                if cls != manifestation:
                    diseases.append({
                        "id": cls.name, 
                        "name": cls.name.replace("_", " "),
                        "description": "" 
                    })
        
        # Sortir A-Z
        diseases.sort(key=lambda x: x["name"])
        
        return {
            "onto": onto,
            "diseases_list": diseases
        }
        
    except Exception as e:
        print(f"❌ Error loading ontology: {e}")
        # Fallback darurat: return dictionary kosong agar app tidak crash total
        return {
            "onto": None,
            "diseases_list": []
        }