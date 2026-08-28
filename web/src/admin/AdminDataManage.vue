<script setup>
import { ref, onMounted, computed } from "vue";
import { Edit, Delete, Search, Plus, RefreshCw } from "lucide-vue-next";

const programs = ref([]);
const total = ref(0);
const page = ref(0);
const pageSize = 15;
const loading = ref(false);
const filters = ref({ keyword: "", province: "", majorCode: "" });
const editing = ref(null);
const form = ref({});
const showForm = ref(false);
const saving = ref(false);
const msg = ref("");
const allProvinces = ref([]);
const allMajors = ref([]);

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)));

async function load() {
  loading.value = true;
  try {
    const params = new URLSearchParams({ page: page.value, pageSize, sort: "admissionYear,desc" });
    Object.entries(filters.value).forEach(([k, v]) => v && params.set(k, v));
    const res = await fetch(`/api/v1/programs?${params}`);
    if (res.ok) {
      const body = await res.json();
      programs.value = body.items;
      total.value = body.total;
    }
  } finally {
    loading.value = false;
  }
}

function loadFilterData() {
  fetch("/api/v1/provinces").then(r => r.json()).then(d => allProvinces.value = d).catch(() => {});
  fetch("/api/v1/majors").then(r => r.json()).then(d => allMajors.value = d).catch(() => {});
}

function search() { page.value = 0; load(); }

function openCreate() {
  editing.value = null;
  form.value = { universityName: "", province: "", majorCode: "", majorName: "", degreeType: "专业学位", studyMode: "FULL_TIME", examSubjects: "", admissionYear: new Date().getFullYear(), universityLevel: "" };
  showForm.value = true;
}

function openEdit(p) {
  editing.value = p.id;
  form.value = { ...p };
  showForm.value = true;
}

async function save() {
  saving.value = true;
  msg.value = "";
  try {
    const method = editing.value ? "PUT" : "POST";
    const url = editing.value ? `/api/v1/admin/programs/${editing.value}` : "/api/v1/admin/programs";
    const res = await fetch(url, { method, headers: { "Content-Type": "application/json" }, body: JSON.stringify(form.value) });
    if (res.ok) {
      msg.value = editing.value ? "更新成功" : "创建成功";
      showForm.value = false;
      load();
    } else {
      const e = await res.json();
      msg.value = e.message || "操作失败";
    }
  } finally {
    saving.value = false;
  }
}

async function remove(id) {
  if (!confirm("确认删除该记录？")) return;
  const res = await fetch(`/api/v1/admin/programs/${id}`, { method: "DELETE" });
  if (res.ok) { msg.value = "删除成功"; load(); }
}

onMounted(() => { load(); loadFilterData(); });
</script>

<template>
  <div class="admin-data">
    <div class="section-header">
      <h2>招生数据管理 <small>{{ total }} 条</small></h2>
      <div class="header-actions">
        <button class="primary" @click="openCreate"><Plus :size="16"/> 新增</button>
        <button class="plain" @click="load"><RefreshCw :size="16"/> 刷新</button>
      </div>
    </div>
    <p v-if="msg" class="msg">{{ msg }}</p>
    <form class="filters" @submit.prevent="search">
      <label><Search :size="14"/><input v-model="filters.keyword" placeholder="搜索院校/专业"/></label>
      <select v-model="filters.province"><option value="">全部省份</option><option v-for="p in allProvinces" :key="p" :value="p">{{ p }}</option></select>
      <select v-model="filters.majorCode"><option value="">全部专业</option><option v-for="m in allMajors" :key="m.code" :value="m.code">{{ m.code }} {{ m.name }}</option></select>
      <button class="primary" type="submit">查询</button>
    </form>
    <div class="table-wrap">
      <table>
        <thead><tr><th>ID</th><th>院校</th><th>省份</th><th>专业</th><th>年份</th><th>复试线</th><th>录取</th><th>报名</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="p in programs" :key="p.id">
            <td>{{ p.id }}</td>
            <td><b>{{ p.universityName }}</b></td>
            <td>{{ p.province }}</td>
            <td>{{ p.majorCode }} {{ p.majorName }}</td>
            <td>{{ p.admissionYear }}</td>
            <td>{{ p.reexaminationLine ?? '未公开' }}</td>
            <td>{{ p.actualEnrollment ?? '-' }}</td>
            <td>{{ p.registrationCount ?? '未公开' }}</td>
            <td class="actions">
              <button class="icon" @click="openEdit(p)"><Edit :size="15"/></button>
              <button class="icon danger" @click="remove(p.id)"><Delete :size="15"/></button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="pager">
      <button :disabled="page===0" @click="page--;load()">上一页</button>
      <span>第 {{ page+1 }} / {{ totalPages }} 页</span>
      <button :disabled="page+1>=totalPages" @click="page++;load()">下一页</button>
    </div>
    <div v-if="showForm" class="modal-mask" @click.self="showForm=false">
      <div class="modal">
        <h3>{{ editing ? '编辑' : '新增' }}招生数据</h3>
        <div class="form-grid">
          <label>院校名称<input v-model="form.universityName" required/></label>
          <label>省份<input v-model="form.province" required/></label>
          <label>专业代码<input v-model="form.majorCode" required/></label>
          <label>专业名称<input v-model="form.majorName" required/></label>
          <label>学位类型<select v-model="form.degreeType"><option>学术学位</option><option>专业学位</option></select></label>
          <label>培养方式<select v-model="form.studyMode"><option value="FULL_TIME">全日制</option><option value="PART_TIME">非全日制</option></select></label>
          <label>考试科目<input v-model="form.examSubjects"/></label>
          <label>年度<input v-model.number="form.admissionYear" type="number"/></label>
          <label>院校层次<input v-model="form.universityLevel"/></label>
          <label>复试线<input v-model.number="form.reexaminationLine" type="number"/></label>
          <label>计划招生<input v-model.number="form.plannedEnrollment" type="number"/></label>
          <label>实际录取<input v-model.number="form.actualEnrollment" type="number"/></label>
          <label>报名人数<input v-model.number="form.registrationCount" type="number"/></label>
          <label>国家线<input v-model.number="form.nationalLine" type="number"/></label>
        </div>
        <div class="modal-actions">
          <button class="plain" @click="showForm=false">取消</button>
          <button class="primary" :disabled="saving" @click="save">{{ saving ? '保存中...' : '保存' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>
