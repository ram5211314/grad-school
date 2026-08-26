<script setup>
import { ref } from "vue";
import { User, Lock, GraduationCap, Eye, EyeOff } from "lucide-vue-next";

const isLogin = ref(true);
const form = ref({ username: "", password: "", email: "" });
const showPwd = ref(false);
const error = ref("");
const loading = ref(false);
const emit = defineEmits(["login"]);

async function handleSubmit() {
  error.value = "";
  if (!form.value.username || !form.value.password) { error.value = "请填写用户名和密码"; return; }
  if (!isLogin.value && !form.value.email) { error.value = "请填写邮箱"; return; }
  loading.value = true;
  try {
    const url = isLogin.value ? "/api/v1/auth/login" : "/api/v1/auth/register";
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form.value)
    });
    const data = await res.json();
    if (res.ok) {
      localStorage.setItem("token", data.token);
      localStorage.setItem("user", JSON.stringify(data.user));
      emit("login", data.user);
    } else {
      error.value = data.message || "操作失败";
    }
  } catch (e) {
    error.value = "网络错误，请检查后端服务";
  } finally {
    loading.value = false;
  }
}

function fillDemo(role) {
  form.value.username = role === "admin" ? "admin" : "student";
  form.value.password = "123456";
  form.value.email = role === "admin" ? "admin@grad.cn" : "stu@grad.cn";
}
</script>

<template>
  <div class="login-page">
    <div class="login-bg"></div>
    <div class="login-card">
      <div class="login-header">
        <div class="logo"><GraduationCap :size="32" color="#409eff"/></div>
        <h1>计算机考研择校平台</h1>
        <p>{{ isLogin ? '欢迎回来，请登录您的账号' : '创建新账号' }}</p>
      </div>
      <form class="login-form" @submit.prevent="handleSubmit">
        <div class="input-group">
          <User :size="18" color="#909399"/>
          <input v-model="form.username" placeholder="用户名" required/>
        </div>
        <div class="input-group" v-if="!isLogin">
          <span style="width:18px;text-align:center;color:#909399;font-size:13px">@</span>
          <input v-model="form.email" type="email" placeholder="邮箱"/>
        </div>
        <div class="input-group">
          <Lock :size="18" color="#909399"/>
          <input v-model="form.password" :type="showPwd ? 'text' : 'password'" placeholder="密码" required/>
          <button type="button" class="eye-btn" @click="showPwd = !showPwd"><component :is="showPwd ? EyeOff : Eye" :size="16"/></button>
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button class="login-btn" type="submit" :disabled="loading">{{ loading ? '处理中...' : (isLogin ? '登 录' : '注 册') }}</button>
      </form>
      <div class="login-footer">
        <span>{{ isLogin ? '还没有账号？' : '已有账号？' }}</span>
        <button class="link-btn" @click="isLogin = !isLogin; error = ''">{{ isLogin ? '立即注册' : '去登录' }}</button>
      </div>
      <div class="demo-accounts">
        <p>演示账号（点击自动填充）：</p>
        <div class="demo-btns">
          <button @click="fillDemo('admin')">管理员 admin</button>
          <button @click="fillDemo('user')">普通用户 student</button>
        </div>
      </div>
    </div>
  </div>
</template>
