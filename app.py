from flask import Flask, render_template, request, redirect, url_for
from knowledge.ontology_loader import load_knowledge
from knowledge.inference import run_diagnosis

app = Flask(__name__)

# Load Knowledge saat startup
# Pastikan file 'Terrain.ttl' ada di folder yang sama dengan app.py
knowledge = load_knowledge("Terrain.ttl")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/diagnose", methods=["GET", "POST"])
def diagnose_view():
    # Jika Data Gagal Load
    if not knowledge:
        return render_template("base.html", error="Ontology failed to load.")

    if request.method == "GET":
        # Tampilkan Dropdown Penyakit
        diseases = knowledge.get("diseases_list", [])
        return render_template("diagnose.html", diseases=diseases)
    
    # POST: Proses Diagnosa
    disease_id = request.form.get("disease_id")
    if not disease_id:
        return redirect(url_for('diagnose_view'))
        
    result = run_diagnosis(disease_id, knowledge)
    return render_template("result.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)