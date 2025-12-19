from dataclasses import dataclass, field
from typing import List, Dict, Any, Set
from rdflib import Graph, Namespace, RDF, RDFS, OWL, BNode, URIRef
import os

# Definisikan Namespace sesuai file TTL Anda
# Perhatikan: Base URI di file Anda agak unik, kita sesuaikan agar matching
OTO = Namespace("http://www.semanticweb.org/hp/ontologies/2025/10/untitled-ontology-11/")
VEENDA = Namespace("http://www.github.com/veenda/Terrain-Theory-Ontology/ontology#")

@dataclass
class Disease:
    id: str
    name: str
    affected_organs: List[str] = field(default_factory=list)
    terrain_phase: str = "Unknown Phase"

@dataclass
class Food:
    id: str
    name: str
    type: str # Herbal / Food
    cleanses: List[str] = field(default_factory=list)
    nourishes: List[str] = field(default_factory=list)
    best_phases: List[str] = field(default_factory=list)

def get_label(graph, entity):
    """Ambil label yang bisa dibaca manusia, fallback ke ID"""
    label = graph.value(entity, RDFS.label)
    if label:
        return str(label)
    return entity.split("#")[-1].split("/")[-1].replace("_", " ")

def resolve_restriction(graph, subject, property_uri):
    """
    Mencari target dari OWL Restriction.
    Contoh: Acne -> subClassOf -> [onProperty affectsSystem; someValuesFrom Skin]
    """
    targets = []
    
    # 1. Cek properti langsung (Direct Property)
    for obj in graph.objects(subject, property_uri):
        if not isinstance(obj, BNode):
            targets.append(get_label(graph, obj))

    # 2. Cek Restriction via rdfs:subClassOf (untuk Kelas/Penyakit)
    for parent in graph.objects(subject, RDFS.subClassOf):
        if isinstance(parent, BNode):
            # Cek apakah ini restriction pada properti yang dicari
            if (parent, OWL.onProperty, property_uri) in graph:
                target = graph.value(parent, OWL.someValuesFrom)
                # Handle Union/Intersection jika ada (Complex Class)
                if target:
                    if isinstance(target, BNode):
                        # Coba cari elemen list jika itu union/intersection
                        # (Penyederhanaan: ambil label representatif saja)
                        pass 
                    else:
                        targets.append(get_label(graph, target))

    # 3. Cek Restriction via rdf:type (untuk Individual/Makanan)
    for type_node in graph.objects(subject, RDF.type):
        if isinstance(type_node, BNode):
            if (type_node, OWL.onProperty, property_uri) in graph:
                target = graph.value(type_node, OWL.someValuesFrom)
                # Handle target yang berupa unionOf (kumpulan organ)
                if isinstance(target, BNode):
                    # Cek apakah ada unionOf
                    union_list = graph.value(target, OWL.unionOf)
                    if union_list:
                        # Iterasi RDF List sederhana
                        curr = union_list
                        while curr != RDF.nil:
                            item = graph.value(curr, RDF.first)
                            if item:
                                targets.append(get_label(graph, item))
                            curr = graph.value(curr, RDF.rest)
                elif target:
                    targets.append(get_label(graph, target))
    
    return list(set(targets)) # Hapus duplikat

def load_knowledge(filename="Terrain.ttl") -> Dict[str, Any]:
    print(f"📥 Loading Ontology via RDFLib: {filename}")
    
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_path, filename)

    if not os.path.exists(file_path):
        print("❌ File not found!")
        return {}

    g = Graph()
    try:
        g.parse(file_path, format="turtle")
        print(f"✅ Parsed {len(g)} triples.")
    except Exception as e:
        print(f"❌ Error Parsing Turtle: {e}")
        return {}

    # --- 1. LOAD DISEASES ---
    diseases = []
    # Cari semua subclass dari Manifestation
    manifestation_root = OTO.Manifestation
    
    # Kita cari semua subject yang punya Triple: ?s rdfs:subClassOf :Manifestation
    # Catatan: RDFLib tidak otomatis melakukan transitive inference, 
    # jadi kita iterasi manual atau gunakan query path jika perlu.
    # Untuk simplifikasi, kita cari semua yang dideklarasikan sebagai Class
    # dan punya hubungan hierarki ke Manifestation.
    
    all_classes = set(g.subjects(RDF.type, OWL.Class))
    
    for cls in all_classes:
        # Cek apakah dia anak dari Manifestation (cek nama stringnya biar cepat)
        # atau traverse tree (lebih akurat tapi lambat).
        # Kita pakai heuristik sederhana dulu: 
        # Cek apakah dia punya properti "affectsSystem" atau "hasTerrainPhase"
        # Karena di TTL Anda, penyakit didefinisikan dengan properti itu.
        
        is_disease = False
        # Cek apakah punya restriction hasTerrainPhase
        for parent in g.objects(cls, RDFS.subClassOf):
            if isinstance(parent, BNode):
                if (parent, OWL.onProperty, OTO.hasTerrainPhase) in g:
                    is_disease = True
                    break
        
        if is_disease:
            name = get_label(g, cls)
            if "Manifestation" in name: continue # Skip kategori induk
            
            # Extract Organs
            organs = resolve_restriction(g, cls, OTO.affectsSystem)
            
            # Extract Phase
            phases = resolve_restriction(g, cls, OTO.hasTerrainPhase)
            phase_label = phases[0] if phases else "General"
            
            diseases.append(Disease(
                id=str(cls).split("#")[-1].split("/")[-1],
                name=name,
                affected_organs=organs,
                terrain_phase=phase_label
            ))

    diseases.sort(key=lambda x: x.name)

    # --- 2. LOAD FOODS ---
    foods = []
    # Cari semua instance dari DietaryInput
    # Di TTL Anda, Makanan adalah NamedIndividual
    all_individuals = set(g.subjects(RDF.type, OWL.NamedIndividual))
    
    for ind in all_individuals:
        # Cek apakah dia DietaryInput (atau punya properti cleanses/nourishes)
        is_food = False
        
        # Cek tipe restrictions
        cleanses = resolve_restriction(g, ind, VEENDA.cleansesOrgan)
        nourishes = resolve_restriction(g, ind, VEENDA.nourishesSystem)
        best_phases = resolve_restriction(g, ind, VEENDA.bestConsumedDuring)
        
        if cleanses or nourishes or best_phases:
            is_food = True
        
        if is_food:
            name = get_label(g, ind)
            
            # Tentukan tipe (Herbal vs Food)
            # Cek rdf:type langsung
            f_type = "Food"
            for t in g.objects(ind, RDF.type):
                t_str = str(t)
                if "Herbal" in t_str:
                    f_type = "Herbal"
            
            foods.append(Food(
                id=str(ind).split("#")[-1],
                name=name,
                type=f_type,
                cleanses=cleanses,
                nourishes=nourishes,
                best_phases=best_phases
            ))

    print(f"📊 Loaded {len(diseases)} diseases and {len(foods)} foods.")

    # Convert to dictionary for easy access
    diseases_dict = {d.id: d for d in diseases}
    
    return {
        "graph": g,
        "diseases_list": [{"id": d.id, "name": d.name} for d in diseases],
        "diseases_obj": diseases_dict,
        "foods_obj": foods
    }