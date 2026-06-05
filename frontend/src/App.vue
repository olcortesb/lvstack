<template>
  <div class="min-h-screen bg-gray-950 text-white p-6">
    <header class="max-w-6xl mx-auto mb-8">
      <h1 class="text-3xl font-bold">lvstack</h1>
      <p class="text-gray-400 text-sm mt-1">Local AWS services dashboard</p>
      <div class="flex items-center gap-4 mt-3">
        <span v-if="health" class="text-xs px-2 py-1 rounded-full bg-green-900 text-green-300">
          {{ health.edition }} · v{{ health.version }}
        </span>
        <span v-if="health" class="text-xs text-gray-500">
          {{ Object.keys(health.services).length }} services running
        </span>
        <span v-if="error" class="text-xs px-2 py-1 rounded-full bg-red-900 text-red-300">
          {{ error }}
        </span>
      </div>
    </header>

    <main v-if="health" class="max-w-6xl mx-auto">
      <!-- Category filter -->
      <div class="flex flex-wrap gap-2 mb-6">
        <button
          v-for="cat in categories"
          :key="cat"
          @click="activeCategory = activeCategory === cat ? null : cat"
          class="text-xs px-3 py-1 rounded-full border transition-colors"
          :class="activeCategory === cat ? 'bg-white text-gray-900 border-white' : 'border-gray-700 text-gray-400 hover:border-gray-500'"
        >
          {{ cat }} ({{ countByCategory(cat) }})
        </button>
      </div>

      <!-- Services grid -->
      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
        <div
          v-for="[id, status] in filteredServices"
          :key="id"
          class="bg-gray-900 border border-gray-800 rounded-xl p-4 hover:border-gray-600 transition-colors"
        >
          <div class="text-2xl mb-2">{{ getMeta(id).icon }}</div>
          <div class="text-sm font-medium text-gray-200">{{ getMeta(id).name }}</div>
          <div class="flex items-center gap-1 mt-2">
            <span class="w-2 h-2 rounded-full" :class="status === 'available' || status === 'running' ? 'bg-green-500' : 'bg-yellow-500'"></span>
            <span class="text-xs text-gray-500">{{ status }}</span>
          </div>
        </div>
      </div>
    </main>

    <div v-else-if="!error" class="text-center text-gray-500 py-20">
      Connecting to health endpoint...
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { SERVICE_META, CATEGORIES } from './data/services.js'

const health = ref(null)
const error = ref(null)
const activeCategory = ref(null)
let pollInterval = null

const ENDPOINTS = [
  { path: '/_ministack/health', name: 'MiniStack' },
  { path: '/_localstack/health', name: 'LocalStack/Floci' },
  { path: '/_robotocore/health', name: 'RobotoCore' },
]

async function fetchHealth() {
  for (const ep of ENDPOINTS) {
    try {
      const resp = await fetch(ep.path)
      if (resp.ok) {
        health.value = await resp.json()
        error.value = null
        return
      }
    } catch {}
  }
  health.value = null
  error.value = 'No local stack running on port 4566/4569'
}

onMounted(() => {
  fetchHealth()
  pollInterval = setInterval(fetchHealth, 5000)
})

onUnmounted(() => {
  clearInterval(pollInterval)
})

function getMeta(id) {
  return SERVICE_META[id] || { name: id, icon: '☁️', category: 'Other' }
}

function countByCategory(cat) {
  if (!health.value) return 0
  return Object.keys(health.value.services).filter(id => getMeta(id).category === cat).length
}

const categories = computed(() => {
  if (!health.value) return []
  const cats = new Set(Object.keys(health.value.services).map(id => getMeta(id).category))
  return CATEGORIES.filter(c => cats.has(c))
})

const filteredServices = computed(() => {
  if (!health.value) return []
  const entries = Object.entries(health.value.services)
  if (!activeCategory.value) return entries
  return entries.filter(([id]) => getMeta(id).category === activeCategory.value)
})
</script>
