from datetime import datetime
import pytz
from owlready2 import *

TIMEZONE = pytz.timezone('Asia/Jakarta')

def get_current_phase():
    """Menentukan Fase Tubuh berdasarkan Jam WIB"""
    now = datetime.now(TIMEZONE).hour
    if 4 <= now < 12:
        return "1_EliminationPhase", "Pagi (Detox Mode)"
    elif 12 <= now < 20:
        return "2_AppropriationPhase", "Siang-Sore (Eating Mode)"
    else:
        return "3_AssimilationPhase", "Malam (Rest & Repair Mode)"

def check_restriction(food_individual, property_name, target_name=None):
    """Helper untuk cek properti di level Class (Inheritance)"""
    for parent in food_individual.is_a:
        if isinstance(parent, owlready2.class_construct.Restriction):
            if parent.property.name == property_name:
                target = parent.value
                if target_name is None:
                    return target.name if hasattr(target, 'name') else str(target)
                if hasattr(target, 'name') and target.name == target_name:
                    return True
    
    # Cek direct property
    direct_props = getattr(food_individual, property_name, [])
    for item in direct_props:
        if hasattr(item, 'name') and (target_name is None or item.name == target_name):
            return item.name if target_name is None else True
    return None if target_name is None else False

def get_allowed_phases_list(food_individual):
    """Mencari fase waktu yang cocok untuk makanan"""
    phases = []
    # Cek restriction parent
    for parent in food_individual.is_a:
        if isinstance(parent, owlready2.class_construct.Restriction):
            if parent.property.name == 'bestConsumedDuring':
                target = parent.value
                if hasattr(target, 'name'):
                    phases.append(target.name)
    # Cek direct
    if hasattr(food_individual, 'bestConsumedDuring'):
        for phase in food_individual.bestConsumedDuring:
            phases.append(phase.name)
    return phases

def run_diagnosis(disease_id, knowledge_data):
    """
    Logika Utama: Menerima ID Penyakit -> Output Rekomendasi Makanan
    """
    onto = knowledge_data["onto"]
    current_phase_id, phase_label = get_current_phase()
    
    disease = onto.search_one(iri=f"*{disease_id}")
    if not disease:
        return None

    # Cari Organ Terdampak
    target_organs_names = []
    # Cek Restriction Class
    for parent in disease.is_a:
        if isinstance(parent, owlready2.class_construct.Restriction):
            if parent.property.name == 'affectsSystem':
                val = parent.value
                if hasattr(val, 'name'):
                    target_organs_names.append(val.name)
    # Cek Direct
    if hasattr(disease, 'affectsSystem'):
         for o in disease.affectsSystem:
             if o.name not in target_organs_names:
                 target_organs_names.append(o.name)

    # Cari Makanan
    recommendations = []
    all_foods = []
    
    # Cek apakah ada DietaryInput, jika tidak coba fallback ke ElectricFoods
    if hasattr(onto, 'DietaryInput'):
        all_foods = list(onto.DietaryInput.instances())
    elif hasattr(onto, 'ElectricFoods'): # Fallback jaga-jaga
        all_foods = list(onto.ElectricFoods.instances())

    for organ_name in target_organs_names:
        for food in all_foods:
            # Filter Logic
            is_cleanser = check_restriction(food, 'cleansesOrgan', organ_name)
            is_nourisher = check_restriction(food, 'nourishesSystem', organ_name)
            
            if is_cleanser or is_nourisher:
                allowed_phases = get_allowed_phases_list(food)
                status = "Allowed"
                warning = ""
                
                # Time Filter
                if allowed_phases and current_phase_id not in allowed_phases:
                    status = "Wait"
                    # Bersihkan nama fase agar enak dibaca
                    phase_pretty = [p.replace("1_", "").replace("2_", "").replace("3_", "").replace("Phase", "") for p in allowed_phases]
                    warning = f"Wait for: {', '.join(phase_pretty)}"
                
                food_type = "Food"
                for parent in food.is_a:
                    if hasattr(parent, 'name') and "Herbal" in parent.name:
                        food_type = "Herbal"
                        break

                recommendations.append({
                    "name": food.name.replace("_", " "),
                    "organ": organ_name.replace("_", " "),
                    "status": status,
                    "warning": warning,
                    "type": food_type
                })

    # Deduping & Sorting
    seen = set()
    unique_recs = []
    for r in recommendations:
        key = (r['name'], r['organ'])
        if key not in seen:
            seen.add(key)
            unique_recs.append(r)
    unique_recs.sort(key=lambda x: x['status']) # Allowed first

    return {
        "disease_name": disease.name.replace("_", " "),
        "phase_info": phase_label,
        "affected_organs": [o.replace("_", " ") for o in target_organs_names],
        "recommendations": unique_recs
    }