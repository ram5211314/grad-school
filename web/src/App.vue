<script setup>
import { computed, onMounted, ref, watch, nextTick } from "vue";
import { BarChart3, Bookmark, ChevronLeft, ChevronRight, Database, ExternalLink, GraduationCap, LayoutDashboard, MapPin, PieChart, Search, Settings, Shield, SlidersHorizontal, Sparkles, Upload, User, Users, FileText, X } from "lucide-vue-next";
import * as echarts from "echarts";

const apiBase = "/api/v1";
const recommendationUrl = "/recommendation/api/v1/recommendations";
const route = ref(location.hash.replace("#", "") || "/programs");
const mode = ref("user");
const programs = ref([]); const total = ref(0); const loading = ref(false); const apiError = ref(false);
const selectedPrograms = ref(JSON.parse(localStorage.getItem("shortlist") || "[]"));
const recommendations = ref([]); const isRecommending = ref(false); const page = ref(0);
const filters = ref({ keyword: "", province: "", majorCode: "", examKeyword: "", studyMode: "" });
const profile = ref({ targetMajor: "大数据技术与工程", estimatedScore: 340, preferredProvinces: "江苏,浙江", riskPreference: "BALANCED" });
const weights = ref({ score: 45, competition: 20, region: 15, major: 15 });
const pageSize = 12;
const userNav = [{ path: "/programs", label: "招生检索", icon: Search }, { path: "/compare", label: "对比清单", icon: BarChart3 }, { path: "/recommend", label: "择校建议", icon: Sparkles }, { path: "/charts", label: "数据可视化", icon: PieChart }, { path: "/user/profile", label: "个人中心", icon: User }, { path: "/user/favorites", label: "我的收藏", icon: Bookmark }];
const adminNav = [{ path: "/admin/dashboard", label: "系统概览", icon: LayoutDashboard }, { path: "/admin/data", label: "数据管理", icon: Database }, { path: "/admin/import", label: "数据导入", icon: Upload }, { path: "/admin/users", label: "用户管理", icon: Users }, { path: "/admin/logs", label: "系统日志", icon: FileText }];
const nav = computed(() => mode.value === "admin" ? adminNav : userNav);
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)));
const candidatePrograms = computed(() => selectedPrograms.value.length ? selectedPrograms.value : programs.value);

function go(path) { location.hash = path; }
function switchMode(m) { mode.value = m; const first = nav.value[0]; if (first) go(first.path); }
window.addEventListener("hashchange", () => {
  const r = location.hash.replace("#", "") || "/programs";
  route.value = r;
  if (r.startsWith("/admin")) mode.value = "admin";
});
watch(selectedPrograms, value => localStorage.setItem("shortlist", JSON.stringify(value)), { deep: true });
function ratio(p) { return p.registrationCount && p.actualEnrollment ? `${(p.registrationCount / p.actualEnrollment).toFixed(1)} : 1` : "未公开"; }
function sourceTime(p) { return p.collectedAt ? new Date(p.collectedAt).toLocaleDateString("zh-CN") : "未记录"; }
function selected(p) { return selectedPrograms.value.some(item => item.id === p.id); }
function toggle(p) { const i = selectedPrograms.value.findIndex(item => item.id === p.id); if (i >= 0) selectedPrograms.value.splice(i, 1); else if (selectedPrograms.value.length < 5) selectedPrograms.value.push(p); }
function clearFilters() { filters.value = { keyword: "", province: "", majorCode: "", examKeyword: "", studyMode: "" }; page.value = 0; loadPrograms(); }
async function loadPrograms() { loading.value = true; apiError.value = false; try { const params = new URLSearchParams({ page: page.value, pageSize, sort: "admissionYear,desc" }); Object.entries(filters.value).forEach(([k,v]) => v && params.set(k,v)); const res = await fetch(`${apiBase}/programs?${params}`); if (!res.ok) throw new Error(); const body = await res.json(); programs.value = body.items; total.value = body.total; } catch { apiError.value = true; programs.value = []; total.value = 0; } finally { loading.value = false; } }
function submitSearch() { page.value = 0; loadPrograms(); }
async function getRecommendations() { if (!candidatePrograms.value.length) return; isRecommending.value = true; const requestProfile = { estimated_score: profile.value.estimatedScore, target_major: profile.value.targetMajor, preferred_provinces: profile.value.preferredProvinces.split(",").map(x => x.trim()).filter(Boolean), risk_preference: profile.value.riskPreference }; const requestPrograms = candidatePrograms.value.map(p => ({ id:p.id, university_name:p.universityName, major_name:p.majorName, province:p.province, reexamination_line:p.reexaminationLine, national_line:p.nationalLine, actual_enrollment:p.actualEnrollment, registration_count:p.registrationCount, admission_year:p.admissionYear, source_name:p.sourceName })); try { const res = await fetch(recommendationUrl, { method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({profile:requestProfile, programs:requestPrograms, weights:weights.value}) }); if (!res.ok) throw new Error(); recommendations.value = (await res.json()).items; } finally { isRecommending.value = false; } }
function openRecommend() { go("/recommend"); setTimeout(getRecommendations, 0); }
let provinceChart, majorChart, yearChart, enrollmentChart;
const chartsLoaded = ref(false);
async function initCharts() { if (chartsLoaded.value) return; chartsLoaded.value = true; try { const all = []; let pg = 0; let tot = Infinity; while (pg * 200 < tot) { const res = await fetch(`${apiBase}/programs?page=${pg}&pageSize=200`); if (!res.ok) break; const b = await res.json(); all.push(...b.items); tot = b.total; pg++; } renderCharts(all); } catch {} }
function renderCharts(programs) { const provMap = {}, majorMap = {}, yearMap = {}, uniEnroll = {}; programs.forEach(p => { provMap[p.province] = (provMap[p.province] || 0) + 1; const mc = p.majorCode?.substring(0, 4) || p.majorCode; majorMap[mc] = (majorMap[mc] || 0) + 1; yearMap[p.admissionYear] = (yearMap[p.admissionYear] || 0) + 1; const n = p.universityName; if (!uniEnroll[n]) uniEnroll[n] = { e: 0, r: 0 }; if (p.actualEnrollment) uniEnroll[n].e += p.actualEnrollment; if (p.registrationCount) uniEnroll[n].r += p.registrationCount; }); nextTick(() => { renderProvinceChart(provMap); renderMajorChart(majorMap); renderYearChart(yearMap, programs); renderEnrollChart(uniEnroll); }); }
function renderProvinceChart(data) { const el = document.getElementById("chart-province"); if (!el) return; if (provinceChart) provinceChart.dispose(); provinceChart = echarts.init(el); const s = Object.entries(data).sort((a, b) => b[1] - a[1]); provinceChart.setOption({ title: { text: "各省份数据分布", left: "center" }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: s.map(x => x[0]), axisLabel: { rotate: 45, fontSize: 11 } }, yAxis: { type: "value" }, series: [{ type: "bar", data: s.map(x => x[1]), itemStyle: { color: "#409eff" } }], grid: { left: 50, right: 20, bottom: 80, top: 40 } }); }
function renderMajorChart(data) { const el = document.getElementById("chart-major"); if (!el) return; if (majorChart) majorChart.dispose(); majorChart = echarts.init(el); const lbl = { "0812": "0812 计算机", "0835": "0835 软件工程", "0839": "0839 网安", "0854": "0854 电子信息" }; majorChart.setOption({ title: { text: "专业代码分布", left: "center" }, tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" }, legend: { bottom: 0 }, series: [{ type: "pie", radius: ["30%", "55%"], label: { formatter: "{b}\n{d}%" }, data: Object.entries(data).map(([k, v]) => ({ name: lbl[k] || k, value: v })) }] }); }
function renderYearChart(yearMap, programs) { const el = document.getElementById("chart-year"); if (!el) return; if (yearChart) yearChart.dispose(); yearChart = echarts.init(el); const years = Object.keys(yearMap).sort(); const enr = {}, reg = {}; programs.forEach(p => { const y = p.admissionYear; if (p.actualEnrollment) enr[y] = (enr[y] || 0) + p.actualEnrollment; if (p.registrationCount) reg[y] = (reg[y] || 0) + p.registrationCount; }); yearChart.setOption({ title: { text: "年度数据与报录比", left: "center" }, tooltip: { trigger: "axis" }, legend: { bottom: 0, data: ["记录数", "录取人数", "报录比"] }, xAxis: { type: "category", data: years }, yAxis: [{ type: "value" }, { type: "value", name: "报录比", min: 0 }], series: [{ name: "记录数", type: "bar", data: years.map(y => yearMap[y]) }, { name: "录取人数", type: "bar", data: years.map(y => enr[y] || 0) }, { name: "报录比", type: "line", yAxisIndex: 1, data: years.map(y => reg[y] && enr[y] ? +(reg[y] / enr[y]).toFixed(2) : null), itemStyle: { color: "#e6a23c" } }], grid: { left: 50, right: 50, bottom: 50, top: 40 } }); }
function renderEnrollChart(uniEnroll) { const el = document.getElementById("chart-enrollment"); if (!el) return; if (enrollmentChart) enrollmentChart.dispose(); enrollmentChart = echarts.init(el); const s = Object.entries(uniEnroll).filter(([, v]) => v.e > 0).sort((a, b) => b[1].e - a[1].e).slice(0, 12); enrollmentChart.setOption({ title: { text: "TOP12 高校录取规模", left: "center" }, tooltip: { trigger: "axis" }, legend: { bottom: 0, data: ["录取", "报名"] }, xAxis: { type: "category", data: s.map(x => x[0].length > 6 ? x[0].substring(0, 6) + ".." : x[0]), axisLabel: { rotate: 30, fontSize: 11 } }, yAxis: { type: "value" }, series: [{ name: "录取", type: "bar", data: s.map(x => x[1].e), itemStyle: { color: "#67c23a" } }, { name: "报名", type: "bar", data: s.map(x => x[1].r), itemStyle: { color: "#f56c6c" } }], grid: { left: 50, right: 20, bottom: 60, top: 40 } }); }
watch(route, (v) => { if (v === "/charts") setTimeout(initCharts, 100); });
window.addEventListener("resize", () => { [provinceChart, majorChart, yearChart, enrollmentChart].forEach(c => c?.resize()); });
onMounted(loadPrograms);
</script>

<template>
  <main class="app-shell">
    <header class="app-header">
      <button class="brand" @click="go('/programs')"><GraduationCap :size="22"/> 计算机考研择校</button>
      <div class="mode-switch">
        <button :class="{ active: mode === 'user' }" @click="switchMode('user')"><User :size="15"/> 用户端</button>
        <button :class="{ active: mode === 'admin' }" @click="switchMode('admin')"><Shield :size="15"/> 管理员</button>
      </div>
      <nav><button v-for="item in nav" :key="item.path" :class="{ active: route === item.path }" @click="go(item.path)"><component :is="item.icon" :size="17"/>{{ item.label }}</button></nav>
      <span class="header-note"><Database :size="15"/>公开数据优先</span>
    </header>

    <!-- ========== 用户端 ========== -->
    <section v-if="route === '/programs'" class="page-wrap">
      <div class="page-title"><div><p>PROGRAM DIRECTORY</p><h1>招生信息检索</h1><span>仅展示已发布记录。数据年份、来源和采集时间在每个项目中可追溯。</span></div><button class="primary" @click="openRecommend"><Sparkles :size="17"/>生成择校建议</button></div>
      <form class="filters" @submit.prevent="submitSearch"><label class="wide"><Search :size="16"/><input v-model="filters.keyword" placeholder="院校或专业名称"/></label><label><MapPin :size="16"/><select v-model="filters.province"><option value="">全部省份</option><option>北京</option><option>上海</option><option>江苏</option><option>浙江</option><option>湖北</option><option>四川</option><option>陕西</option><option>辽宁</option><option>福建</option><option>广东</option><option>湖南</option><option>安徽</option><option>山东</option><option>河北</option></select></label><label><select v-model="filters.majorCode"><option value="">全部专业代码</option><option value="0812">0812 计算机</option><option value="0835">0835 软件工程</option><option value="0839">0839 网安</option><option value="0854">0854 电子信息</option></select></label><label><SlidersHorizontal :size="16"/><select v-model="filters.examKeyword"><option value="">全部专业课</option><option value="408">408</option><option value="数学二">数学二</option><option value="数学一">数学一</option></select></label><button class="primary" :disabled="loading">{{ loading ? '检索中' : '检索' }}</button><button type="button" class="plain" @click="clearFilters">清空</button></form>
      <p v-if="apiError" class="notice">业务服务不可用。</p><p class="result-meta">{{ total }} 条已发布项目 · 第 {{ page + 1 }} / {{ totalPages }} 页</p>
      <div class="programs"><article v-for="p in programs" :key="p.id" class="program"><div class="program-head"><span>{{ p.majorCode }}</span><button class="icon" :class="{ chosen: selected(p) }" @click="toggle(p)"><Bookmark :size="17" :fill="selected(p) ? 'currentColor' : 'none'"/></button></div><h2>{{ p.universityName }}</h2><strong>{{ p.majorName }}</strong><div class="tags"><span>{{ p.province }}</span><span>{{ p.studyMode === 'FULL_TIME' ? '全日制' : p.studyMode }}</span><span>{{ p.admissionYear }} 年</span></div><dl><div><dt>复试线</dt><dd>{{ p.reexaminationLine ?? '未公开' }}</dd></div><div><dt>计划</dt><dd>{{ p.plannedEnrollment ?? '未公开' }}</dd></div><div><dt>报录比</dt><dd>{{ ratio(p) }}</dd></div></dl><p class="subjects">{{ p.examSubjects }}</p><footer><span>来源：{{ p.sourceName || '未标注' }}</span><a v-if="p.sourceUrl" :href="p.sourceUrl" target="_blank">查看来源 <ExternalLink :size="12"/></a><small>采集：{{ sourceTime(p) }}</small></footer></article></div>
      <div class="pager"><button class="icon" :disabled="page === 0" @click="page--; loadPrograms()"><ChevronLeft :size="17"/></button><span>第 {{ page + 1 }} 页</span><button class="icon" :disabled="page + 1 >= totalPages" @click="page++; loadPrograms()"><ChevronRight :size="17"/></button></div>
    </section>

    <section v-else-if="route === '/compare'" class="page-wrap">
      <div class="page-title"><div><p>SHORTLIST</p><h1>对比清单 <em>{{ selectedPrograms.length }} / 5</em></h1></div><button class="plain" @click="selectedPrograms = []">清空清单</button></div>
      <div v-if="!selectedPrograms.length" class="empty"><Bookmark :size="25"/>从检索页加入不超过 5 个项目。</div>
      <div v-else class="comparison"><table><thead><tr><th>院校专业</th><th>年份</th><th>复试线</th><th>计划</th><th>报录比</th><th>来源</th><th></th></tr></thead><tbody><tr v-for="p in selectedPrograms" :key="p.id"><td><b>{{ p.universityName }}</b><span>{{ p.majorCode }} · {{ p.majorName }}</span></td><td>{{ p.admissionYear }}</td><td>{{ p.reexaminationLine ?? '未公开' }}</td><td>{{ p.plannedEnrollment ?? '未公开' }}</td><td>{{ ratio(p) }}</td><td>{{ p.sourceName }}</td><td><button class="icon" @click="toggle(p)"><X :size="16"/></button></td></tr></tbody></table></div>
    </section>

    <section v-else-if="route === '/charts'" class="page-wrap charts-page">
      <div class="page-title"><div><p>DATA ANALYTICS</p><h1>数据可视化</h1><span>基于全部已发布数据的统计分析图表。</span></div></div>
      <div class="chart-grid"><div class="chart-card"><div id="chart-province" class="chart-box"></div></div><div class="chart-card"><div id="chart-major" class="chart-box"></div></div><div class="chart-card"><div id="chart-year" class="chart-box"></div></div><div class="chart-card"><div id="chart-enrollment" class="chart-box"></div></div></div>
    </section>

    <section v-else-if="route === '/recommend'" class="page-wrap recommendation">
      <div class="page-title"><div><p>DECISION SUPPORT</p><h1>择校建议</h1><span>模型会解释评分组成，但不构成录取承诺。</span></div><button class="primary" :disabled="isRecommending || !candidatePrograms.length" @click="getRecommendations"><Sparkles :size="17"/>{{ isRecommending ? '计算中' : '更新建议' }}</button></div>
      <div class="recommend-layout"><aside class="recommend-form"><h2>个人画像</h2><label>目标方向<select v-model="profile.targetMajor"><option>大数据技术与工程</option><option>计算机科学与技术</option><option>计算机技术</option><option>网络空间安全</option></select></label><label>预估初试分<input v-model.number="profile.estimatedScore" type="number" min="0" max="500"/></label><label>目标地区<input v-model="profile.preferredProvinces" placeholder="江苏,浙江"/></label><label>风险偏好<select v-model="profile.riskPreference"><option value="CONSERVATIVE">保守</option><option value="BALANCED">平衡</option><option value="AGGRESSIVE">进取</option></select></label><h2>权重配置</h2><label v-for="(value, key) in weights" :key="key">{{ ({ score: '分数匹配', competition: '竞争度', region: '地区', major: '专业' })[key] }}<input v-model.number="weights[key]" type="range" min="0" max="60"/><span>{{ value }}</span></label><p class="candidate-note">候选集：{{ candidatePrograms.length }} 项</p></aside><div><div v-if="!recommendations.length" class="empty"><Sparkles :size="25"/>填写画像后生成建议</div><div v-else class="recommendations"><article v-for="item in recommendations" :key="`${item.id}-${item.major_name}`"><div><span class="tier" :class="item.tier">{{ item.tier }}</span><b>{{ item.recommendation_score }}</b></div><h2>{{ item.university_name }}</h2><p>{{ item.major_name }} · {{ item.province }}</p><ul><li v-for="reason in item.reasons" :key="reason">{{ reason }}</li></ul><footer>{{ item.admission_year }} 年 · {{ item.source_name || '来源待补充' }} · {{ item.model_version }}</footer></article></div><p v-if="recommendations.length" class="disclaimer">仅供择校参考，不构成录取承诺。</p></div></div>
    </section>

    <section v-else-if="route === '/user/profile'" class="page-wrap user-page">
      <div class="page-title"><div><p>USER CENTER</p><h1>个人中心</h1></div></div>
      <div class="profile-layout">
        <div class="profile-card"><div class="avatar"><User :size="40" color="#409eff"/></div><h3>考研学生</h3><p>预估 {{ profile.estimatedScore }} 分</p></div>
        <div class="profile-form"><h3>学生画像</h3><div class="form-grid"><label>目标方向<select v-model="profile.targetMajor"><option>大数据技术与工程</option><option>计算机科学与技术</option><option>网络空间安全</option></select></label><label>预估初试分<input v-model.number="profile.estimatedScore" type="number"/></label><label>目标地区<input v-model="profile.preferredProvinces" placeholder="江苏,浙江"/></label><label>风险偏好<select v-model="profile.riskPreference"><option value="CONSERVATIVE">保守</option><option value="BALANCED">平衡</option><option value="AGGRESSIVE">进取</option></select></label></div></div>
      </div>
    </section>

    <section v-else-if="route === '/user/favorites'" class="page-wrap user-page">
      <div class="page-title"><div><p>FAVORITES</p><h1>我的收藏 <small>{{ selectedPrograms.length }} / 5</small></h1></div><button class="plain" @click="go('/programs')">去检索</button></div>
      <div v-if="!selectedPrograms.length" class="empty"><Bookmark :size="25"/>还没有收藏，去检索页添加。</div>
      <div v-else class="fav-grid"><article v-for="p in selectedPrograms" :key="p.id" class="fav-card"><h3>{{ p.universityName }}</h3><p>{{ p.majorCode }} · {{ p.majorName }}</p><div class="tags"><span>{{ p.province }}</span><span>{{ p.admissionYear }}年</span></div><dl><div><dt>复试线</dt><dd>{{ p.reexaminationLine ?? '未公开' }}</dd></div><div><dt>录取</dt><dd>{{ p.actualEnrollment ?? '-' }}</dd></div><div><dt>报录比</dt><dd>{{ ratio(p) }}</dd></div></dl><button class="icon danger" @click="toggle(p)">移除</button></article></div>
    </section>

    <!-- ========== 管理员端 ========== -->
    <section v-else-if="route === '/admin/dashboard'" class="page-wrap admin-page">
      <div class="page-title"><div><p>ADMIN DASHBOARD</p><h1>系统概览</h1></div></div>
      <div class="stat-cards"><div class="stat-card"><div class="stat-icon" style="background:#ecf5ff"><Database :size="24" color="#409eff"/></div><div class="stat-info"><span class="stat-num">{{ total }}</span><span class="stat-label">数据总量</span></div></div><div class="stat-card"><div class="stat-icon" style="background:#f0f9eb"><CheckCircle :size="24" color="#67c23a"/></div><div class="stat-info"><span class="stat-num">{{ total }}</span><span class="stat-label">已发布</span></div></div><div class="stat-card"><div class="stat-icon" style="background:#fdf6ec"><AlertCircle :size="24" color="#e6a23c"/></div><div class="stat-info"><span class="stat-num">0</span><span class="stat-label">待审核</span></div></div><div class="stat-card"><div class="stat-icon" style="background:#fef0f0"><Users :size="24" color="#f56c6c"/></div><div class="stat-info"><span class="stat-num">0</span><span class="stat-label">注册用户</span></div></div></div>
      <div class="dashboard-section"><h3>快速操作</h3><div class="quick-actions"><button class="action-btn" @click="go('/admin/data')">管理数据</button><button class="action-btn" @click="go('/admin/import')">导入数据</button><button class="action-btn" @click="go('/admin/users')">用户管理</button></div></div>
    </section>

    <section v-else-if="route === '/admin/data'" class="page-wrap admin-page">
      <div class="page-title"><div><p>DATA MANAGEMENT</p><h1>招生数据管理 <small>{{ total }} 条</small></h1></div><button class="plain" @click="loadPrograms">刷新</button></div>
      <form class="filters" @submit.prevent="submitSearch"><label><Search :size="14"/><input v-model="filters.keyword" placeholder="搜索院校/专业"/></label><select v-model="filters.province"><option value="">全部省份</option><option>北京</option><option>上海</option><option>江苏</option><option>浙江</option><option>湖北</option><option>四川</option><option>广东</option></select><select v-model="filters.majorCode"><option value="">全部专业</option><option value="0812">0812</option><option value="0835">0835</option><option value="0839">0839</option><option value="0854">0854</option></select><button class="primary" type="submit">查询</button></form>
      <div class="table-wrap"><table><thead><tr><th>ID</th><th>院校</th><th>省份</th><th>专业</th><th>年份</th><th>复试线</th><th>录取</th><th>报名</th></tr></thead><tbody><tr v-for="p in programs" :key="p.id"><td>{{ p.id }}</td><td><b>{{ p.universityName }}</b></td><td>{{ p.province }}</td><td>{{ p.majorCode }} {{ p.majorName }}</td><td>{{ p.admissionYear }}</td><td>{{ p.reexaminationLine ?? '未公开' }}</td><td>{{ p.actualEnrollment ?? '-' }}</td><td>{{ p.registrationCount ?? '未公开' }}</td></tr></tbody></table></div>
      <div class="pager"><button :disabled="page === 0" @click="page--; loadPrograms()">上一页</button><span>第 {{ page + 1 }} / {{ totalPages }} 页</span><button :disabled="page + 1 >= totalPages" @click="page++; loadPrograms()">下一页</button></div>
    </section>

    <section v-else-if="route === '/admin/import'" class="page-wrap admin-page">
      <div class="page-title"><div><p>DATA IMPORT</p><h1>数据导入</h1></div></div>
      <div class="import-card"><h3>上传CSV文件</h3><p>支持UTF-8编码CSV，首行为表头</p><p class="fields-hint">必填：universityName, province, majorCode, majorName, admissionYear</p></div>
    </section>

    <section v-else-if="route === '/admin/users'" class="page-wrap admin-page">
      <div class="page-title"><div><p>USER MANAGEMENT</p><h1>用户管理</h1></div></div>
      <p class="notice">用户管理功能需先实现账号注册/登录模块（Spring Security + RBAC）。</p>
    </section>

    <section v-else-if="route === '/admin/logs'" class="page-wrap admin-page">
      <div class="page-title"><div><p>SYSTEM LOGS</p><h1>系统日志</h1></div></div>
      <p class="notice">系统日志功能需先实现操作审计模块。</p>
    </section>

    <section v-else class="page-wrap">
      <div class="empty"><GraduationCap :size="40"/><p>请选择功能模块</p></div>
    </section>
  </main>
</template>
