<script setup>
import { ref, onMounted } from "vue";
import { Users, Shield, Search } from "lucide-vue-next";

const users = ref([]);
const total = ref(0);
const page = ref(0);
const loading = ref(false);
const msg = ref("");

async function load() {
  loading.value = true;
  try {
    const res = await fetch(`/api/v1/admin/users?page=${page.value}&pageSize=15`);
    if (res.ok) {
      const body = await res.json();
      users.value = body.items || [];
      total.value = body.total || 0;
    }
  } finally {
    loading.value = false;
  }
}

async function toggleRole(user) {
  const newRole = user.role === "ADMIN" ? "USER" : "ADMIN";
  const res = await fetch(`/api/v1/admin/users/${user.id}/role`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role: newRole })
  });
  if (res.ok) { user.role = newRole; msg.value = "角色已更新"; }
}

async function toggleStatus(user) {
  const newStatus = user.status === "ACTIVE" ? "DISABLED" : "ACTIVE";
  const res = await fetch(`/api/v1/admin/users/${user.id}/status`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status: newStatus })
  });
  if (res.ok) { user.status = newStatus; msg.value = "状态已更新"; }
}

onMounted(load);
</script>

<template>
  <div class="admin-users">
    <h2>用户管理 <small>{{ total }} 人</small></h2>
    <p v-if="msg" class="msg">{{ msg }}</p>
    <div class="table-wrap">
      <table>
        <thead><tr><th>ID</th><th>用户名</th><th>邮箱</th><th>角色</th><th>状态</th><th>注册时间</th><th>操作</th></tr></thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td>{{ u.id }}</td>
            <td>{{ u.username }}</td>
            <td>{{ u.email || '-' }}</td>
            <td><span :class="['badge', u.role === 'ADMIN' ? 'admin' : 'user']">{{ u.role === 'ADMIN' ? '管理员' : '普通用户' }}</span></td>
            <td><span :class="['badge', u.status === 'ACTIVE' ? 'active' : 'disabled']">{{ u.status === 'ACTIVE' ? '正常' : '禁用' }}</span></td>
            <td>{{ u.createdAt || '-' }}</td>
            <td class="actions">
              <button class="icon" :title="u.role === 'ADMIN' ? '设为用户' : '设为管理员'" @click="toggleRole(u)"><Shield :size="15"/></button>
              <button class="icon" :title="u.status === 'ACTIVE' ? '禁用' : '启用'" @click="toggleStatus(u)"><Users :size="15"/></button>
            </td>
          </tr>
          <tr v-if="!users.length"><td colspan="7" class="empty-row">暂无用户数据（需要先实现注册/登录功能）</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
