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
    """Membersihkan nama fase agar cocok (misal 'AppropriationCycle' -> 'Appropriation Phase')"""
    if "Appropriation" in phase_name: return "Appropriation Phase"
    if "Elimination" in phase_name: return "Elimination Phase"
    if "Assimilation" in phase_name: return "Assimilation Phase"
    return phase_name

def run_diagnosis(disease_id, knowledge_data):
    """
    Logika Utama (Versi RDFLib Compatible)
    """
    if not knowledge_data:
        return None

    diseases_dict = knowledge_data.get("diseases_obj", {})
    all_foods = knowledge_data.get("foods_obj", [])
    
    # Ambil objek penyakit dari dictionary
    disease = diseases_dict.get(disease_id)
    if not disease:
        return None

    current_phase_key, phase_label = get_current_phase()
    
    # Organ Target
    target_organs = disease.affected_organs
    # Bersihkan nama organ (misal "Liver" tetap "Liver")
    
    recommendations = []

    for food in all_foods:
        # Cek apakah makanan ini membersihkan atau menutrisi organ yang sakit
        is_relevant = False
        relevant_organ = ""
        
        # Cek Cleanses
        for organ in target_organs:
            if organ in food.cleanses:
                is_relevant = True
                relevant_organ = organ
                break # Prioritas cleansing
            if organ in food.nourishes:
                is_relevant = True
                relevant_organ = organ
        
        if is_relevant:
            # Cek Waktu Konsumsi
            status = "Allowed"
            warning = ""
            
            # Normalisasi fase makanan
            food_phases = [normalize_phase_name(p) for p in food.best_phases]
            
            if food_phases:
                if current_phase_key not in food_phases:
                    status = "Wait"
                    warning = f"Tunggu: {', '.join(food_phases)}"
            
            recommendations.append({
                "name": food.name,
                "organ": relevant_organ,
                "status": status,
                "warning": warning,
                "type": food.type
            })

    # Deduping & Sorting
    seen = set()
    unique_recs = []
    for r in recommendations:
        key = (r['name'], r['organ'])
        if key not in seen:
            seen.add(key)
            unique_recs.append(r)
    
    # Sort: Allowed dulu, lalu Wait. Di dalam itu urut nama.
    unique_recs.sort(key=lambda x: (x['status'] != 'Allowed', x['name']))

    return {
        "disease_name": disease.name,
        "phase_info": phase_label,
        "affected_organs": target_organs,
        "recommendations": unique_recs
    }