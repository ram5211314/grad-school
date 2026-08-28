<template>
  <div class="combo-box" ref="boxRef">
    <div class="combo-input-wrap" @click="open = !open">
      <input
        ref="inputRef"
        v-model="query"
        :placeholder="selectedLabel || placeholder"
        @focus="open = true"
        @input="open = true"
        @keydown="onKeydown"
        class="combo-input"
      />
      <button v-if="modelValue" class="combo-clear" @click.stop="clear">&times;</button>
    </div>
    <div v-if="open && filteredOptions.length" class="combo-dropdown">
      <div
        v-for="(opt, i) in displayedOptions"
        :key="opt.value"
        :class="['combo-option', { active: i === activeIndex }]"
        @mousedown.prevent="select(opt)"
        @mouseenter="activeIndex = i"
      >{{ opt.label }}</div>
      <div v-if="filteredOptions.length > displayLimit" class="combo-more">输入关键词缩小范围（共 {{ filteredOptions.length }} 项）</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue";

const props = defineProps({
  modelValue: { type: String, default: "" },
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: "请选择" }
});
const emit = defineEmits(["update:modelValue", "select"]);

const boxRef = ref(null);
const inputRef = ref(null);
const open = ref(false);
const query = ref("");
const activeIndex = ref(-1);
const displayLimit = 100;

const normalizedOptions = computed(() =>
  props.options.map(o =>
    typeof o === "string" ? { label: o, value: o } : o
  )
);

const selectedLabel = computed(() => {
  const found = normalizedOptions.value.find(o => o.value === props.modelValue);
  return found ? found.label : "";
});

const filteredOptions = computed(() => {
  const q = query.value.trim().toLowerCase();
  if (!q) return normalizedOptions.value;
  return normalizedOptions.value.filter(o => o.label.toLowerCase().includes(q));
});

const displayedOptions = computed(() =>
  filteredOptions.value.slice(0, displayLimit)
);

watch(() => props.modelValue, () => { query.value = ""; activeIndex.value = -1; });

function select(opt) {
  emit("update:modelValue", opt.value);
  emit("select", opt.value);
  query.value = "";
  open.value = false;
  activeIndex.value = -1;
}

function clear() {
  emit("update:modelValue", "");
  emit("select", "");
  query.value = "";
  activeIndex.value = -1;
}

function onKeydown(e) {
  const len = displayedOptions.value.length;
  if (e.key === "ArrowDown") {
    e.preventDefault();
    activeIndex.value = (activeIndex.value + 1) % len;
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    activeIndex.value = (activeIndex.value - 1 + len) % len;
  } else if (e.key === "Enter") {
    e.preventDefault();
    if (activeIndex.value >= 0 && activeIndex.value < len) {
      select(displayedOptions.value[activeIndex.value]);
    }
  } else if (e.key === "Escape") {
    open.value = false;
    activeIndex.value = -1;
  }
}

function onClickOutside(e) {
  if (boxRef.value && !boxRef.value.contains(e.target)) {
    open.value = false;
    activeIndex.value = -1;
  }
}

onMounted(() => document.addEventListener("click", onClickOutside));
onBeforeUnmount(() => document.removeEventListener("click", onClickOutside));
</script>
