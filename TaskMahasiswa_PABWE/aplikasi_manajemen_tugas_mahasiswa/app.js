/* TaskMahasiswa - proyek pembelajaran PABWE.
   Penyimpanan menggunakan localStorage pada browser pengguna. */
const STORAGE_KEY = "taskmahasiswa.tasks.v1";
const form = document.querySelector("#taskForm");
const taskName = document.querySelector("#taskName");
const course = document.querySelector("#course");
const dueDate = document.querySelector("#dueDate");
const priority = document.querySelector("#priority");
const notes = document.querySelector("#notes");
const taskList = document.querySelector("#taskList");
const emptyState = document.querySelector("#emptyState");
const searchInput = document.querySelector("#searchInput");
const filterStatus = document.querySelector("#filterStatus");
const sortBy = document.querySelector("#sortBy");
const toast = document.querySelector("#toast");
const dialog = document.querySelector("#deleteDialog");
let tasks = loadTasks();
let editingId = null;
let deletingId = null;
let toastTimer;

function loadTasks() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
    return Array.isArray(saved) ? saved.filter(isValidTask) : [];
  } catch (error) {
    console.error("Data tugas tidak dapat dibaca:", error);
    return [];
  }
}
function isValidTask(task) {
  return task && typeof task.id === "string" && typeof task.title === "string" &&
    typeof task.course === "string" && typeof task.dueDate === "string" &&
    typeof task.priority === "string" && typeof task.completed === "boolean";
}
function saveTasks() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
    return true;
  } catch (error) {
    console.error("Data tugas tidak dapat disimpan:", error);
    showToast("Penyimpanan gagal. Periksa ruang penyimpanan browser.");
    return false;
  }
}
function createId() {
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 9)}`;
}
function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, character => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[character]);
}
function formatDate(dateString) {
  const date = new Date(`${dateString}T00:00:00`);
  if (Number.isNaN(date.getTime())) return dateString;
  return new Intl.DateTimeFormat("id-ID", { day: "numeric", month: "short", year: "numeric" }).format(date);
}
function isOverdue(task) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return !task.completed && new Date(`${task.dueDate}T00:00:00`) < today;
}
function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 2600);
}
function renderStats() {
  document.querySelector("#totalCount").textContent = tasks.length;
  document.querySelector("#pendingCount").textContent = tasks.filter(task => !task.completed).length;
  document.querySelector("#doneCount").textContent = tasks.filter(task => task.completed).length;
}
function getVisibleTasks() {
  const query = searchInput.value.trim().toLocaleLowerCase("id-ID");
  let visible = tasks.filter(task => {
    const matchesSearch = `${task.title} ${task.course} ${task.notes || ""}`.toLocaleLowerCase("id-ID").includes(query);
    const matchesStatus = filterStatus.value === "Semua" ||
      (filterStatus.value === "Selesai" ? task.completed : !task.completed);
    return matchesSearch && matchesStatus;
  });
  if (sortBy.value === "due") visible.sort((a, b) => a.dueDate.localeCompare(b.dueDate));
  if (sortBy.value === "priority") {
    const rank = { Tinggi: 0, Sedang: 1, Rendah: 2 };
    visible.sort((a, b) => rank[a.priority] - rank[b.priority] || a.dueDate.localeCompare(b.dueDate));
  }
  if (sortBy.value === "newest") visible.sort((a, b) => b.createdAt - a.createdAt);
  return visible;
}
function renderTasks() {
  const visible = getVisibleTasks();
  taskList.innerHTML = visible.map(task => {
    const statusText = task.completed ? "Selesai" : (isOverdue(task) ? "Terlambat" : `Tenggat ${formatDate(task.dueDate)}`);
    const statusClass = isOverdue(task) ? "overdue" : "";
    return `<article class="task-card ${task.completed ? "completed" : ""}" data-id="${escapeHTML(task.id)}">
      <button class="check-button" data-action="toggle" aria-label="${task.completed ? "Tandai belum selesai" : "Tandai selesai"}" title="${task.completed ? "Tandai belum selesai" : "Tandai selesai"}">${task.completed ? "✓" : ""}</button>
      <div class="task-main">
        <p class="task-title">${escapeHTML(task.title)}</p>
        <p class="task-course">${escapeHTML(task.course)}</p>
        <div class="task-meta"><span class="pill priority-${escapeHTML(task.priority)}">${escapeHTML(task.priority)}</span><span class="${statusClass}">${statusText}</span></div>
        ${task.notes ? `<p class="task-notes">${escapeHTML(task.notes)}</p>` : ""}
      </div>
      <div class="task-actions"><button class="icon-button" data-action="edit" aria-label="Edit tugas" title="Edit">✎</button><button class="icon-button" data-action="delete" aria-label="Hapus tugas" title="Hapus">×</button></div>
    </article>`;
  }).join("");
  emptyState.classList.toggle("hidden", visible.length > 0);
  taskList.classList.toggle("hidden", visible.length === 0);
  document.querySelector("#visibleCount").textContent = `${visible.length} tugas`;
  renderStats();
}
function resetForm() {
  form.reset();
  editingId = null;
  document.querySelector("#formTitle").textContent = "Tambah tugas";
  document.querySelector("#submitButton").textContent = "＋ Simpan tugas";
  document.querySelector("#cancelEdit").classList.add("hidden");
  dueDate.value = "";
}
form.addEventListener("submit", event => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const data = {
    title: taskName.value.trim(),
    course: course.value.trim(),
    dueDate: dueDate.value,
    priority: priority.value,
    notes: notes.value.trim()
  };
  if (!data.title || !data.course || !data.dueDate) {
    showToast("Lengkapi nama tugas, mata kuliah, dan tenggat waktu.");
    return;
  }
  if (editingId) {
    tasks = tasks.map(task => task.id === editingId ? { ...task, ...data } : task);
    showToast("Perubahan tugas berhasil disimpan.");
  } else {
    tasks.push({ id: createId(), ...data, completed: false, createdAt: Date.now() });
    showToast("Tugas baru berhasil ditambahkan.");
  }
  saveTasks();
  resetForm();
  renderTasks();
});
taskList.addEventListener("click", event => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const card = button.closest(".task-card");
  const task = tasks.find(item => item.id === card?.dataset.id);
  if (!task) return;
  const action = button.dataset.action;
  if (action === "toggle") {
    task.completed = !task.completed;
    saveTasks();
    renderTasks();
    showToast(task.completed ? "Tugas ditandai selesai." : "Tugas dikembalikan ke daftar aktif.");
  }
  if (action === "edit") {
    editingId = task.id;
    taskName.value = task.title;
    course.value = task.course;
    dueDate.value = task.dueDate;
    priority.value = task.priority;
    notes.value = task.notes || "";
    document.querySelector("#formTitle").textContent = "Edit tugas";
    document.querySelector("#submitButton").textContent = "Simpan perubahan";
    document.querySelector("#cancelEdit").classList.remove("hidden");
    document.querySelector("#taskName").focus();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
  if (action === "delete") {
    deletingId = task.id;
    if (typeof dialog.showModal === "function") dialog.showModal();
    else if (window.confirm("Hapus tugas ini?")) deleteTask();
  }
});
function deleteTask() {
  if (!deletingId) return;
  tasks = tasks.filter(task => task.id !== deletingId);
  deletingId = null;
  saveTasks();
  renderTasks();
  showToast("Tugas berhasil dihapus.");
}
document.querySelector("#confirmDelete").addEventListener("click", event => {
  event.preventDefault();
  deleteTask();
  dialog.close();
});
document.querySelector("#cancelEdit").addEventListener("click", () => {
  resetForm();
  showToast("Edit dibatalkan.");
});
searchInput.addEventListener("input", renderTasks);
filterStatus.addEventListener("change", renderTasks);
sortBy.addEventListener("change", renderTasks);
renderTasks();
