from owlready2 import *
import os

def load_knowledge(filename="Terrain.ttl"):
    """
    Loader 'Anti-Gagal' untuk Vercel.
    Membersihkan file dari sintaks @base yang bermasalah,
    dan melakukan iterasi manual untuk memastikan penyakit terdeteksi.
    """
    
    # 1. Tentukan lokasi file
    # Kita naik satu level dari folder 'knowledge' untuk ke root
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_path, filename)
    
    print(f"📥 Loading Ontology from: {file_path}")
    
    # Siapkan list default (berisi error jika nanti gagal)
    diseases = []
    onto = None

    try:
        # --- TAHAP 1: PEMBERSIHAN FILE (Sanitasi) ---
        if not os.path.exists(file_path):
            return {"onto": None, "diseases_list": [{"id": "err", "name": "❌ Error: File Terrain.ttl tidak ditemukan"}]}

        # Baca file asli dengan encoding UTF-8 (menangani karakter aneh/BOM)
        with open(file_path, "r", encoding="utf-8-sig") as f:
            raw_lines = f.readlines()

        # Hapus baris yang mengandung '@base' (Penyebab utama error parsing di Vercel)
        clean_content = "".join([line for line in raw_lines if not line.strip().startswith("@base")])
        
        # Simpan versi bersih ke folder sementara (/tmp) milik Vercel
        tmp_path = "/tmp/terrain_clean.ttl"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(clean_content)
            
        print("🧹 File berhasil dibersihkan dari @base.")

        # --- TAHAP 2: LOADING KE MEMORI ---
        try:
            # Load dari file sementara yang sudah bersih
            onto = get_ontology(tmp_path).load()
            print("✅ Ontology Loaded Successfully!")
        except Exception as e:
            # Jika loading gagal, kirim pesan error ke dropdown
            error_msg = str(e)[:50] # Ambil 50 huruf pertama errornya
            return {"onto": None, "diseases_list": [{"id": "err", "name": f"❌ Gagal Load: {error_msg}..."}]}

        # --- TAHAP 3: PENCARIAN PENYAKIT (Metode Manual) ---
        # Kita cari semua kelas yang namanya TIDAK mengandung "Manifestation" (artinya dia penyakit spesifik)
        # tapi dia adalah TURUNAN dari sesuatu yang berbau "Manifestation".
        
        found_count = 0
        
        # Ambil SEMUA kelas di ontologi
        for cls in onto.classes():
            try:
                # Cek leluhur kelas ini (Ancestors)
                # Apakah salah satu leluhurnya punya nama "Manifestation"?
                is_disease = False
                for ancestor in cls.ancestors():
                    if "Manifestation" in ancestor.name and ancestor != cls:
                        is_disease = True
                        break
                
                if is_disease:
                    # FILTER TAMBAHAN:
                    # Kita tidak mau menampilkan Kategori Induk (misal: SkinManifestation)
                    # Kita cuma mau anak-anaknya (misal: Acne, Eczema)
                    # Jadi jika nama kelasnya sendiri mengandung "Manifestation", kita skip.
                    if "Manifestation" in cls.name:
                        continue

                    # Bersihkan nama (hilangkan underscore)
                    clean_name = cls.name.replace("_", " ")
                    
                    diseases.append({
                        "id": cls.name,
                        "name": clean_name
                    })
                    found_count += 1
            except:
                continue

        # Sortir Abjad A-Z
        diseases.sort(key=lambda x: x["name"])

        # Jika kosong, beri laporan
        if found_count == 0:
            diseases.append({"id": "empty", "name": "⚠️ Tidak ada penyakit ditemukan (Cek Struktur)"})
        
        print(f"📊 Total Penyakit: {found_count}")
        
        return {
            "onto": onto,
            "diseases_list": diseases
        }

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        return {
            "onto": None,
            "diseases_list": [{"id": "err", "name": f"🔥 System Error: {str(e)}"}]
        }