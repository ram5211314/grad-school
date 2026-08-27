<script setup>
import { ref, onMounted } from "vue";
import { User, Mail, GraduationCap, MapPin, Star, Edit } from "lucide-vue-next";

const profile = ref({
  username: "考研学生",
  email: "",
  undergraduateMajor: "",
  targetMajor: "",
  preferredProvinces: "",
  estimatedScore: 350,
  riskPreference: "BALANCED",
});
const editing = ref(false);
const msg = ref("");
const stats = ref({ favorites: 0, comparisons: 0 });
const allMajors = ref([]);

function load() {
  const saved = localStorage.getItem("userProfile");
  if (saved) Object.assign(profile.value, JSON.parse(saved));
  const favs = JSON.parse(localStorage.getItem("shortlist") || "[]");
  stats.value.favorites = favs.length;
  fetch("/api/v1/majors").then(r => r.json()).then(d => allMajors.value = d).catch(() => {});
}

function save() {
  localStorage.setItem("userProfile", JSON.stringify(profile.value));
  editing.value = false;
  msg.value = "保存成功";
  setTimeout(() => msg.value = "", 2000);
}

onMounted(load);
</script>

<template>
  <div class="user-profile">
    <h2>个人中心</h2>
    <p v-if="msg" class="msg">{{ msg }}</p>
    <div class="profile-layout">
      <div class="profile-card">
        <div class="avatar"><User :size="40" color="#409eff"/></div>
        <h3>{{ profile.username }}</h3>
        <p>{{ profile.email || '未设置邮箱' }}</p>
        <div class="profile-stats">
          <div><span class="num">{{ stats.favorites }}</span><span>对比清单</span></div>
          <div><span class="num">{{ profile.estimatedScore }}</span><span>预估分数</span></div>
        </div>
        <button class="primary" @click="editing = true"><Edit :size="16"/> 编辑资料</button>
      </div>
      <div class="profile-form">
        <h3>学生画像</h3>
        <div class="form-grid">
          <label>用户名<input v-model="profile.username" :disabled="!editing"/></label>
          <label>邮箱<input v-model="profile.email" :disabled="!editing" type="email"/></label>
          <label>本科专业<input v-model="profile.undergraduateMajor" :disabled="!editing" placeholder="如：计算机科学与技术"/></label>
          <label>目标方向<select v-model="profile.targetMajor" :disabled="!editing"><option value="">请选择专业</option><option v-for="m in allMajors" :key="m.code" :value="m.code">{{ m.code }} {{ m.name }}</option></select></label>
          <label>目标省份<input v-model="profile.preferredProvinces" :disabled="!editing" placeholder="江苏,浙江"/></label>
          <label>预估初试分<input v-model.number="profile.estimatedScore" :disabled="!editing" type="number"/></label>
          <label>风险偏好<select v-model="profile.riskPreference" :disabled="!editing"><option value="CONSERVATIVE">保守</option><option value="BALANCED">平衡</option><option value="AGGRESSIVE">进取</option></select></label>
        </div>
        <div class="form-actions" v-if="editing">
          <button class="plain" @click="editing = false">取消</button>
          <button class="primary" @click="save">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>
