<script setup>
import { ref, onMounted } from "vue";
import { Bookmark, Trash2, ExternalLink, ArrowRight } from "lucide-vue-next";

const favorites = ref([]);

function load() {
  favorites.value = JSON.parse(localStorage.getItem("shortlist") || "[]");
}

function remove(id) {
  favorites.value = favorites.value.filter(p => p.id !== id);
  localStorage.setItem("shortlist", JSON.stringify(favorites.value));
}

function goSearch() { location.hash = "/programs"; }

function ratio(p) {
  return p.registrationCount && p.actualEnrollment
    ? `${(p.registrationCount / p.actualEnrollment).toFixed(1)} : 1`
    : "未公开";
}

onMounted(load);
</script>

<template>
  <div class="user-favorites">
    <h2>我的收藏 <small>{{ favorites.length }} / 5</small></h2>
    <p class="hint">收藏的院校专业会自动用于择校建议生成。最多保存5个。</p>
    <div v-if="!favorites.length" class="empty-state">
      <Bookmark :size="48" color="#c0c4cc"/>
      <p>还没有收藏任何院校</p>
      <button class="primary" @click="goSearch">去检索 <ArrowRight :size="16"/></button>
    </div>
    <div v-else class="fav-grid">
      <article v-for="p in favorites" :key="p.id" class="fav-card">
        <div class="fav-head">
          <span class="badge">{{ p.majorCode }}</span>
          <button class="icon danger" @click="remove(p.id)" title="移除"><Trash2 :size="16"/></button>
        </div>
        <h3>{{ p.universityName }}</h3>
        <p class="major">{{ p.majorName }}</p>
        <div class="fav-tags">
          <span>{{ p.province }}</span>
          <span>{{ p.admissionYear }}年</span>
          <span>{{ p.studyMode === 'FULL_TIME' ? '全日制' : p.studyMode }}</span>
        </div>
        <dl>
          <div><dt>复试线</dt><dd>{{ p.reexaminationLine ?? '未公开' }}</dd></div>
          <div><dt>录取</dt><dd>{{ p.actualEnrollment ?? '-' }}</dd></div>
          <div><dt>报录比</dt><dd>{{ ratio(p) }}</dd></div>
        </dl>
        <footer>
          <span>{{ p.sourceName || '来源待补充' }}</span>
          <a v-if="p.sourceUrl" :href="p.sourceUrl" target="_blank">来源链接 <ExternalLink :size="12"/></a>
        </footer>
      </article>
    </div>
  </div>
</template>
