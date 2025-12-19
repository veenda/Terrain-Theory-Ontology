from owlready2 import *
import os

def load_knowledge(filename="Terrain.ttl"):
    """
    Memuat ontologi Terrain Theory dengan teknik 'Sanitasi In-Memory'
    dan iterasi manual agar SEMUA penyakit terdeteksi.
    """
    # 1. Tentukan path file asli
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_path, filename)
    
    print(f"📥 Loading Ontology from: {file_path}")
    
    try:
        # --- TEKNIK 1: SANITASI FILE (BYPASS ERROR @base) ---
        # Baca konten file asli sebagai teks (gunakan utf-8-sig untuk handle BOM)
        with open(file_path, "r", encoding="utf-8-sig") as f:
            raw_content = f.readlines()
            
        # Hapus baris yang mengandung '@base' agar parser Vercel tidak error
        clean_lines = [line for line in raw_content if not line.strip().startswith("@base")]
        clean_content = "".join(clean_lines)
        
        # Simpan file bersih ke folder sementara
        tmp_path = "/tmp/clean_terrain.ttl"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(clean_content)
            
        print("🧹 Sanitasi Selesai: @base dihapus.")
        # ----------------------------------------------------

        # Load file sementara
        onto = get_ontology(tmp_path).load()
        print("✅ Ontology Loaded Successfully!")
        
        diseases = []
        
        # --- TEKNIK 2: PENCARIAN PENYAKIT (LEBIH KUAT) ---
        
        # Cari kelas induk "Manifestation" dengan IRI lengkap
        # Sesuaikan dengan prefix di file Terrain.ttl Anda
        iri_root = "http://www.semanticweb.org/hp/ontologies/2025/10/untitled-ontology-11/Manifestation"
        root = onto.search_one(iri=iri_root)
        
        # Fallback jika IRI berubah/salah, cari wildcard
        if not root:
             print(f"⚠️ Warning: Root IRI {iri_root} tidak ditemukan. Mencoba wildcard...")
             root = onto.search_one(iri="*Manifestation")

        if root:
            # Iterasi SEMUA kelas yang ada di ontologi (dijamin tidak ada yang terlewat)
            for cls in onto.classes():
                try:
                    # Cek apakah cls adalah turunan dari Root (Manifestation)
                    if cls != root and issubclass(cls, root):
                        
                        # FILTER PENTING:
                        # Jangan masukkan "Kategori" (yang namanya mengandung 'Manifestation')
                        # Kita hanya mau Penyakit spesifik (Leaf Nodes) seperti 'Acne', 'Diabetes', dll.
                        if "Manifestation" in cls.name:
                            continue 
                        
                        # Format Nama agar rapi (hapus underscore)
                        clean_name = cls.name.replace("_", " ")
                        
                        diseases.append({
                            "id": cls.name,
                            "name": clean_name
                        })
                except:
                    continue
        else:
            print("❌ Error: Kelas 'Manifestation' tidak ditemukan sama sekali di Ontologi.")

        # Sortir A-Z agar mudah dicari di dropdown
        diseases.sort(key=lambda x: x["name"])
        
        print(f"📊 Total Penyakit Ditemukan: {len(diseases)}")
        
        return {
            "onto": onto,
            "diseases_list": diseases
        }
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR loading ontology: {e}")
        return {
            "onto": None,
            "diseases_list": []
        }