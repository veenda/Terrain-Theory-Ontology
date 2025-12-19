from owlready2 import *
import os

def load_knowledge(filename="Terrain.ttl"):
    """
    Memuat ontologi dengan mode Debugging.
    Jika error, pesan error akan dikirim ke Dropdown di website.
    """
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_path, filename)
    
    print(f"📥 Loading Ontology from: {file_path}")
    
    try:
        # 1. SANITASI FILE (Hapus baris @base yang bikin error di Vercel)
        if not os.path.exists(file_path):
            return {"onto": None, "diseases_list": [{"id": "err", "name": f"❌ Error: File {filename} tidak ditemukan!"}]}

        with open(file_path, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
        
        # Hapus baris yang mengandung '@base'
        clean_content = "".join([l for l in lines if not l.strip().startswith("@base")])
        
        # Simpan ke folder sementara
        tmp_path = "/tmp/terrain_fixed.ttl"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(clean_content)
            
        # 2. LOAD ONTOLOGI
        try:
            onto = get_ontology(tmp_path).load()
        except Exception as e:
            return {"onto": None, "diseases_list": [{"id": "err", "name": f"❌ Parse Error: {str(e)[:50]}..."}]}

        # 3. CARI PENYAKIT (Metode Leluhur/Ancestors)
        diseases = []
        
        # Cari kelas 'Manifestation' (Root dari semua penyakit)
        root = onto.search_one(iri="*Manifestation")
        
        if not root:
            # Coba cari manual jika search_one gagal
            for cls in onto.classes():
                if "Manifestation" in cls.name and "Skin" not in cls.name: # Cari yg umum
                    root = cls
                    break
        
        if not root:
            return {"onto": onto, "diseases_list": [{"id": "err", "name": "❌ Error: Kelas 'Manifestation' tidak ditemukan"}]}

        # Iterasi semua kelas dan cek apakah mereka anak dari Root
        count = 0
        for cls in onto.classes():
            try:
                # Cek apakah 'root' ada di dalam daftar leluhur (ancestors) kelas ini
                if cls != root and root in cls.ancestors():
                    
                    # FILTER: Jangan masukkan kategori induk (yang namanya mengandung 'Manifestation')
                    # Kecuali Anda ingin kategori juga muncul, hapus baris if ini.
                    if "Manifestation" in cls.name:
                        continue 
                    
                    clean_name = cls.name.replace("_", " ")
                    diseases.append({
                        "id": cls.name,
                        "name": clean_name
                    })
                    count += 1
            except:
                continue

        # 4. HASIL
        if count == 0:
            return {"onto": onto, "diseases_list": [{"id": "err", "name": "⚠️ 0 Penyakit ditemukan (Cek Hierarki)"}]}

        diseases.sort(key=lambda x: x["name"])
        print(f"✅ Berhasil memuat {count} penyakit.")
        
        return {
            "onto": onto,
            "diseases_list": diseases
        }
        
    except Exception as e:
        # Tangkap error tak terduga
        print(f"❌ CRITICAL ERROR: {e}")
        return {
            "onto": None,
            "diseases_list": [{"id": "err", "name": f"🔥 System Error: {str(e)}"}]
        }