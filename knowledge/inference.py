from datetime import datetime
import pytz

TIMEZONE = pytz.timezone('Asia/Jakarta')

def get_current_phase():
    """Menentukan Fase Tubuh berdasarkan Jam WIB"""
    now = datetime.now(TIMEZONE).hour
    if 4 <= now < 12:
        return "Elimination Phase", "Pagi (Detox Mode)"
    elif 12 <= now < 20:
        return "Appropriation Phase", "Siang-Sore (Eating Mode)"
    else:
        return "Assimilation Phase", "Malam (Rest & Repair Mode)"

def normalize_phase_name(phase_name):
    """Membersihkan nama fase dari Ontologi agar cocok dengan jam"""
    p = phase_name.lower()
    if "elimination" in p: return "Elimination Phase"
    if "appropriation" in p: return "Appropriation Phase"
    if "assimilation" in p: return "Assimilation Phase"
    return phase_name

def run_diagnosis(disease_id, knowledge_data):
    """
    Logika Utama Diagnosa (Kompatibel dengan RDFLib Loader)
    """
    if not knowledge_data:
        return None

    # Ambil data dari hasil loader
    diseases_dict = knowledge_data.get("diseases_obj", {})
    all_foods = knowledge_data.get("foods_obj", [])
    
    # 1. Cari Penyakit
    disease = diseases_dict.get(disease_id)
    if not disease:
        return None

    # 2. Cek Waktu
    current_phase_key, phase_label = get_current_phase()
    
    # 3. Cari Organ Terdampak
    target_organs = disease.affected_organs
    
    recommendations = []

    # 4. Filter Makanan
    for food in all_foods:
        is_relevant = False
        relevant_organ = ""
        
        # Cek apakah makanan membersihkan organ yg sakit?
        for organ in target_organs:
            # Cek Cleanses (Prioritas)
            if any(organ in c for c in food.cleanses):
                is_relevant = True
                relevant_organ = organ
                break
            # Cek Nourishes
            if any(organ in n for n in food.nourishes):
                is_relevant = True
                relevant_organ = organ
                break
        
        if is_relevant:
            status = "Allowed"
            warning = ""
            
            # Cek Fase Waktu
            food_phases = [normalize_phase_name(p) for p in food.best_phases]
            
            # Jika makanan punya aturan waktu, dan waktu sekarang tidak cocok
            if food_phases and current_phase_key not in food_phases:
                status = "Wait"
                pretty_phases = [p.replace(" Phase", "") for p in food_phases]
                warning = f"Wait for: {', '.join(pretty_phases)}"
            
            recommendations.append({
                "name": food.name,
                "organ": relevant_organ,
                "status": status,
                "warning": warning,
                "type": food.type
            })

    # 5. Bersihkan Duplikat & Urutkan
    seen = set()
    unique_recs = []
    for r in recommendations:
        key = (r['name'], r['organ'])
        if key not in seen:
            seen.add(key)
            unique_recs.append(r)
    
    # Urutkan: Allowed paling atas, lalu Wait
    unique_recs.sort(key=lambda x: (x['status'] != 'Allowed', x['name']))

    return {
        "disease_name": disease.name,
        "phase_info": phase_label,
        "affected_organs": target_organs,
        "recommendations": unique_recs
    }