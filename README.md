# Terrain Theory Ontology 🌱

> **Sistem Pakar Berbasis Ontologi untuk Rekomendasi Kesehatan Bio-Elektrik**

Repositori ini dikembangkan sebagai tugas akhir mata kuliah **Knowledge Base and Reasoning**. Sistem ini menerapkan prinsip *Terrain Theory* (Dr. Sebi) untuk mendiagnosis manifestasi penyakit dan memberikan rekomendasi nutrisi yang selaras dengan ritme sirkadian tubuh (Body Clock).

---

## 📋 Fitur Utama

-   **Diagnosis Berbasis Ontologi:** Menggunakan `rdflib` untuk menelusuri graf pengetahuan (`Terrain.ttl`) yang kompleks.
-   **Rekomendasi Nutrisi Bio-Elektrik:** Menyarankan makanan *Alkaline* dan *Herbal* berdasarkan organ yang terdampak.
-   **Integrasi Ritme Sirkadian:** Rekomendasi disesuaikan dengan jam tubuh pengguna saat ini (Fase Eliminasi, Apropriasi, atau Asimilasi).
-   **Antarmuka Cascading:** Dropdown cerdas yang mengelompokkan penyakit berdasarkan kategori manifestasi.
-   **Clean UI:** Antarmuka modern dengan tema warna alam (Hijau & Biru).

---

## 📖 Tutorial for User (Panduan Pengguna)

Ikuti langkah-langkah berikut untuk menggunakan aplikasi web ini:

1.  **Buka Halaman Utama:**
    Akses website dan klik tombol **"Start Consultation"**.
2.  **Pilih Kategori Manifestasi:**
    Pada halaman konsultasi, pilih jenis keluhan umum pada dropdown pertama (contoh: *Skin Problems* atau *Digestive Problems*).
3.  **Pilih Kondisi Spesifik:**
    Setelah memilih kategori, dropdown kedua akan aktif. Pilih kondisi spesifik yang Anda alami (contoh: *Acne*, *Gastritis*, dll).
4.  **Dapatkan Protokol:**
    Klik tombol **"Generate Protocol"**. Sistem akan menganalisis ontologi dan menampilkan:
    -   Fase tubuh Anda saat ini (berdasarkan waktu server).
    -   Organ yang perlu dipulihkan.
    -   Daftar makanan yang **Dianjurkan (Allowed)** untuk dikonsumsi sekarang.
    -   Daftar makanan yang harus **Ditunggu (Wait)** karena belum masuk fase waktunya.

---

## 💻 Tutorial for Developer (Instalasi Lokal)

Jika Anda ingin menjalankan proyek ini di komputer Anda sendiri, ikuti langkah berikut:

### Prasyarat
-   Python 3.8 atau lebih baru.
-   Git.

### Langkah Instalasi

1.  **Clone Repositori:**
    ```bash
    git clone [https://github.com/username-anda/Terrain-Theory-Ontology.git](https://github.com/username-anda/Terrain-Theory-Ontology.git)
    cd Terrain-Theory-Ontology
    ```

2.  **Buat Virtual Environment (Opsional tapi Disarankan):**
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    Pastikan file `requirements.txt` ada, lalu jalankan:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Jalankan Aplikasi:**
    ```bash
    python app.py
    ```

5.  **Akses Website:**
    Buka browser dan kunjungi `http://127.0.0.1:5000/`.

---

## 📂 Struktur Proyek

```text
Terrain-Theory-Ontology/
├── knowledge/
│   ├── inference.py        # Logika sistem pakar (aturan waktu & filter makanan)
│   └── ontology_loader.py  # Membaca file .ttl menggunakan RDFLib
├── static/
│   ├── css/
│   │   └── style.css       # Styling tampilan (Clean Theme)
│   └── js/
│       └── main.js         # Logika frontend (Cascading Dropdown)
├── templates/
│   ├── base.html           # Layout dasar HTML
│   ├── diagnose.html       # Halaman form konsultasi
│   ├── index.html          # Halaman beranda
│   └── result.html         # Halaman hasil rekomendasi
├── app.py                  # Server Flask utama
├── requirements.txt        # Daftar pustaka Python
├── Terrain.ttl             # File Knowledge Base (Ontologi)
└── vercel.json             # Konfigurasi deployment Vercel

## 👥 Authors
Program Studi Sains Data Fakultas Teknologi Informasi dan Sains Data Universitas Sebelas Maret

- Emeralita Wistyaka Rani 📧 emeralita@student.uns.ac.id

- Veenda Putri Divo 📧 veenda@student.uns.ac.id