<script setup>
import { ref, onMounted } from "vue";
import { Database, Users, FileText, TrendingUp, CheckCircle, AlertCircle } from "lucide-vue-next";

const stats = ref({ total: 0, universities: 0, provinces: 0, years: 0, published: 0, pending: 0 });
const recentImports = ref([]);
const loading = ref(true);

async function loadDashboard() {
  loading.value = true;
  try {
    const res = await fetch("/api/v1/programs?page=0&pageSize=1");
    if (res.ok) {
      const body = await res.json();
      stats.value.total = body.total;
    }
    const statsRes = await fetch("/api/v1/admin/stats");
    if (statsRes.ok) {
      const s = await statsRes.json();
      Object.assign(stats.value, s);
    }
  } finally {
    loading.value = false;
  }
}

onMounted(loadDashboard);
</script>

<template>
  <div class="admin-dashboard">
    <h2>系统概览</h2>
    <div class="stat-cards">
      <div class="stat-card">
        <div class="stat-icon" style="background:#ecf5ff"><Database :size="24" color="#409eff"/></div>
        <div class="stat-info"><span class="stat-num">{{ stats.total }}</span><span class="stat-label">数据总量</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#f0f9eb"><CheckCircle :size="24" color="#67c23a"/></div>
        <div class="stat-info"><span class="stat-num">{{ stats.published ?? stats.total }}</span><span class="stat-label">已发布</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#fdf6ec"><AlertCircle :size="24" color="#e6a23c"/></div>
        <div class="stat-info"><span class="stat-num">{{ stats.pending ?? 0 }}</span><span class="stat-label">待审核</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#fef0f0"><Users :size="24" color="#f56c6c"/></div>
        <div class="stat-info"><span class="stat-num">{{ stats.users ?? 0 }}</span><span class="stat-label">注册用户</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#ecf5ff"><FileText :size="24" color="#409eff"/></div>
        <div class="stat-info"><span class="stat-num">{{ stats.universities ?? 0 }}</span><span class="stat-label">高校数量</span></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon" style="background:#f0f9eb"><TrendingUp :size="24" color="#67c23a"/></div>
        <div class="stat-info"><span class="stat-num">{{ stats.provinces ?? 0 }}</span><span class="stat-label">覆盖省份</span></div>
      </div>
    </div>
    <div class="dashboard-section">
      <h3>快速操作</h3>
      <div class="quick-actions">
        <button class="action-btn" onclick="location.hash='/admin/data'">管理招生数据</button>
        <button class="action-btn" onclick="location.hash='/admin/import'">导入新数据</button>
        <button class="action-btn" onclick="location.hash='/admin/users'">用户管理</button>
        <button class="action-btn" onclick="location.hash='/admin/logs'">查看日志</button>
      </div>
    </div>
    <div class="dashboard-section">
      <h3>数据说明</h3>
      <p class="info-text">当前数据来源为CPEER开源数据集（649条），覆盖59所高校、15个省份、2020-2023年度。</p>
      <p class="info-text">复试线、计划招生数等字段需从高校官网单独采集，当前大部分显示为"未公开"属正常现象。</p>
    </div>
  </div>
</template>
