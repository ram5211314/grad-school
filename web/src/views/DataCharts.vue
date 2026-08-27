<script setup>
import { onMounted, ref, nextTick } from "vue";
import * as echarts from "echarts";

const loading = ref(true);
const stats = ref({ total: 0, universities: 0, provinces: 0, years: 0 });

let provinceChart, majorChart, yearChart, enrollmentChart;

async function loadData() {
  loading.value = true;
  try {
    const allPrograms = [];
    let page = 0;
    const pageSize = 100;
    let total = Infinity;
    while (page * pageSize < total) {
      const res = await fetch(`/api/v1/programs?page=${page}&pageSize=${pageSize}`);
      if (!res.ok) break;
      const body = await res.json();
      allPrograms.push(...body.items);
      total = body.total;
      page++;
    }
    processCharts(allPrograms);
  } finally {
    loading.value = false;
  }
}

function processCharts(programs) {
  const uniSet = new Set();
  const provMap = {};
  const majorMap = {};
  const yearMap = {};
  let totalEnroll = 0;
  let totalReg = 0;
  let countWithEnroll = 0;

  programs.forEach(p => {
    uniSet.add(p.universityName);
    provMap[p.province] = (provMap[p.province] || 0) + 1;
    const mc = p.majorCode?.substring(0, 2) === "08" ? p.majorCode.substring(0, 4) : p.majorCode;
    majorMap[mc] = (majorMap[mc] || 0) + 1;
    yearMap[p.admissionYear] = (yearMap[p.admissionYear] || 0) + 1;
    if (p.actualEnrollment) { totalEnroll += p.actualEnrollment; countWithEnroll++; }
    if (p.registrationCount) totalReg += p.registrationCount;
  });

  stats.value = {
    total: programs.length,
    universities: uniSet.size,
    provinces: Object.keys(provMap).length,
    years: Object.keys(yearMap).length,
  };

  nextTick(() => {
    renderProvince(provMap);
    renderMajor(majorMap);
    renderYear(yearMap, programs);
    renderEnrollment(programs);
  });
}

function renderProvince(data) {
  const el = document.getElementById("chart-province");
  if (!el) return;
  if (provinceChart) provinceChart.dispose();
  provinceChart = echarts.init(el);
  const sorted = Object.entries(data).sort((a, b) => b[1] - a[1]);
  provinceChart.setOption({
    title: { text: "各省份院校专业数量", left: "center" },
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: sorted.map(x => x[0]), axisLabel: { rotate: 45, fontSize: 11 } },
    yAxis: { type: "value", name: "数量" },
    series: [{ type: "bar", data: sorted.map(x => x[1]), itemStyle: { color: "#409eff" } }],
    grid: { left: 60, right: 30, bottom: 80, top: 50 },
  });
}

function renderMajor(data) {
  const el = document.getElementById("chart-major");
  if (!el) return;
  if (majorChart) majorChart.dispose();
  majorChart = echarts.init(el);
  const labelMap = { "0812": "0812 计算机科学与技术", "0835": "0835 软件工程", "0839": "0839 网络空间安全", "0854": "0854 电子信息", "085404": "085404 计算机技术", "085405": "085405 软件工程", "085410": "085410 人工智能", "085411": "085411 大数据", "085412": "085412 网络与信息安全" };
  const pieData = Object.entries(data).map(([k, v]) => ({ name: labelMap[k] || k, value: v }));
  majorChart.setOption({
    title: { text: "专业代码分布", left: "center" },
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    legend: { bottom: 0, type: "scroll" },
    series: [{
      type: "pie", radius: ["35%", "60%"], center: ["50%", "50%"],
      label: { formatter: "{b}\n{d}%" },
      data: pieData,
    }],
  });
}

function renderYear(yearMap, programs) {
  const el = document.getElementById("chart-year");
  if (!el) return;
  if (yearChart) yearChart.dispose();
  yearChart = echarts.init(el);
  const years = Object.keys(yearMap).sort();

  const enrollByYear = {};
  const regByYear = {};
  const ratioByYear = {};
  programs.forEach(p => {
    const y = p.admissionYear;
    if (p.actualEnrollment) {
      enrollByYear[y] = (enrollByYear[y] || 0) + p.actualEnrollment;
    }
    if (p.registrationCount) {
      regByYear[y] = (regByYear[y] || 0) + p.registrationCount;
    }
  });
  years.forEach(y => {
    if (regByYear[y] && enrollByYear[y]) {
      ratioByYear[y] = +(regByYear[y] / enrollByYear[y]).toFixed(2);
    }
  });

  yearChart.setOption({
    title: { text: "年度数据量与报录趋势", left: "center" },
    tooltip: { trigger: "axis" },
    legend: { bottom: 0, data: ["记录数", "总录取", "总报名", "报录比"] },
    xAxis: { type: "category", data: years },
    yAxis: [
      { type: "value", name: "人数/条数" },
      { type: "value", name: "报录比", min: 0 },
    ],
    series: [
      { name: "记录数", type: "bar", data: years.map(y => yearMap[y]) },
      { name: "总录取", type: "bar", data: years.map(y => enrollByYear[y] || 0) },
      { name: "总报名", type: "bar", data: years.map(y => regByYear[y] || 0) },
      { name: "报录比", type: "line", yAxisIndex: 1, data: years.map(y => ratioByYear[y] || null), itemStyle: { color: "#e6a23c" } },
    ],
    grid: { left: 60, right: 60, bottom: 50, top: 50 },
  });
}

function renderEnrollment(programs) {
  const el = document.getElementById("chart-enrollment");
  if (!el) return;
  if (enrollmentChart) enrollmentChart.dispose();
  enrollmentChart = echarts.init(el);

  const uniEnroll = {};
  programs.forEach(p => {
    const name = p.universityName;
    if (!uniEnroll[name]) uniEnroll[name] = { enroll: 0, reg: 0 };
    if (p.actualEnrollment) uniEnroll[name].enroll += p.actualEnrollment;
    if (p.registrationCount) uniEnroll[name].reg += p.registrationCount;
  });

  const sorted = Object.entries(uniEnroll)
    .filter(([, v]) => v.enroll > 0)
    .sort((a, b) => b[1].enroll - a[1].enroll)
    .slice(0, 15);

  enrollmentChart.setOption({
    title: { text: "TOP15 高校录取人数", left: "center" },
    tooltip: { trigger: "axis" },
    legend: { bottom: 0, data: ["录取人数", "报名人数"] },
    xAxis: { type: "category", data: sorted.map(x => x[0].length > 8 ? x[0].substring(0, 8) + "..." : x[0]), axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: "value", name: "人数" },
    series: [
      { name: "录取人数", type: "bar", data: sorted.map(x => x[1].enroll), itemStyle: { color: "#67c23a" } },
      { name: "报名人数", type: "bar", data: sorted.map(x => x[1].reg), itemStyle: { color: "#f56c6c" } },
    ],
    grid: { left: 60, right: 30, bottom: 70, top: 50 },
  });
}

onMounted(() => { loadData(); window.addEventListener("resize", () => { [provinceChart, majorChart, yearChart, enrollmentChart].forEach(c => c?.resize()); }); });
</script>

<template>
  <section class="page-wrap charts-page">
    <div class="page-title">
      <div>
        <p>DATA ANALYTICS</p>
        <h1>数据可视化</h1>
        <span>基于 {{ stats.total }} 条已发布数据，覆盖 {{ stats.universities }} 所高校、{{ stats.provinces }} 个省份、{{ stats.years }} 个年度。</span>
      </div>
    </div>
    <p v-if="loading" class="notice">加载数据中...</p>
    <div class="chart-grid">
      <div class="chart-card"><div id="chart-province" class="chart-box"></div></div>
      <div class="chart-card"><div id="chart-major" class="chart-box"></div></div>
      <div class="chart-card"><div id="chart-year" class="chart-box"></div></div>
      <div class="chart-card"><div id="chart-enrollment" class="chart-box"></div></div>
    </div>
  </section>
</template>
