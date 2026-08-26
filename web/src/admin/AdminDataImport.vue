<script setup>
import { ref } from "vue";
import { Upload, CheckCircle, XCircle, FileText } from "lucide-vue-next";

const file = ref(null);
const uploading = ref(false);
const result = ref(null);
const error = ref("");
const importHistory = ref([]);

function onFileChange(e) {
  file.value = e.target.files[0];
  result.value = null;
  error.value = "";
}

async function upload() {
  if (!file.value) { error.value = "请选择CSV文件"; return; }
  uploading.value = true;
  error.value = "";
  result.value = null;
  try {
    const fd = new FormData();
    fd.append("file", file.value);
    const res = await fetch("/api/v1/admin/imports/programs", { method: "POST", body: fd });
    if (res.ok) {
      result.value = await res.json();
      importHistory.value.unshift({ ...result.value, time: new Date().toLocaleString() });
    } else {
      const e = await res.json();
      error.value = e.message || "导入失败";
    }
  } catch (e) {
    error.value = "网络错误: " + e.message;
  } finally {
    uploading.value = false;
  }
}
</script>

<template>
  <div class="admin-import">
    <h2>数据导入</h2>
    <div class="import-card">
      <div class="import-area">
        <Upload :size="40" color="#c0c4cc"/>
        <h3>上传CSV文件</h3>
        <p>支持格式：UTF-8编码的CSV文件，首行为表头</p>
        <p class="fields-hint">必填字段：universityName, province, majorCode, majorName, admissionYear</p>
        <input type="file" accept=".csv" @change="onFileChange" ref="fileInput"/>
        <button class="primary" :disabled="uploading || !file" @click="upload">
          {{ uploading ? '导入中...' : '开始导入' }}
        </button>
      </div>
      <p v-if="error" class="error"><XCircle :size="16"/> {{ error }}</p>
      <div v-if="result" class="import-result">
        <CheckCircle :size="20" color="#67c23a"/>
        <div>
          <p><b>导入完成</b></p>
          <p>文件：{{ result.fileName }}</p>
          <p>成功：{{ result.successRows }} 条 | 失败：{{ result.failedRows }} 条</p>
          <p>状态：{{ result.status }}</p>
        </div>
      </div>
    </div>
    <div v-if="importHistory.length" class="import-history">
      <h3>导入历史</h3>
      <table>
        <thead><tr><th>时间</th><th>文件</th><th>成功</th><th>失败</th><th>状态</th></tr></thead>
        <tbody>
          <tr v-for="(h, i) in importHistory" :key="i">
            <td>{{ h.time }}</td>
            <td>{{ h.fileName }}</td>
            <td class="ok">{{ h.successRows }}</td>
            <td :class="{ err: h.failedRows > 0 }">{{ h.failedRows }}</td>
            <td><span class="badge">{{ h.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
