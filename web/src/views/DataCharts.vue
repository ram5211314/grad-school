<script setup>
import { onMounted, ref, nextTick } from "vue";
import * as echarts from "echarts";

const loading = ref(true);
const stats = ref({ total: 0, universities: 0, provinces: 0, years: 0 });
const catNames = {"01":"哲学","02":"经济学","03":"法学","04":"教育学","05":"文学","06":"历史学","07":"理学","08":"工学","09":"农学","10":"医学","11":"军事学","12":"管理学","13":"艺术学","14":"交叉学科"};

let provinceChart, majorChart, yearChart, enrollmentChart;

async function loadData() {
  loading.value = true;
  try {
    const res = await fetch("/api/v1/programs/stats");
    if (!res.ok) throw new Error();
    const data = await res.json();
    stats.value = { total: data.total, universities: data.universities, provinces: data.provinces.length, years: data.yearStats.length };
    nextTick(() => {
      renderProvince(data.provinces);
      renderMajor(data.majorCategories);
      renderYear(data.yearStats);
      renderEnrollment(data.topUniversities);
    });
  } finally {
    loading.value = false;
  }
}

function renderProvince(data) {
  const el = document.getElementById("chart-province");
  if (!el) return;
  if (provinceChart) provinceChart.dispose();
  provinceChart = echarts.init(el);
  provinceChart.setOption({
    title: { text: "各省份院校专业数量", left: "center" },
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: data.map(x => x[0]), axisLabel: { rotate: 45, fontSize: 11 } },
    yAxis: { type: "value", name: "数量" },
    series: [{ type: "bar", data: data.map(x => x[1]), itemStyle: { color: "#409eff" } }],
    grid: { left: 60, right: 30, bottom: 80, top: 50 },
  });
}

function renderMajor(data) {
  const el = document.getElementById("chart-major");
  if (!el) return;
  if (majorChart) majorChart.dispose();
  majorChart = echarts.init(el);
  const pieData = data.map(x => ({ name: `${x[0]} ${catNames[x[0]] || x[0]}`, value: x[1] }));
  majorChart.setOption({
    title: { text: "学科门类分布", left: "center" },
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    legend: { bottom: 0, type: "scroll" },
    series: [{
      type: "pie", radius: ["35%", "60%"], center: ["50%", "50%"],
      label: { formatter: "{b}\n{d}%" },
      data: pieData,
    }],
  });
}

function renderYear(data) {
  const el = document.getElementById("chart-year");
  if (!el) return;
  if (yearChart) yearChart.dispose();
  yearChart = echarts.init(el);
  const years = data.map(x => String(x[0]));
  const ratioByYear = {};
  data.forEach(x => { if (x[2] && x[3]) ratioByYear[String(x[0])] = +(x[3] / x[2]).toFixed(2); });
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
      { name: "记录数", type: "bar", data: data.map(x => x[1]) },
      { name: "总录取", type: "bar", data: data.map(x => x[2]) },
      { name: "总报名", type: "bar", data: data.map(x => x[3]) },
      { name: "报录比", type: "line", yAxisIndex: 1, data: years.map(y => ratioByYear[y] || null), itemStyle: { color: "#e6a23c" } },
    ],
    grid: { left: 60, right: 60, bottom: 50, top: 50 },
  });
}

function renderEnrollment(data) {
  const el = document.getElementById("chart-enrollment");
  if (!el) return;
  if (enrollmentChart) enrollmentChart.dispose();
  enrollmentChart = echarts.init(el);
  const names = data.map(x => String(x[0]).length > 8 ? String(x[0]).substring(0, 8) + "..." : String(x[0]));
  enrollmentChart.setOption({
    title: { text: "TOP15 高校录取人数", left: "center" },
    tooltip: { trigger: "axis" },
    xAxis: { type: "category", data: names, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: "value", name: "人数" },
    series: [{ type: "bar", data: data.map(x => x[1]), itemStyle: { color: "#67c23a" } }],
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
