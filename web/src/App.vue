<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { BarChart3, Bookmark, ChevronDown, ChevronLeft, ChevronRight, CheckCircle, AlertCircle, Database, ExternalLink, GraduationCap, LayoutDashboard, LogOut, MapPin, PieChart, Search, Settings, Shield, SlidersHorizontal, Sparkles, Upload, User, Users, FileText, X } from "lucide-vue-next";
import LoginPage from "./views/LoginPage.vue";
import DataCharts from "./views/DataCharts.vue";
import ComboBox from "./components/ComboBox.vue";
import AdminDashboard from "./admin/AdminDashboard.vue";
import AdminDataManage from "./admin/AdminDataManage.vue";
import AdminDataImport from "./admin/AdminDataImport.vue";
import AdminUserManage from "./admin/AdminUserManage.vue";
import AdminSystemLog from "./admin/AdminSystemLog.vue";

const apiBase = "/api/v1";
const recommendationUrl = "/recommendation/api/v1/recommendations";
const route = ref(location.hash.replace("#", "") || "/programs");
const loggedIn = ref(false);
const currentUser = ref(null);
function handleLogin(user) {
  loggedIn.value = true;
  currentUser.value = user;
  const target = user.role === "ADMIN" ? "/admin/dashboard"
    : route.value && route.value !== "/login" ? route.value : "/programs";
  go(target);
}
function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  loggedIn.value = false;
  currentUser.value = null;
  go("/programs");
}
const groupedPrograms = ref([]); const totalGroups = ref(0); const loading = ref(false); const apiError = ref(false); const recommendError = ref("");
const selectedPrograms = ref(JSON.parse(localStorage.getItem("shortlist") || "[]"));
const recommendations = ref([]); const isRecommending = ref(false); const page = ref(0);
const filters = ref({ keyword: "", province: "", majorCode: "", examKeyword: "", studyMode: "" });
const profile = ref({ targetMajor: "", estimatedScore: 340, preferredProvinces: "江苏,浙江", riskPreference: "BALANCED" });
const weights = ref({ score: 45, competition: 20, region: 15, major: 15 });
const pageSize = 10;

// 动态加载省份和专业
const allProvinces = ref([]);
const allMajors = ref([]);
const majorCategories = ref([]);
const selectedMajorCategory = ref("");
const filteredMajors = ref([]);
const allExamSubjects = ref([]);

async function loadFilterData() {
  try {
    const [provRes, majRes, examRes] = await Promise.all([
      fetch(`${apiBase}/provinces`),
      fetch(`${apiBase}/majors`),
      fetch(`${apiBase}/exam-subjects`)
    ]);
    if (provRes.ok) allProvinces.value = await provRes.json();
    if (majRes.ok) {
      allMajors.value = await majRes.json();
      const cats = {};
      allMajors.value.forEach(m => {
        const prefix = m.code.substring(0, 2);
        if (!cats[prefix]) cats[prefix] = { code: prefix, name: getMajorCategoryName(prefix), children: [] };
        cats[prefix].children.push(m);
      });
      majorCategories.value = Object.values(cats).sort((a, b) => a.code.localeCompare(b.code));
    }
    if (examRes.ok) allExamSubjects.value = await examRes.json();
  } catch (e) { console.error("Load filter data error:", e); }
}

function getMajorCategoryName(code) {
  const map = {"01":"哲学","02":"经济学","03":"法学","04":"教育学","05":"文学","06":"历史学","07":"理学","08":"工学","09":"农学","10":"医学","11":"军事学","12":"管理学","13":"艺术学","14":"交叉学科"};
  return map[code] || code;
}

function onMajorCategoryChange() {
  const cat = selectedMajorCategory.value;
  if (cat) {
    const found = majorCategories.value.find(c => c.code === cat);
    filteredMajors.value = found ? found.children : [];
  } else {
    filteredMajors.value = [];
  }
  filters.value.majorCode = "";
}
const selectedProvinces = ref(profile.value.preferredProvinces.split(",").filter(Boolean));
watch(selectedProvinces, (v) => { profile.value.preferredProvinces = v.join(","); });
const provinceSearch = ref("");
const provinceDropdownOpen = ref(false);
const filteredProvinces = computed(() => {
  const q = provinceSearch.value.trim().toLowerCase();
  return allProvinces.value.filter(p => !selectedProvinces.value.includes(p) && ( !q || p.includes(q) ));
});
function addProvince(p) {
  if (!selectedProvinces.value.includes(p)) selectedProvinces.value.push(p);
  provinceSearch.value = "";
}
function removeProvince(p) {
  selectedProvinces.value = selectedProvinces.value.filter(x => x !== p);
}
function onProvinceInput() {
  provinceDropdownOpen.value = true;
}
function onProvinceKeydown(e) {
  if (e.key === "Enter" && provinceSearch.value.trim()) {
    e.preventDefault();
    const v = provinceSearch.value.trim();
    if (allProvinces.value.includes(v) && !selectedProvinces.value.includes(v)) {
      selectedProvinces.value.push(v);
    }
    provinceSearch.value = "";
  }
  if (e.key === "Backspace" && !provinceSearch.value && selectedProvinces.value.length) {
    selectedProvinces.value.pop();
  }
}
const apiTestUrl = ref("/api/v1/programs");
const apiTestMethod = ref("GET");
const apiTestBody = ref('{ "page": 0, "pageSize": 5 }');
const apiTestResult = ref(null);
const apiTestLoading = ref(false);
const expandedGroups = ref({});

async function runApiTest() {
  apiTestLoading.value = true;
  apiTestResult.value = null;
  try {
    const opts = { method: apiTestMethod.value, headers: { "Content-Type": "application/json" } };
    if (apiTestMethod.value === "POST" || apiTestMethod.value === "PUT") opts.body = apiTestBody.value;
    const res = await fetch(apiTestUrl.value, opts);
    const text = await res.text();
    apiTestResult.value = { status: res.status, statusText: res.statusText, body: text };
  } catch (e) {
    apiTestResult.value = { status: 0, statusText: "Error", body: e.message };
  } finally {
    apiTestLoading.value = false;
  }
}
const userNav = [{ path: "/programs", label: "院校专业检索", icon: Search }, { path: "/compare", label: "对比清单", icon: BarChart3 }, { path: "/recommend", label: "择校建议", icon: Sparkles }, { path: "/charts", label: "数据可视化", icon: PieChart }, { path: "/user/profile", label: "个人中心", icon: User }];
const adminNav = [{ path: "/admin/dashboard", label: "系统概览", icon: LayoutDashboard }, { path: "/admin/data", label: "数据管理", icon: Database }, { path: "/admin/import", label: "数据导入", icon: Upload }, { path: "/admin/users", label: "用户管理", icon: Users }, { path: "/admin/logs", label: "系统日志", icon: FileText }];
const testNav = [{ path: "/programs", label: "院校专业检索", icon: Search }, { path: "/compare", label: "对比清单", icon: BarChart3 }, { path: "/test/api", label: "API调试", icon: FileText }, { path: "/charts", label: "数据可视化", icon: PieChart }, { path: "/user/profile", label: "个人中心", icon: User }];
const nav = computed(() => { const r = currentUser.value?.role; if (r === "ADMIN") return adminNav; if (r === "TEST") return testNav; return userNav; });
const isAdmin = computed(() => currentUser.value?.role === "ADMIN");
const isTest = computed(() => currentUser.value?.role === "TEST");
const totalPages = computed(() => Math.max(1, Math.ceil(totalGroups.value / pageSize)));
const candidatePrograms = computed(() => {
  if (selectedPrograms.value.length) return selectedPrograms.value;
  const flat = [];
  groupedPrograms.value.forEach(g => {
    g.years.forEach(y => {
      flat.push({ id: g.universityName + "~" + g.majorCode + "~" + y.year, universityName: g.universityName, majorCode: g.majorCode, majorName: g.majorName, province: g.province, admissionYear: y.year, reexaminationLine: y.reexLine, actualEnrollment: y.actual, registrationCount: y.reg, nationalLine: y.national, sourceName: y.source });
    });
  });
  return flat;
});

function toggleGroup(key) {
  expandedGroups.value[key] = !expandedGroups.value[key];
}
function isExpanded(key) { return !!expandedGroups.value[key]; }

function go(path) { location.hash = path; }
window.addEventListener("hashchange", () => { route.value = location.hash.replace("#", "") || "/programs"; });
watch(selectedPrograms, value => localStorage.setItem("shortlist", JSON.stringify(value)), { deep: true });
function ratio(p) { return p.registrationCount && p.actualEnrollment ? `${(p.registrationCount / p.actualEnrollment).toFixed(1)} : 1` : "未公开"; }
function sourceTime(p) { return p.collectedAt ? new Date(p.collectedAt).toLocaleDateString("zh-CN") : "未记录"; }
function progKey(p) { return (p.universityName || "") + "~" + (p.majorCode || "") + "~" + (p.admissionYear || p.year || ""); }
function selected(p) { return selectedPrograms.value.some(item => progKey(item) === progKey(p)); }
function toggle(p) { const key = progKey(p); const i = selectedPrograms.value.findIndex(item => progKey(item) === key); if (i >= 0) selectedPrograms.value.splice(i, 1); else if (selectedPrograms.value.length < 5) selectedPrograms.value.push({ id: key, universityName: p.universityName, majorCode: p.majorCode, majorName: p.majorName, province: p.province, admissionYear: p.admissionYear || p.year, reexaminationLine: p.reexaminationLine || p.reexLine, actualEnrollment: p.actualEnrollment || p.actual, registrationCount: p.registrationCount || p.reg, nationalLine: p.nationalLine || p.national, sourceName: p.sourceName || p.source }); }
function clearFilters() { filters.value = { keyword: "", province: "", majorCode: "", examKeyword: "", studyMode: "" }; selectedMajorCategory.value = ""; filteredMajors.value = []; page.value = 0; loadPrograms(); }
async function loadPrograms() { loading.value = true; apiError.value = false; try { const params = new URLSearchParams({ page: page.value, pageSize }); Object.entries(filters.value).forEach(([k,v]) => v && params.set(k,v)); const res = await fetch(`${apiBase}/programs/groups?${params}`); if (!res.ok) throw new Error(); const body = await res.json(); groupedPrograms.value = body.items; totalGroups.value = body.total; } catch { apiError.value = true; groupedPrograms.value = []; totalGroups.value = 0; } finally { loading.value = false; } }
function submitSearch() { page.value = 0; loadPrograms(); }
async function getRecommendations() { if (!candidatePrograms.value.length) return; isRecommending.value = true; recommendError.value = ""; const requestProfile = { estimated_score: profile.value.estimatedScore, target_major: profile.value.targetMajor, preferred_provinces: profile.value.preferredProvinces.split(",").map(x => x.trim()).filter(Boolean), risk_preference: profile.value.riskPreference }; const requestPrograms = candidatePrograms.value.map(p => ({ id:p.id || progKey(p), university_name:p.universityName, major_code:p.majorCode, major_name:p.majorName, province:p.province, reexamination_line:p.reexaminationLine, national_line:p.nationalLine, actual_enrollment:p.actualEnrollment, registration_count:p.registrationCount, admission_year:p.admissionYear, source_name:p.sourceName })); try { const res = await fetch(recommendationUrl, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({profile:requestProfile, programs:requestPrograms, weights:weights.value}) }); if (!res.ok) throw new Error("服务返回错误 " + res.status); const body = await res.json(); recommendations.value = body.items || []; } catch(e) { recommendError.value = "推荐服务不可用：" + e.message; recommendations.value = []; } finally { isRecommending.value = false; } }
function openRecommend() { go("/recommend"); }

onMounted(() => {
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".province-combo")) provinceDropdownOpen.value = false;
  });
  const saved = localStorage.getItem("user");
  if (saved) { try { currentUser.value = JSON.parse(saved); loggedIn.value = true; } catch {} }
  loadPrograms();
  loadFilterData();
});
</script>

<template>
  <LoginPage v-if="!loggedIn" @login="handleLogin"/>
  <main v-else class="app-shell">
    <header class="app-header">
      <button class="brand" @click="go('/programs')"><GraduationCap :size="22"/> 计算机考研择校</button>
      <nav><button v-for="item in nav" :key="item.path" :class="{ active: route === item.path }" @click="go(item.path)"><component :is="item.icon" :size="17"/>{{ item.label }}</button></nav>
      <div class="header-right">
        <span class="user-info"><User :size="14"/> {{ currentUser?.username }} <small v-if="isAdmin" style="color:#e6a23c">(管理员)</small><small v-else-if="isTest" style="color:#909399">(测试)</small></span>
        <button class="logout-btn" @click="logout"><LogOut :size="15"/> 退出</button>
      </div>
    </header>

    <!-- ========== 用户端 ========== -->
    <section v-if="route === '/programs'" class="page-wrap">
      <div class="page-title"><div><p>PROGRAM DIRECTORY</p><h1>院校专业检索</h1><span>按高校+专业分组展示，点击展开查看各年份数据。</span></div><button class="primary" @click="openRecommend"><Sparkles :size="17"/>生成择校建议</button></div>
      <form class="filters" @submit.prevent="submitSearch"><label class="wide"><Search :size="16"/><input v-model="filters.keyword" placeholder="院校名称、专业名称、专业代码"/></label><label><MapPin :size="16"/><select v-model="filters.province"><option value="">全部省份</option><option v-for="p in allProvinces" :key="p" :value="p">{{ p }}</option></select></label><label><ComboBox v-model="selectedMajorCategory" :options="majorCategories.map(c => ({label: c.code+' '+c.name, value: c.code}))" placeholder="全部学科门类" @select="onMajorCategoryChange"/></label><label v-if="filteredMajors.length"><ComboBox v-model="filters.majorCode" :options="filteredMajors.map(m => ({label: m.code+' '+m.name, value: m.code}))" placeholder="该门类全部专业"/></label><label><SlidersHorizontal :size="16"/><ComboBox v-model="filters.examKeyword" :options="allExamSubjects" placeholder="全部考试科目"/></label><button class="primary" :disabled="loading">{{ loading ? '检索中' : '检索' }}</button><button type="button" class="plain" @click="clearFilters">清空</button></form>
      <p v-if="apiError" class="notice">业务服务不可用。</p><p class="result-meta">{{ totalGroups }} 个高校专业组 · 第 {{ page + 1 }} / {{ totalPages }} 页（每页 {{ pageSize }} 组）</p>
      <div class="grouped-programs">
        <article v-for="g in groupedPrograms" :key="g.universityName + '~' + g.majorCode" class="group-card">
          <div class="group-header" @click="toggleGroup(g.universityName + '~' + g.majorCode)">
            <div class="group-info">
              <div class="group-left">
                <span class="group-code">{{ g.majorCode }}</span>
                <div>
                  <h2>{{ g.universityName }}</h2>
                  <p class="group-major">{{ g.majorName }} · {{ g.province }} · {{ g.level || '双非' }}</p>
                </div>
              </div>
              <div class="group-right">
                <span class="group-years">{{ g.years.length }}年数据</span>
                <span class="group-latest">{{ g.years[0]?.year || '' }}</span>
                <ChevronDown :size="18" :class="{ rotated: isExpanded(g.universityName + '~' + g.majorCode) }"/>
              </div>
            </div>
          </div>
          <div v-if="isExpanded(g.universityName + '~' + g.majorCode)" class="group-body">
            <p class="group-subjects" v-if="g.examSubjects && g.examSubjects !== '未公开'">考试科目：{{ g.examSubjects }}</p>
            <div class="year-table">
              <table>
                <thead><tr><th>年份</th><th>复试线</th><th>国家线</th><th>计划招生</th><th>录取</th><th>报名</th><th>报录比</th></tr></thead>
                <tbody>
                  <tr v-for="y in g.years" :key="y.year">
                    <td><b>{{ y.year }}</b></td>
                    <td :class="y.reexLine ? 'has-data' : ''">{{ y.reexLine ?? '-' }}</td>
                    <td :class="y.national ? 'has-data' : ''">{{ y.national ?? '-' }}</td>
                    <td :class="y.planned ? 'has-data' : ''">{{ y.planned ?? '-' }}</td>
                    <td :class="y.actual ? 'has-data' : ''">{{ y.actual ?? '-' }}</td>
                    <td>{{ y.reg ?? '-' }}</td>
                    <td>{{ y.reg && y.actual ? (y.reg / y.actual).toFixed(1) + ':1' : '-' }}</td>
                    <td><button class="icon" :class="{ 'selected-check': selected({...y, universityName: g.universityName, majorCode: g.majorCode, majorName: g.majorName}) }" @click.prevent="toggle({...y, universityName: g.universityName, majorCode: g.majorCode, majorName: g.majorName, province: g.province})" :title="selected({...y, universityName: g.universityName, majorCode: g.majorCode}) ? '移出对比' : '加入对比'"><Bookmark :size="15"/></button></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </article>
      </div>
      <div class="pager"><button class="icon" :disabled="page === 0" @click="page--; loadPrograms()"><ChevronLeft :size="17"/></button><span>第 {{ page + 1 }} / {{ totalPages }} 页</span><button class="icon" :disabled="page + 1 >= totalPages" @click="page++; loadPrograms()"><ChevronRight :size="17"/></button></div>
    </section>

    <section v-else-if="route === '/compare'" class="page-wrap">
      <div class="page-title"><div><p>SHORTLIST</p><h1>对比清单 <em>{{ selectedPrograms.length }} / 5</em></h1></div><button class="plain" @click="selectedPrograms = []">清空清单</button></div>
      <div v-if="!selectedPrograms.length" class="empty"><Bookmark :size="25"/>从检索页加入不超过 5 个项目。</div>
      <div v-else class="comparison"><table><thead><tr><th>院校专业</th><th>年份</th><th>复试线</th><th>计划</th><th>报录比</th><th>来源</th><th></th></tr></thead><tbody><tr v-for="p in selectedPrograms" :key="progKey(p)"><td><b>{{ p.universityName }}</b><span>{{ p.majorCode }} · {{ p.majorName }}</span></td><td>{{ p.admissionYear }}</td><td>{{ p.reexaminationLine ?? '未公开' }}</td><td>{{ p.plannedEnrollment ?? '未公开' }}</td><td>{{ ratio(p) }}</td><td>{{ p.sourceName }}</td><td><button class="icon" @click="toggle(p)"><X :size="16"/></button></td></tr></tbody></table></div>
    </section>

    <DataCharts v-else-if="route === '/charts'" />

    <section v-else-if="route === '/recommend'" class="page-wrap recommendation">
      <div class="page-title"><div><p>DECISION SUPPORT</p><h1>择校建议</h1><span>模型会解释评分组成，但不构成录取承诺。</span></div><button class="primary" :disabled="isRecommending" @click="getRecommendations"><Sparkles :size="17"/>{{ isRecommending ? '计算中' : candidatePrograms.length ? '生成建议' : '请先检索选择院校' }}</button></div>
      <p v-if="recommendError" class="notice">{{ recommendError }}</p>
      <div class="recommend-layout"><aside class="recommend-form"><h2>个人画像</h2><label>目标方向<ComboBox v-model="profile.targetMajor" :options="allMajors.map(m => ({label: m.code+' '+m.name, value: m.code}))" placeholder="输入专业名称搜索"/></label><label>预估初试分<input v-model.number="profile.estimatedScore" type="number" min="0" max="500"/></label><label>目标地区<div class="province-combo"><div class="province-tags"><span v-for="p in selectedProvinces" :key="p" class="province-tag">{{ p }}<button @click.prevent="removeProvince(p)">&times;</button></span><input v-model="provinceSearch" @input="onProvinceInput" @focus="provinceDropdownOpen=true" @keydown="onProvinceKeydown" placeholder="输入或选择省份" class="province-input"/></div><div v-if="provinceDropdownOpen && filteredProvinces.length" class="province-dropdown"><div v-for="p in filteredProvinces" :key="p" class="province-option" @mousedown.prevent="addProvince(p)">{{ p }}</div></div></div></label><label>风险偏好<select v-model="profile.riskPreference"><option value="CONSERVATIVE">保守</option><option value="BALANCED">平衡</option><option value="AGGRESSIVE">进取</option></select></label><h2>权重配置</h2><label v-for="(value, key) in weights" :key="key">{{ ({ score: '分数匹配', competition: '竞争度', region: '地区', major: '专业' })[key] }}<input v-model.number="weights[key]" type="range" min="0" max="60"/><span>{{ value }}</span></label><p class="candidate-note">候选集：{{ candidatePrograms.length }} 项</p></aside><div><div v-if="!recommendations.length" class="empty"><Sparkles :size="25"/>{{ candidatePrograms.length ? '点击"生成建议"获取择校推荐' : '请先到院校检索页选择或浏览院校数据' }}</div><div v-else class="recommendations"><article v-for="item in recommendations" :key="`${item.id}-${item.major_name}`"><div><span class="tier" :class="item.tier">{{ item.tier }}</span><b>{{ item.recommendation_score }}</b></div><h2>{{ item.university_name }}</h2><p>{{ item.major_name }} · {{ item.province }}</p><ul><li v-for="reason in item.reasons" :key="reason">{{ reason }}</li></ul><footer>{{ item.admission_year }} 年 · {{ item.source_name || '来源待补充' }} · {{ item.model_version }}</footer></article></div><p v-if="recommendations.length" class="disclaimer">仅供择校参考，不构成录取承诺。</p></div></div>
    </section>

    <section v-else-if="route === '/user/profile'" class="page-wrap user-page">
      <div class="profile-header-bar">
        <div class="profile-banner"></div>
        <div class="profile-info-row">
          <div class="profile-avatar"><User :size="48" color="#fff"/></div>
          <div class="profile-meta">
            <h2>{{ currentUser?.username }}</h2>
            <span class="role-badge" :class="currentUser?.role?.toLowerCase()">{{ currentUser?.role === 'ADMIN' ? '管理员' : currentUser?.role === 'TEST' ? '测试账号' : '考研学生' }}</span>
          </div>
        </div>
      </div>
      <div class="profile-body">
        <div class="profile-sidebar">
          <h3>我的数据</h3>
          <ul class="stats-list">
            <li><span class="stat-num">{{ selectedPrograms.length }}</span><span>对比清单</span></li>
            <li><span class="stat-num">{{ profile.estimatedScore }}</span><span>预估分数</span></li>
            <li><span class="stat-num">{{ selectedProvinces.length }}</span><span>目标省份</span></li>
          </ul>
          <button class="primary" style="width:100%;margin-top:12px" @click="go('/programs')">去检索</button>
        </div>
        <div class="profile-main">
          <h3>快捷入口</h3>
          <div class="quick-links">
            <button class="plain" @click="go('/programs')">院校专业检索</button>
            <button class="plain" @click="go('/compare')">对比清单</button>
            <button class="plain" @click="go('/recommend')">择校建议</button>
            <button class="plain" @click="go('/charts')">数据可视化</button>
          </div>
          <h3 style="margin-top:20px">账号操作</h3>
          <button class="logout-btn" @click="logout()" style="margin-top:8px"><LogOut :size="15"/> 退出登录</button>
        </div>
      </div>
    </section>

    <!-- ========== TEST角色：API调试 ========== -->
    <section v-else-if="route === '/test/api'" class="page-wrap admin-page">
      <div class="page-title"><div><p>API DEBUGGER</p><h1>API 接口调试</h1><span>测试后端API接口，查看返回数据。</span></div></div>
      <div class="api-debugger">
        <div class="api-form">
          <div class="api-row">
            <select v-model="apiTestMethod" class="api-method"><option>GET</option><option>POST</option><option>PUT</option><option>DELETE</option></select>
            <input v-model="apiTestUrl" class="api-url" placeholder="输入API路径"/>
            <button class="primary" @click="runApiTest" :disabled="apiTestLoading">{{ apiTestLoading ? '请求中...' : '发送' }}</button>
          </div>
          <div v-if="apiTestMethod === 'POST' || apiTestMethod === 'PUT'" class="api-body">
            <label>请求体 (JSON)</label>
            <textarea v-model="apiTestBody" rows="6" placeholder='{"key": "value"}'></textarea>
          </div>
          <div class="api-presets">
            <span>快捷请求：</span>
            <button class="plain" @click="apiTestUrl='/api/v1/programs?page=0&pageSize=5'; apiTestMethod='GET'">招生列表</button>
            <button class="plain" @click="apiTestUrl='/api/v1/programs/1'; apiTestMethod='GET'">单条记录</button>
            <button class="plain" @click="apiTestUrl='/recommendation/api/v1/recommendations'; apiTestMethod='POST'; apiTestBody=JSON.stringify({profile:{estimated_score:340,target_major:'计算机科学与技术',preferred_provinces:['北京'],risk_preference:'BALANCED'},programs:[],weights:{score:45,competition:20,region:15,major:15}},null,2)">推荐接口</button>
          </div>
        </div>
        <div v-if="apiTestResult" class="api-result">
          <div class="result-header"><span :class="apiTestResult.status === 200 ? 'status-ok' : 'status-err'">HTTP {{ apiTestResult.status }} {{ apiTestResult.statusText }}</span></div>
          <pre class="result-body">{{ apiTestResult.body }}</pre>
        </div>
      </div>
    </section>

    <!-- ========== 管理员端 ========== -->
    <AdminDashboard v-else-if="route === '/admin/dashboard'"/>
    <AdminDataManage v-else-if="route === '/admin/data'"/>
    <AdminDataImport v-else-if="route === '/admin/import'"/>
    <AdminUserManage v-else-if="route === '/admin/users'"/>
    <AdminSystemLog v-else-if="route === '/admin/logs'"/>

    <section v-else class="page-wrap">
      <div class="empty"><GraduationCap :size="40"/><p>请选择功能模块</p></div>
    </section>
  </main>
</template>
