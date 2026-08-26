<script setup>
import { computed, onMounted, ref, watch, nextTick } from "vue";
import { BarChart3, Bookmark, ChevronLeft, ChevronRight, Database, ExternalLink, GraduationCap, MapPin, PieChart, Search, SlidersHorizontal, Sparkles, X } from "lucide-vue-next";
import * as echarts from "echarts";

const apiBase = "/api/v1";
const recommendationUrl = "/recommendation/api/v1/recommendations";
const route = ref(location.hash.replace("#", "") || "/programs");
const programs = ref([]); const total = ref(0); const loading = ref(false); const apiError = ref(false);
const selectedPrograms = ref(JSON.parse(localStorage.getItem("shortlist") || "[]"));
const recommendations = ref([]); const isRecommending = ref(false); const page = ref(0);
const filters = ref({ keyword: "", province: "", majorCode: "", examKeyword: "", studyMode: "" });
const profile = ref({ targetMajor: "大数据技术与工程", estimatedScore: 340, preferredProvinces: "江苏,浙江", riskPreference: "BALANCED" });
const weights = ref({ score: 45, competition: 20, region: 15, major: 15 });
const pageSize = 12;
const nav = [{ path: "/programs", label: "招生检索", icon: Search }, { path: "/compare", label: "对比清单", icon: BarChart3 }, { path: "/recommend", label: "择校建议", icon: Sparkles }, { path: "/charts", label: "数据可视化", icon: PieChart }];
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)));
const candidatePrograms = computed(() => selectedPrograms.value.length ? selectedPrograms.value : programs.value);
function go(path) { location.hash = path; }
window.addEventListener("hashchange", () => route.value = location.hash.replace("#", "") || "/programs");
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

async function initCharts() {
  if (chartsLoaded.value) return;
  chartsLoaded.value = true;
  try {
    const allPrograms = [];
    let pg = 0;
    const ps = 200;
    let tot = Infinity;
    while (pg * ps < tot) {
      const res = await fetch(`${apiBase}/programs?page=${pg}&pageSize=${ps}`);
      if (!res.ok) break;
      const body = await res.json();
      allPrograms.push(...body.items);
      tot = body.total;
      pg++;
    }
    renderCharts(allPrograms);
  } catch {}
}

function renderCharts(programs) {
  const provMap = {}, majorMap = {}, yearMap = {};
  const uniEnroll = {};
  programs.forEach(p => {
    provMap[p.province] = (provMap[p.province] || 0) + 1;
    const mc = p.majorCode?.substring(0, 4) || p.majorCode;
    majorMap[mc] = (majorMap[mc] || 0) + 1;
    yearMap[p.admissionYear] = (yearMap[p.admissionYear] || 0) + 1;
    const name = p.universityName;
    if (!uniEnroll[name]) uniEnroll[name] = { e: 0, r: 0 };
    if (p.actualEnrollment) uniEnroll[name].e += p.actualEnrollment;
    if (p.registrationCount) uniEnroll[name].r += p.registrationCount;
  });
  nextTick(() => {
    renderProvinceChart(provMap);
    renderMajorChart(majorMap);
    renderYearChart(yearMap, programs);
    renderEnrollChart(uniEnroll);
  });
}

function renderProvinceChart(data) {
  const el = document.getElementById("chart-province"); if (!el) return;
  if (provinceChart) provinceChart.dispose();
  provinceChart = echarts.init(el);
  const s = Object.entries(data).sort((a, b) => b[1] - a[1]);
  provinceChart.setOption({ title: { text: "各省份数据分布", left: "center" }, tooltip: { trigger: "axis" }, xAxis: { type: "category", data: s.map(x => x[0]), axisLabel: { rotate: 45, fontSize: 11 } }, yAxis: { type: "value" }, series: [{ type: "bar", data: s.map(x => x[1]), itemStyle: { color: "#409eff" } }], grid: { left: 50, right: 20, bottom: 80, top: 40 } });
}

function renderMajorChart(data) {
  const el = document.getElementById("chart-major"); if (!el) return;
  if (majorChart) majorChart.dispose();
  majorChart = echarts.init(el);
  const lbl = { "0812": "0812 计算机", "0835": "0835 软件工程", "0839": "0839 网安", "0854": "0854 电子信息" };
  const pie = Object.entries(data).map(([k, v]) => ({ name: lbl[k] || k, value: v }));
  majorChart.setOption({ title: { text: "专业代码分布", left: "center" }, tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" }, legend: { bottom: 0 }, series: [{ type: "pie", radius: ["30%", "55%"], label: { formatter: "{b}\n{d}%" }, data: pie }] });
}

function renderYearChart(yearMap, programs) {
  const el = document.getElementById("chart-year"); if (!el) return;
  if (yearChart) yearChart.dispose();
  yearChart = echarts.init(el);
  const years = Object.keys(yearMap).sort();
  const enr = {}, reg = {};
  programs.forEach(p => { const y = p.admissionYear; if (p.actualEnrollment) enr[y] = (enr[y] || 0) + p.actualEnrollment; if (p.registrationCount) reg[y] = (reg[y] || 0) + p.registrationCount; });
  const ratio = years.map(y => reg[y] && enr[y] ? +(reg[y] / enr[y]).toFixed(2) : null);
  yearChart.setOption({ title: { text: "年度数据与报录比", left: "center" }, tooltip: { trigger: "axis" }, legend: { bottom: 0, data: ["记录数", "录取人数", "报录比"] }, xAxis: { type: "category", data: years }, yAxis: [{ type: "value" }, { type: "value", name: "报录比", min: 0 }], series: [{ name: "记录数", type: "bar", data: years.map(y => yearMap[y]) }, { name: "录取人数", type: "bar", data: years.map(y => enr[y] || 0) }, { name: "报录比", type: "line", yAxisIndex: 1, data: ratio, itemStyle: { color: "#e6a23c" } }], grid: { left: 50, right: 50, bottom: 50, top: 40 } });
}

function renderEnrollChart(uniEnroll) {
  const el = document.getElementById("chart-enrollment"); if (!el) return;
  if (enrollmentChart) enrollmentChart.dispose();
  enrollmentChart = echarts.init(el);
  const s = Object.entries(uniEnroll).filter(([, v]) => v.e > 0).sort((a, b) => b[1].e - a[1].e).slice(0, 12);
  enrollmentChart.setOption({ title: { text: "TOP12 高校录取规模", left: "center" }, tooltip: { trigger: "axis" }, legend: { bottom: 0, data: ["录取", "报名"] }, xAxis: { type: "category", data: s.map(x => x[0].length > 6 ? x[0].substring(0, 6) + ".." : x[0]), axisLabel: { rotate: 30, fontSize: 11 } }, yAxis: { type: "value" }, series: [{ name: "录取", type: "bar", data: s.map(x => x[1].e), itemStyle: { color: "#67c23a" } }, { name: "报名", type: "bar", data: s.map(x => x[1].r), itemStyle: { color: "#f56c6c" } }], grid: { left: 50, right: 20, bottom: 60, top: 40 } });
}

watch(route, (v) => { if (v === "/charts") setTimeout(initCharts, 100); });
window.addEventListener("resize", () => { [provinceChart, majorChart, yearChart, enrollmentChart].forEach(c => c?.resize()); });

onMounted(loadPrograms);
</script>

<template>
  <main class="app-shell">
    <header class="app-header"><button class="brand" @click="go('/programs')"><GraduationCap :size="22"/> 计算机考研择校</button><nav><button v-for="item in nav" :key="item.path" :class="{active:route===item.path}" @click="go(item.path)"><component :is="item.icon" :size="17"/>{{ item.label }}</button></nav><span class="header-note"><Database :size="15"/>公开数据优先</span></header>
    <section v-if="route === '/programs'" class="page-wrap">
      <div class="page-title"><div><p>PROGRAM DIRECTORY</p><h1>招生信息检索</h1><span>仅展示已发布记录。数据年份、来源和采集时间在每个项目中可追溯。</span></div><button class="primary" @click="openRecommend"><Sparkles :size="17"/>生成择校建议</button></div>
      <form class="filters" @submit.prevent="submitSearch"><label class="wide"><Search :size="16"/><input v-model="filters.keyword" placeholder="院校或专业名称"/></label><label><MapPin :size="16"/><select v-model="filters.province"><option value="">全部省份</option><option>北京</option><option>上海</option><option>江苏</option><option>浙江</option><option>湖北</option><option>四川</option><option>陕西</option><option>辽宁</option><option>福建</option><option>广西</option><option>吉林</option><option>贵州</option><option>河北</option><option>新疆</option><option>西藏</option><option>广东</option><option>湖南</option><option>安徽</option><option>山东</option><option>黑龙江</option></select></label><label><select v-model="filters.majorCode"><option value="">全部专业代码</option><option value="0812">0812 计算机</option><option value="0835">0835 软件工程</option><option value="0839">0839 网安</option><option value="0854">0854 电子信息</option></select></label><label><SlidersHorizontal :size="16"/><select v-model="filters.examKeyword"><option value="">全部专业课</option><option value="408">408</option><option value="数学二">数学二</option><option value="数学一">数学一</option></select></label><button class="primary" :disabled="loading">{{loading ? '检索中' : '检索'}}</button><button type="button" class="plain" @click="clearFilters">清空</button></form>
      <p v-if="apiError" class="notice">业务服务不可用，当前不显示未经验证的本地替代数据。</p><p class="result-meta">{{ total }} 条已发布项目 · 第 {{ page + 1 }} / {{ totalPages }} 页</p>
      <div class="programs"><article v-for="p in programs" :key="p.id" class="program"><div class="program-head"><span>{{p.majorCode}}</span><button class="icon" :class="{chosen:selected(p)}" :title="selected(p)?'移出对比':'加入对比'" @click="toggle(p)"><Bookmark :size="17" :fill="selected(p)?'currentColor':'none'"/></button></div><h2>{{p.universityName}}</h2><strong>{{p.majorName}}</strong><div class="tags"><span>{{p.province}}</span><span>{{p.studyMode === 'FULL_TIME' ? '全日制' : p.studyMode}}</span><span>{{p.admissionYear}} 年</span></div><dl><div><dt>复试线</dt><dd>{{p.reexaminationLine ?? '未公开'}}</dd></div><div><dt>计划</dt><dd>{{p.plannedEnrollment ?? '未公开'}}</dd></div><div><dt>报录比</dt><dd>{{ratio(p)}}</dd></div></dl><p class="subjects">{{p.examSubjects}}</p><footer><span>来源：{{p.sourceName || '未标注'}}</span><a v-if="p.sourceUrl" :href="p.sourceUrl" target="_blank" rel="noreferrer">查看来源 <ExternalLink :size="12"/></a><small>采集：{{sourceTime(p)}}</small></footer></article></div>
      <div class="pager"><button class="icon" :disabled="page===0" @click="page--;loadPrograms()"><ChevronLeft :size="17"/></button><span>第 {{page+1}} 页</span><button class="icon" :disabled="page+1>=totalPages" @click="page++;loadPrograms()"><ChevronRight :size="17"/></button></div>
    </section>
    <section v-else-if="route === '/compare'" class="page-wrap"><div class="page-title"><div><p>SHORTLIST</p><h1>对比清单 <em>{{selectedPrograms.length}} / 5</em></h1><span>不同年份的数据不应直接等价比较。</span></div><button class="plain" :disabled="!selectedPrograms.length" @click="selectedPrograms=[]">清空清单</button></div><div v-if="!selectedPrograms.length" class="empty"><Bookmark :size="25"/>从检索页加入不超过 5 个项目。</div><div v-else class="comparison"><table><thead><tr><th>院校专业</th><th>年份</th><th>复试线</th><th>计划</th><th>报录比</th><th>考试科目</th><th>来源</th><th></th></tr></thead><tbody><tr v-for="p in selectedPrograms" :key="p.id"><td><b>{{p.universityName}}</b><span>{{p.majorCode}} · {{p.majorName}}</span></td><td>{{p.admissionYear}}</td><td>{{p.reexaminationLine ?? '未公开'}}</td><td>{{p.plannedEnrollment ?? '未公开'}}</td><td>{{ratio(p)}}</td><td>{{p.examSubjects}}</td><td>{{p.sourceName}}</td><td><button class="icon" @click="toggle(p)"><X :size="16"/></button></td></tr></tbody></table></div></section>
    <section v-else-if="route === '/charts'" class="page-wrap charts-page">
      <div class="page-title"><div><p>DATA ANALYTICS</p><h1>数据可视化</h1><span>基于全部已发布数据的统计分析图表。</span></div></div>
      <div class="chart-grid">
        <div class="chart-card"><div id="chart-province" class="chart-box"></div></div>
        <div class="chart-card"><div id="chart-major" class="chart-box"></div></div>
        <div class="chart-card"><div id="chart-year" class="chart-box"></div></div>
        <div class="chart-card"><div id="chart-enrollment" class="chart-box"></div></div>
      </div>
    </section>
    <section v-else class="page-wrap recommendation"><div class="page-title"><div><p>DECISION SUPPORT</p><h1>择校建议</h1><span>模型会解释评分组成，但不构成录取承诺。</span></div><button class="primary" :disabled="isRecommending || !candidatePrograms.length" @click="getRecommendations"><Sparkles :size="17"/>{{isRecommending?'计算中':'更新建议'}}</button></div><div class="recommend-layout"><aside class="recommend-form"><h2>个人画像</h2><label>目标方向<select v-model="profile.targetMajor"><option>大数据技术与工程</option><option>计算机科学与技术</option><option>计算机技术</option><option>网络空间安全</option></select></label><label>预估初试分<input v-model.number="profile.estimatedScore" type="number" min="0" max="500"/></label><label>目标地区<input v-model="profile.preferredProvinces" placeholder="江苏,浙江"/></label><label>风险偏好<select v-model="profile.riskPreference"><option value="CONSERVATIVE">保守</option><option value="BALANCED">平衡</option><option value="AGGRESSIVE">进取</option></select></label><h2>权重配置</h2><label v-for="(value,key) in weights" :key="key">{{({score:'分数匹配',competition:'竞争度',region:'地区',major:'专业'})[key]}}<input v-model.number="weights[key]" type="range" min="0" max="60"/><span>{{value}}</span></label><p class="candidate-note">候选集：{{candidatePrograms.length}} 项；优先使用对比清单。</p></aside><div><div v-if="!recommendations.length" class="empty"><Sparkles :size="25"/>填写画像后生成建议；结果会列出数据年份、来源和理由。</div><div v-else class="recommendations"><article v-for="item in recommendations" :key="`${item.id}-${item.major_name}`"><div><span class="tier" :class="item.tier">{{item.tier}}</span><b>{{item.recommendation_score}}</b></div><h2>{{item.university_name}}</h2><p>{{item.major_name}} · {{item.province}}</p><ul><li v-for="reason in item.reasons" :key="reason">{{reason}}</li></ul><footer>{{item.admission_year}} 年 · {{item.source_name || '来源待补充'}} · {{item.model_version}}</footer></article></div><p v-if="recommendations.length" class="disclaimer">仅供择校参考，不构成录取承诺。请以对应年度院校官方发布信息为准。</p></div></div></section>
  </main>
</template>