from flask import Flask, render_template, jsonify, request
from owlready2 import *
import urllib.request
from datetime import datetime
import pytz
import os

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
app = Flask(__name__, template_folder=template_dir)

# --- KONFIGURASI PENTING ---
# Ganti 'USERNAME' dengan username GitHub Anda yang asli.
# Pastikan repository Anda bersifat PUBLIC.
GITHUB_USERNAME = "veenda" 
REPO_NAME = "Terrain-Theory-Ontology"
BRANCH = "main"

# URL Raw otomatis tersusun
ONTOLOGY_URL = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/{BRANCH}/ontology/Terrain.ttl"

# Set Zona Waktu ke Indonesia (WIB)
TIMEZONE = pytz.timezone('Asia/Jakarta')

# --- LOAD ONTOLOGY ---
# Download file .ttl ke memori sementara server (agar tidak perlu simpan file fisik)
try:
    print(f"📥 Downloading ontology from: {ONTOLOGY_URL}")
    urllib.request.urlretrieve(ONTOLOGY_URL, "/tmp/terrain.ttl")
    
    # Load Ontology dengan Owlready2
    onto = get_ontology("/tmp/terrain.ttl").load()
    print("✅ Ontology Loaded Successfully!")
except Exception as e:
    print(f"❌ Error loading ontology: {e}")
    print("Pastikan URL GitHub benar dan Repository PUBLIC.")

# --- HELPER FUNCTIONS ---

def clean_name(entity):
    """Membersihkan nama dari format owl (misal: terrain.Melon -> Melon)"""
    if hasattr(entity, 'name'):
        return entity.name.replace("_", " ")
    return str(entity)

def get_current_phase():
    """Menentukan Fase Tubuh berdasarkan Jam WIB sekarang"""
    now = datetime.now(TIMEZONE).hour
    
    # Logika 3 Siklus Dr. Sebi
    if 4 <= now < 12:
        return "1_EliminationPhase", "Pagi (Detox Mode)"
    elif 12 <= now < 20:
        return "2_AppropriationPhase", "Siang-Sore (Eating Mode)"
    else:
        # Mencakup jam 20:00 sampai 23:59 DAN 00:00 sampai 03:59
        return "3_AssimilationPhase", "Malam (Rest & Repair Mode)"

def check_restriction(food_individual, property_name, target_name=None):
    """
    Fungsi Cerdas pengganti Reasoner.
    Mengecek apakah makanan punya aturan (Restriction) di level Class Induknya.
    Contoh: Apakah 'Melon' (anak SebiFruits) punya aturan 'cleansesOrgan' ke 'Kidneys'?
    """
    # 1. Cek semua induk (Parent Classes)
    for parent in food_individual.is_a:
        # Cek apakah induk adalah Aturan (Restriction), bukan sekadar Class biasa
        if isinstance(parent, owlready2.class_construct.Restriction):
            if parent.property.name == property_name:
                
                # Ambil nilai targetnya (misal: Kidneys)
                target = parent.value
                
                # Kasus A: Kita cuma mau tau targetnya apa (tanpa filter nama)
                if target_name is None:
                    return target.name if hasattr(target, 'name') else str(target)
                
                # Kasus B: Kita mau cek kecocokan dengan organ tertentu
                if hasattr(target, 'name') and target.name == target_name:
                    return True
                
    # 2. Cek juga jika ada mapping langsung di individual (Panel Types di Protege)
    direct_props = getattr(food_individual, property_name, [])
    for item in direct_props:
        if hasattr(item, 'name') and (target_name is None or item.name == target_name):
            return item.name if target_name is None else True
            
    return None if target_name is None else False

def get_allowed_phases_list(food_individual):
    """Mencari semua fase waktu yang diizinkan untuk makanan ini"""
    phases = []
    
    # Cek dari warisan induk (Class Restriction)
    for parent in food_individual.is_a:
        if isinstance(parent, owlready2.class_construct.Restriction):
            if parent.property.name == 'bestConsumedDuring':
                target = parent.value
                if hasattr(target, 'name'):
                    phases.append(target.name)
    
    # Cek dari individual langsung
    if hasattr(food_individual, 'bestConsumedDuring'):
        for phase in food_individual.bestConsumedDuring:
            phases.append(phase.name)
            
    return phases

# --- ROUTES (Jalur Web) ---

@app.route('/')
def home():
    """Halaman Utama"""
    return render_template('index.html')

@app.route('/get_diseases')
def get_diseases():
    """API untuk mengambil daftar penyakit untuk Dropdown"""
    diseases = []
    # Cari Class Manifestation
    manifestation_class = onto.search_one(iri="*Manifestation")
    
    if manifestation_class:
        for cls in manifestation_class.descendants():
            if cls != manifestation_class:
                diseases.append({"id": cls.name, "label": clean_name(cls)})
    
    # Urutkan abjad A-Z
    diseases.sort(key=lambda x: x['label'])
    return jsonify(diseases)

@app.route('/diagnose', methods=['POST'])
def diagnose():
    """API Utama: Menerima ID Penyakit, Mengembalikan Solusi"""
    data = request.json
    disease_id = data.get('disease_id')
    
    # 1. Cek Waktu Sekarang
    current_phase_id, phase_label = get_current_phase()
    
    # 2. Cari Penyakit di Ontology
    disease = onto.search_one(iri=f"*{disease_id}")
    if not disease:
        return jsonify({"error": "Penyakit tidak ditemukan"}), 404

    result = {
        "disease_name": clean_name(disease),
        "current_time_phase": phase_label,
        "affected_organs": [],
        "recommendations": []
    }

    # 3. Analisis Organ Terdampak
    # Kita cari organ dari properti 'affectsSystem'
    target_organs_names = []
    
    # Cek Restriction pada Class Penyakit (Level Class)
    for parent in disease.is_a:
        if isinstance(parent, owlready2.class_construct.Restriction):
            if parent.property.name == 'affectsSystem':
                val = parent.value
                if hasattr(val, 'name'):
                    target_organs_names.append(val.name)
    
    # Cek Direct Property (Level Individual/Asserted)
    if hasattr(disease, 'affectsSystem'):
         for o in disease.affectsSystem:
             if o.name not in target_organs_names:
                 target_organs_names.append(o.name)
             
    # Simpan nama organ ke result agar muncul di web
    result["affected_organs"] = [o.replace("_", " ") for o in target_organs_names]
    
    # 4. Cari Makanan Solusi
    # Ambil semua makanan yang ada di DietaryInput
    if hasattr(onto, 'DietaryInput'):
        all_foods = list(onto.DietaryInput.instances())
    else:
        # Fallback jika DietaryInput tidak ditemukan langsung
        all_foods = []
        electric_class = onto.search_one(iri="*ElectricFoods")
        if electric_class:
            all_foods = electric_class.instances()

    for organ_name in target_organs_names:
        for food in all_foods:
            # LOGIKA INTI:
            # Apakah makanan ini membersihkan (cleanses) ATAU menutrisi (nourishes) organ ini?
            is_cleanser = check_restriction(food, 'cleansesOrgan', organ_name)
            is_nourisher = check_restriction(food, 'nourishesSystem', organ_name)
            
            if is_cleanser or is_nourisher:
                # Makanan ini COCOK untuk organ, sekarang cek WAKTU
                allowed_phases = get_allowed_phases_list(food)
                
                status = "Allowed"
                warning = ""
                
                # Jika makanan punya aturan waktu, tapi fase sekarang TIDAK cocok
                if allowed_phases and current_phase_id not in allowed_phases:
                    status = "Not Recommended Now"
                    # Bersihkan nama fase agar enak dibaca user
                    phase_pretty = [p.replace("1_", "").replace("2_", "").replace("3_", "").replace("Phase", "") for p in allowed_phases]
                    warning = f"Tunggu Fase: {', '.join(phase_pretty)}"
                
                # Tentukan Tipe (Herbal vs Food)
                food_type = "Food"
                # Cek apakah dia turunan dari HerbalTeas
                for parent in food.is_a:
                    if hasattr(parent, 'name') and "Herbal" in parent.name:
                        food_type = "Herbal"
                        break

                result["recommendations"].append({
                    "food_name": clean_name(food),
                    "target_organ": organ_name.replace("_", " "),
                    "status": status,
                    "warning": warning,
                    "type": food_type
                })

    # 5. Membersihkan Duplikat (Deduping)
    # Satu makanan mungkin muncul 2x jika dia membersihkan 2 organ berbeda
    seen = set()
    unique_recs = []
    for r in result["recommendations"]:
        key = (r['food_name'], r['target_organ']) # Unik berdasarkan nama & organ
        if key not in seen:
            seen.add(key)
            unique_recs.append(r)
            
    # Urutkan: Yang 'Allowed' di atas, yang 'Not Recommended' di bawah
    unique_recs.sort(key=lambda x: x['status'])
    
    result["recommendations"] = unique_recs
    
    return jsonify(result)

# Jalankan lokal (untuk testing di laptop)
if __name__ == '__main__':
    app.run(debug=True)