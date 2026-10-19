"""Pengujian otomatis TaskMahasiswa (Playwright + Chromium).
Pemakaian: python3 test_app.py <folder_aplikasi> [folder_screenshot]
"""
import sys, json, pathlib
from playwright.sync_api import sync_playwright

APP = pathlib.Path(sys.argv[1]).resolve()
SHOTS = pathlib.Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else None
if SHOTS: SHOTS.mkdir(parents=True, exist_ok=True)
URL = APP.joinpath("index.html").as_uri()
KEY = "taskmahasiswa.tasks.v1"
results = []

def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("PASS" if cond else "FAIL"), "-", name, ("| " + str(detail)) if detail and not cond else "")

def add(page, title, course, due, prio="Sedang", notes=""):
    page.fill("#taskName", title); page.fill("#course", course)
    page.fill("#dueDate", due); page.select_option("#priority", prio)
    page.fill("#notes", notes); page.click("#submitButton")

def titles(page):
    return page.locator(".task-title").all_inner_texts()

def stats(page):
    return [page.inner_text(f"#{i}") for i in ("totalCount", "pendingCount", "doneCount")]

with sync_playwright() as p:
    browser = p.chromium.launch()
    ctx = browser.new_context(viewport={"width": 1280, "height": 900})
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("dialog", lambda d: d.accept())
    page.goto(URL)

    # Keadaan kosong awal
    check("Awal: keadaan kosong tampil", page.is_visible("#emptyState") and stats(page) == ["0", "0", "0"])
    if SHOTS: page.screenshot(path=str(SHOTS / "01-kosong-desktop.png"), full_page=True)

    # 1. Tambah tugas
    add(page, "Laporan PABWE", "PABWE", "2030-05-10", "Tinggi", "Bab 1-3")
    add(page, "Kuis Basis Data", "Basis Data", "2030-05-01", "Rendah")
    add(page, "Esai Etika", "Etika Profesi", "2030-05-20", "Sedang")
    check("1. Tambah 3 tugas -> daftar & ringkasan", len(titles(page)) == 3 and stats(page) == ["3", "3", "0"], (titles(page), stats(page)))
    if SHOTS: page.screenshot(path=str(SHOTS / "02-terisi-desktop.png"), full_page=True)

    # 2. Validasi input wajib
    page.fill("#taskName", "   "); page.fill("#course", "X"); page.fill("#dueDate", "2030-01-01")
    page.click("#submitButton")
    check("2a. Nama hanya spasi ditolak", len(titles(page)) == 3)
    page.fill("#taskName", "Ada"); page.fill("#course", ""); page.click("#submitButton")
    check("2b. Mata kuliah kosong ditolak", len(titles(page)) == 3)
    page.fill("#course", "Y"); page.fill("#dueDate", ""); page.click("#submitButton")
    check("2c. Tenggat kosong ditolak", len(titles(page)) == 3)
    page.click("#submitButton") if False else None
    page.reload()
    check("2d. Percobaan gagal tidak tersimpan", len(titles(page)) == 3)

    # 3. Edit
    page.locator(".task-card", has_text="Kuis Basis Data").locator("[data-action=edit]").click()
    check("3a. Form terisi saat edit", page.input_value("#taskName") == "Kuis Basis Data" and page.is_visible("#cancelEdit"))
    page.fill("#taskName", "Kuis SQL"); page.fill("#dueDate", "2030-06-01"); page.click("#submitButton")
    check("3b. Hasil edit tampil", "Kuis SQL" in titles(page) and "Kuis Basis Data" not in titles(page) and len(titles(page)) == 3)
    page.locator(".task-card", has_text="Kuis SQL").locator("[data-action=edit]").click()
    page.click("#cancelEdit")
    check("3c. Batal edit mengosongkan form", page.input_value("#taskName") == "" and not page.is_visible("#cancelEdit"))

    # 5. Status selesai
    page.locator(".task-card", has_text="Laporan PABWE").locator("[data-action=toggle]").click()
    check("5a. Tandai selesai -> ringkasan", stats(page) == ["3", "2", "1"], stats(page))
    page.locator(".task-card", has_text="Laporan PABWE").locator("[data-action=toggle]").click()
    check("5b. Kembalikan ke belum selesai", stats(page) == ["3", "3", "0"], stats(page))
    page.locator(".task-card", has_text="Laporan PABWE").locator("[data-action=toggle]").click()

    # 6. Cari & filter
    page.fill("#searchInput", "pabwe")
    check("6a. Cari nama/mata kuliah (case-insensitive)", titles(page) == ["Laporan PABWE"], titles(page))
    page.fill("#searchInput", "zzz")
    check("6b. Cari tanpa hasil -> pesan kosong", page.is_visible("#emptyState"))
    empty_msg = page.inner_text("#emptyState")
    check("6c. Pesan 'tidak ada hasil' berbeda dari 'belum ada tugas'", "Belum ada tugas" not in empty_msg, empty_msg)
    page.fill("#searchInput", "Bab 1")  # hanya ada di catatan
    check("6d. Pencarian hanya nama/mata kuliah (bukan catatan)", len(titles(page)) == 0, titles(page))
    page.fill("#searchInput", "")
    page.select_option("#filterStatus", "Selesai")
    check("6e. Filter Selesai", titles(page) == ["Laporan PABWE"], titles(page))
    page.select_option("#filterStatus", "Belum selesai")
    check("6f. Filter Belum selesai", sorted(titles(page)) == ["Esai Etika", "Kuis SQL"], titles(page))
    page.select_option("#filterStatus", "Semua")

    # 7. Urutkan
    page.select_option("#sortBy", "due")
    check("7a. Urut tenggat", titles(page) == ["Laporan PABWE", "Esai Etika", "Kuis SQL"], titles(page))
    page.select_option("#sortBy", "priority")
    check("7b. Urut prioritas", titles(page) == ["Laporan PABWE", "Esai Etika", "Kuis SQL"], titles(page))
    page.select_option("#sortBy", "newest")
    check("7c. Urut terbaru", titles(page)[0] == "Esai Etika", titles(page))
    page.select_option("#sortBy", "due")

    # 8. Persistensi
    page.reload()
    check("8. Data & status tetap setelah reload", len(titles(page)) == 3 and stats(page) == ["3", "2", "1"], stats(page))

    # 4. Hapus (batal lalu konfirmasi)
    card = lambda t: page.locator(".task-card", has_text=t)
    card("Esai Etika").locator("[data-action=delete]").click()
    check("4a. Dialog konfirmasi muncul", page.is_visible("#deleteDialog"))
    page.click("#deleteDialog button[value=cancel]")
    check("4b. Batal hapus -> tugas tetap", len(titles(page)) == 3)
    card("Esai Etika").locator("[data-action=delete]").click()
    page.keyboard.press("Escape")
    check("4c. Escape menutup dialog tanpa menghapus", len(titles(page)) == 3)
    card("Esai Etika").locator("[data-action=delete]").click()
    page.click("#confirmDelete")
    check("4d. Konfirmasi hapus -> tugas hilang & ringkasan", "Esai Etika" not in titles(page) and stats(page) == ["2", "1", "1"], stats(page))
    page.reload()
    check("4e. Penghapusan persisten", len(titles(page)) == 2)

    # Hapus tugas yang sedang diedit
    card("Kuis SQL").locator("[data-action=edit]").click()
    card("Kuis SQL").locator("[data-action=delete]").click()
    page.click("#confirmDelete")
    check("4f. Hapus tugas yang sedang diedit -> form keluar dari mode edit", page.inner_text("#formTitle") == "Tambah tugas", page.inner_text("#formTitle"))

    # 9. Teks tidak biasa
    page.evaluate("localStorage.clear()"); page.reload()
    xss = "<img src=x onerror=\"window.__pwned=1\"><script>window.__pwned=1</script>"
    add(page, xss, "'\"&<b>bold</b>", "2030-01-01", "Sedang", xss)
    page.wait_for_timeout(200)
    check("9a. HTML tidak dieksekusi", page.evaluate("window.__pwned") is None)
    check("9b. HTML tampil sebagai teks", "<img src=x" in page.inner_text(".task-title") and page.locator(".task-card img").count() == 0)
    long_word = "A" * 80
    add(page, "B" * 100, long_word, "2030-01-02")
    add(page, "Emoji 😀 日本語 áéí", "Kuliah ñ", "2030-01-03")
    page.reload()
    check("9c. Emoji/Unicode tersimpan", any("😀" in t for t in titles(page)))
    overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
    check("9d. Teks panjang tanpa spasi tidak membuat halaman meluap (desktop)", not overflow)

    # Data rusak di localStorage
    page.evaluate(f"localStorage.setItem('{KEY}', '{{rusak')"); page.reload()
    check("9e. JSON rusak -> aplikasi tetap jalan (kosong)", page.is_visible("#emptyState") and not errors, errors)
    bad = [
        {"id": "a", "title": "Normal", "course": "C", "dueDate": "2030-01-01", "priority": "Sedang", "completed": False, "createdAt": 1},
        {"id": "b", "title": "PrioritasAneh", "course": "C", "dueDate": "2030-01-02", "priority": "Super", "completed": False, "createdAt": 2},
        {"id": "c", "title": "TanggalAneh", "course": "C", "dueDate": "bukan-tanggal", "priority": "Tinggi", "completed": False, "createdAt": 3},
        {"id": "d", "title": "TanpaCreatedAt", "course": "C", "dueDate": "2030-01-03", "priority": "Tinggi", "completed": False},
        "sampah", None, 42,
    ]
    page.evaluate(f"localStorage.setItem('{KEY}', JSON.stringify({json.dumps(bad)}))"); page.reload()
    page.select_option("#sortBy", "priority")
    t = titles(page)
    check("9f. Record tidak valid (prioritas/tanggal aneh, sampah) disaring", not errors and sorted(t) == ["Normal", "TanpaCreatedAt"], (t, errors))
    check("9g. Urut prioritas deterministik pada data lama", t == ["TanpaCreatedAt", "Normal"], t)
    page.select_option("#sortBy", "newest")
    check("9h. Urut terbaru tanpa createdAt tidak error", not errors and sorted(titles(page)) == ["Normal", "TanpaCreatedAt"], (titles(page), errors))

    # Gagal menyimpan: simulasikan quota penuh
    page.evaluate("localStorage.clear()"); page.reload()
    page.evaluate("(() => { const o = Storage.prototype.setItem; Storage.prototype.setItem = function(k, v){ if (k === 'taskmahasiswa.tasks.v1') throw new DOMException('quota','QuotaExceededError'); return o.call(this, k, v); }; })()")
    add(page, "Gagal simpan", "X", "2030-01-01")
    toast = page.inner_text("#toast")
    check("9i. Gagal simpan -> pesan kesalahan, bukan pesan sukses", "gagal" in toast.lower() and "berhasil" not in toast.lower(), toast)
    check("9j. Tidak ada error JS tak tertangani", not errors, errors)

    # Localstorage tidak tersedia sama sekali
    ctx2 = browser.new_context(viewport={"width": 1280, "height": 900})
    p2 = ctx2.new_page(); e2 = []
    p2.on("pageerror", lambda e: e2.append(str(e)))
    p2.add_init_script("Object.defineProperty(window,'localStorage',{get(){throw new DOMException('denied','SecurityError')}})")
    p2.goto(URL)
    add(p2, "Tanpa storage", "X", "2030-01-01")
    check("9k. localStorage diblokir -> aplikasi tetap berfungsi", not e2 and len(titles(p2)) == 1, (e2, titles(p2)))
    ctx2.close()

    # 10. Layar kecil
    m = browser.new_context(viewport={"width": 375, "height": 740}, device_scale_factor=2)
    mp = m.new_page(); me = []
    mp.on("pageerror", lambda e: me.append(str(e)))
    mp.goto(URL)
    add(mp, "Laporan Praktikum", "PABWE", "2030-05-10", "Tinggi", "Catatan singkat")
    add(mp, "B" * 90, "C" * 80, "2030-05-11", "Rendah", "N" * 120)
    ov = mp.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check("10a. Tidak ada scroll horizontal pada 375px", ov <= 0, f"selisih {ov}px")
    mp.set_viewport_size({"width": 320, "height": 640})
    ov = mp.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
    check("10b. Tidak ada scroll horizontal pada 320px", ov <= 0, f"selisih {ov}px")
    mp.set_viewport_size({"width": 375, "height": 740})
    small = mp.evaluate("""() => [...document.querySelectorAll('button, input, select, textarea')]
        .filter(e => e.offsetParent !== null).map(e => e.getBoundingClientRect())
        .filter(r => r.width < 28 || r.height < 28).length""")
    check("10c. Target sentuh >= 28px", small == 0, f"{small} elemen lebih kecil")
    check("10d. Tidak ada error JS di ponsel", not me, me)
    if SHOTS:
        mp.screenshot(path=str(SHOTS / "03-terisi-ponsel.png"), full_page=True)
    m.close()

    # Screenshot dialog & edit (desktop)
    if SHOTS:
        page.evaluate("localStorage.clear()"); page.reload()
        add(page, "Laporan Praktikum PABWE", "PABWE", "2020-01-10", "Tinggi", "Kerjakan bab 1-3.")
        page.locator(".task-card").first.locator("[data-action=edit]").click()
        page.screenshot(path=str(SHOTS / "04-edit-desktop.png"), full_page=True)
        page.click("#cancelEdit")
        page.locator(".task-card").first.locator("[data-action=delete]").click()
        page.screenshot(path=str(SHOTS / "05-dialog-hapus.png"))

    browser.close()

fails = [r for r in results if not r[1]]
print(f"\nTOTAL: {len(results)} pemeriksaan, {len(results)-len(fails)} lulus, {len(fails)} gagal")
json.dump(results, open(pathlib.Path(__file__).with_name("hasil_uji.json"), "w"), ensure_ascii=False, indent=1)
sys.exit(1 if fails else 0)
