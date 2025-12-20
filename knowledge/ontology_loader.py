from dataclasses import dataclass, field
from typing import List, Dict, Any
from rdflib import Graph, Namespace, RDF, RDFS, OWL, BNode
import os

# Namespace Ontologi
OTO = Namespace("http://www.semanticweb.org/hp/ontologies/2025/10/untitled-ontology-11/")
VEENDA = Namespace("http://www.github.com/veenda/Terrain-Theory-Ontology/ontology#")

@dataclass
class Disease:
    id: str
    name: str
    affected_organs: List[str] = field(default_factory=list)
    terrain_phase: str = "General"

# Kita hapus @dataclass untuk Category agar lebih fleksibel, 
# atau kita konversi manual nanti. Biarkan dulu untuk struktur internal.
@dataclass
class Category:
    id: str
    name: str
    diseases: List[Dict] = field(default_factory=list)

@dataclass
class Food:
    id: str
    name: str
    type: str
    cleanses: List[str] = field(default_factory=list)
    nourishes: List[str] = field(default_factory=list)
    best_phases: List[str] = field(default_factory=list)

def get_label(graph, entity):
    label = graph.value(entity, RDFS.label)
    if label: return str(label)
    if hasattr(entity, 'split'):
        return entity.split("#")[-1].split("/")[-1].replace("_", " ")
    return str(entity)

def resolve_restriction(graph, subject, property_uri):
    targets = []
    # 1. Direct
    for obj in graph.objects(subject, property_uri):
        if not isinstance(obj, BNode): targets.append(get_label(graph, obj))
    # 2. SubClassOf Restriction
    for parent in graph.objects(subject, RDFS.subClassOf):
        if isinstance(parent, BNode):
            if (parent, OWL.onProperty, property_uri) in graph:
                target = graph.value(parent, OWL.someValuesFrom)
                if target and not isinstance(target, BNode):
                    targets.append(get_label(graph, target))
    # 3. Type Restriction
    for type_node in graph.objects(subject, RDF.type):
        if isinstance(type_node, BNode):
            if (type_node, OWL.onProperty, property_uri) in graph:
                target = graph.value(type_node, OWL.someValuesFrom)
                if target and not isinstance(target, BNode):
                    targets.append(get_label(graph, target))
    return list(set(targets))

def load_knowledge(filename="Terrain.ttl") -> Dict[str, Any]:
    print(f"📥 Loading Ontology (RDFLib): {filename}")
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_path, filename)

    if not os.path.exists(file_path):
        return {}

    g = Graph()
    try:
        g.parse(file_path, format="turtle")
    except Exception as e:
        print(f"❌ Error Parsing: {e}")
        return {}

    # --- 1. LOAD CATEGORIES & DISEASES ---
    categories_map = {}
    diseases_dict = {}

    all_classes = set(g.subjects(RDF.type, OWL.Class))
    
    # A. Identifikasi Kategori
    for cls in all_classes:
        label = get_label(g, cls)
        if "Manifestation" in label and label != "Manifestation":
            cat_id = str(cls).split("#")[-1]
            cat_name = label.replace("Manifestation", "").strip() or "General"
            
            if cat_id not in categories_map:
                categories_map[cat_id] = Category(id=cat_id, name=f"{cat_name} Problems")

    categories_list = list(categories_map.values())
    
    # B. Identifikasi Penyakit
    for cls in all_classes:
        label = get_label(g, cls)
        if "Manifestation" not in label: # Penyakit (Leaf Node)
            
            # Cari Parent Kategori
            parent_cat_id = None
            for parent in g.objects(cls, RDFS.subClassOf):
                p_str = str(parent)
                for cat in categories_list:
                    if cat.id in p_str:
                        parent_cat_id = cat.id
                        break
            
            # Jika punya parent kategori, masukkan
            if parent_cat_id:
                disease_id = str(cls).split("#")[-1]
                organs = resolve_restriction(g, cls, OTO.affectsSystem)
                phases = resolve_restriction(g, cls, OTO.hasTerrainPhase)
                phase_label = phases[0] if phases else "General"
                
                # Simpan Object Disease (untuk Inference)
                diseases_dict[disease_id] = Disease(
                    id=disease_id, name=label, 
                    affected_organs=organs, terrain_phase=phase_label
                )
                
                # Simpan Dict Sederhana (untuk Dropdown)
                categories_map[parent_cat_id].diseases.append({
                    "id": disease_id, 
                    "name": label
                })

    # C. Finalisasi Kategori
    final_categories = [c for c in categories_list if c.diseases]
    for c in final_categories:
        c.diseases.sort(key=lambda x: x['name'])
    final_categories.sort(key=lambda x: x.name)

    # --- PERBAIKAN PENTING: Konversi ke Dictionary Biasa ---
    # Agar {{ categories | tojson }} di HTML tidak error
    categories_for_json = [
        {
            "id": c.id,
            "name": c.name,
            "diseases": c.diseases
        }
        for c in final_categories
    ]

    # --- 2. LOAD FOODS ---
    foods = []
    for ind in g.subjects(RDF.type, OWL.NamedIndividual):
        cleanses = resolve_restriction(g, ind, VEENDA.cleansesOrgan)
        nourishes = resolve_restriction(g, ind, VEENDA.nourishesSystem)
        phases = resolve_restriction(g, ind, VEENDA.bestConsumedDuring)
        
        if cleanses or nourishes or phases:
            f_type = "Herbal" if "Herbal" in str(list(g.objects(ind, RDF.type))) else "Food"
            foods.append(Food(
                id=str(ind).split("#")[-1], name=get_label(g, ind), type=f_type,
                cleanses=cleanses, nourishes=nourishes, best_phases=phases
            ))

    return {
        "categories": categories_for_json, # Pastikan ini kirim LIST OF DICTS
        "diseases_obj": diseases_dict,
        "foods_obj": foods
    }