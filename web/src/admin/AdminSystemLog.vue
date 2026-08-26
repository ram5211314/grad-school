<script setup>
import { ref, onMounted } from "vue";
import { FileText, RefreshLeft } from "lucide-vue-next";

const logs = ref([]);
const total = ref(0);
const page = ref(0);
const loading = ref(false);

async function load() {
  loading.value = true;
  try {
    const res = await fetch(`/api/v1/admin/logs?page=${page.value}&pageSize=20`);
    if (res.ok) {
      const body = await res.json();
      logs.value = body.items || [];
      total.value = body.total || 0;
    }
  } finally {
    loading.value = false;
  }
}

function levelColor(level) {
  return { INFO: "#67c23a", WARN: "#e6a23c", ERROR: "#f56c6c", DEBUG: "#909399" }[level] || "#909399";
}

onMounted(load);
</script>

<template>
  <div class="admin-logs">
    <div class="section-header">
      <h2>系统日志 <small>{{ total }} 条</small></h2>
      <button class="plain" @click="load"><RefreshLeft :size="16"/> 刷新</button>
    </div>
    <div class="table-wrap">
      <table>
        <thead><tr><th>时间</th><th>级别</th><th>模块</th><th>操作人</th><th>内容</th><th>IP</th></tr></thead>
        <tbody>
          <tr v-for="(l, i) in logs" :key="i">
            <td>{{ l.createdAt || '-' }}</td>
            <td><span class="badge" :style="{ color: levelColor(l.level), borderColor: levelColor(l.level) }">{{ l.level }}</span></td>
            <td>{{ l.module || '-' }}</td>
            <td>{{ l.operator || '系统' }}</td>
            <td class="log-msg">{{ l.message }}</td>
            <td>{{ l.ip || '-' }}</td>
          </tr>
          <tr v-if="!logs.length"><td colspan="6" class="empty-row">暂无日志记录</td></tr>
        </tbody>
      </table>
    </div>
    <div class="pager" v-if="total > 20">
      <button :disabled="page===0" @click="page--;load()">上一页</button>
      <span>第 {{ page+1 }} 页</span>
      <button :disabled="(page+1)*20>=total" @click="page++;load()">下一页</button>
    </div>
  </div>
</template>
