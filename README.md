# Terrain Theory Ontology
Repositori yang dibuat untuk memenuhi mata kuliah Knowledge Base and Reasoning.

### Member of this project group:
- Emeralita Wistyaka Rani
- Veenda Putri Divo

# Tutorial Connect Protégé ke GitHub
## Tahap 1: Persiapan
1. **Instal GitHub Desktop**: Unduh dan instal aplikasi [GitHub Desktop](https://github.com/apps/desktop). Login dengan akun GitHub Anda.
2. **Buat Repository (Di Website GitHub)**:
   - Buka GitHub.com, buat Repository baru (misal: `Terrain-Ontology-Project`).
   - Set ke Private (jika ingin rahasia) atau Public.
   - *Penting*: Centang "Add a README file" agar repository langsung siap dipakai.
3. **Clone ke Laptop (Lewat GitHub Desktop)**:
   - Buka GitHub Desktop.
   - Pilih menu `File` > `Clone Repository`.
   - Pilih repository `Terrain-Ontology-Project` tadi.
   - Pilih folder tujuan di laptop Anda (Misal: `D:\Documents\Terrain-Project`).
Sekarang, folder `D:\Documents\Terrain-Project` di laptop Anda adalah "Pintu Ajaib" yang terhubung langsung ke GitHub.

## Tahap 2: Cara Menyimpan dari Protégé (Workflow Harian)
Ini yang harus Anda dan partner lakukan setiap kali bekerja:
1. Buka **Protégé**.
2. Saat pertama kali menyimpan (`File` > `Save As`), arahkan penyimpanannya **MASUK** ke dalam folder hasil clone tadi (`D:\Documents\Terrain-Project`).
3. **SANGAT PENTING**: Pilih format penyimpanan **Turtle Syntax (.ttl)**.
   - *Kenapa?* Format default Protégé (RDF/XML) sangat berantakan jika dilihat di GitHub. Format Turtle (.ttl) lebih rapi, baris per baris, sehingga GitHub bisa mendeteksi perubahan dengan mudah.

## tahap 3: Mengirim ke GitHub (Push)
Setelah Anda selesai mengedit di Protégé dan menekan tombol Save (Ctrl+S):
1. Buka aplikasi **GitHub Desktop**.
2. Anda akan melihat daftar perubahan file (misal: *GraphDB akan mendeteksi ada baris baru tentang "Electric Foods"*).
3. Di kotak kiri bawah (Summary), tulis catatan singkat, misal: *"Menambahkan Class ElectricFoods dan MucuslessFoods"*.
4. Klik tombol biru **Commit to main**.
5. Klik tombol **Push origin** di bagian atas.
Selesai! File ontologi Anda sekarang aman di awan (GitHub).

## Tahap 4: Cara Partner Mengambil Data (Pull)
Ketika partner Anda ingin mulai bekerja melanjutkan tugas Anda:
1. Partner membuka **GitHub Desktop** di laptopnya.
2. Klik tombol **Fetch origin** lalu **Pull origin**.
3. File `.ttl` di folder laptop partner akan otomatis berubah menjadi versi terbaru yang Anda buat.
4. Partner membuka file tersebut di Protégé, mengedit, lalu melakukan **Commit** dan **Push** lagi seperti Tahap 3.

## Tips Penting Mencegah Konflik (Wajib Baca)
Karena file ontologi adalah file teks, jika Anda dan partner mengedit baris yang sama di waktu yang bersamaan, akan terjadi Conflict (GitHub bingung mau pakai versi siapa).
**Aturan Emas**:
1. **Komunikasi**: Sebelum mulai kerja, bilang di grup chat: "*Saya lagi edit bagian Class Makanan ya.*" Partner sebaiknya mengerjakan bagian lain (misal: *Class Penyakit*).
2. **Pull Dulu**: Sebelum buka Protégé, biasakan selalu klik *Pull* di GitHub Desktop untuk memastikan Anda mengedit di atas versi terbaru.
