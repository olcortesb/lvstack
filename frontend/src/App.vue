<template>
  <div class="min-h-screen bg-gray-950 text-white p-6">
    <header class="max-w-6xl mx-auto mb-8">
      <h1 class="text-3xl font-bold">lvstack</h1>
      <p class="text-gray-400 text-sm mt-1">Local AWS services dashboard</p>
    </header>

    <main class="max-w-6xl mx-auto">
      <!-- Stack selector -->
      <div class="flex gap-4 mb-8">
        <button
          v-for="stack in stacks"
          :key="stack.id"
          @click="selectStack(stack)"
          class="flex items-center gap-3 px-5 py-3 rounded-xl border transition-all"
          :class="activeStack?.id === stack.id
            ? 'bg-gray-800 border-white'
            : stack.online
              ? 'bg-gray-900 border-gray-700 hover:border-gray-500'
              : 'bg-gray-900 border-gray-800 opacity-50'"
        >
          <span class="w-3 h-3 rounded-full" :class="stack.online ? 'bg-green-500' : 'bg-gray-600'"></span>
          <div class="text-left">
            <div class="font-medium text-sm">{{ stack.name }}</div>
            <div class="text-xs text-gray-500" v-if="stack.online">v{{ stack.version }} · {{ stack.serviceCount }} services</div>
            <div class="text-xs text-gray-500" v-else>offline</div>
          </div>
        </button>
      </div>

      <!-- Services grid -->
      <div v-if="activeStack && services">
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

        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-3">
          <div
            v-for="[id, status] in filteredServices"
            :key="id"
            @click="selectService(id)"
            class="bg-gray-900 border rounded-xl p-4 transition-colors cursor-pointer"
            :class="activeService === id ? 'border-white' : 'border-gray-800 hover:border-gray-600'"
          >
            <div class="text-2xl mb-2">{{ getMeta(id).icon }}</div>
            <div class="text-sm font-medium text-gray-200">{{ getMeta(id).name }}</div>
            <div class="flex items-center gap-1 mt-2">
              <span class="w-2 h-2 rounded-full" :class="getStatus(status) === 'available' || getStatus(status) === 'running' ? 'bg-green-500' : 'bg-yellow-500'"></span>
              <span class="text-xs text-gray-500">{{ getStatus(status) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!stacks.length" class="text-center text-gray-500 py-20">
        Connecting to backend...
      </div>

      <div v-else class="text-center text-gray-500 py-20">
        Select a stack above to view services
      </div>

      <!-- Service detail panel -->
      <div v-if="activeService && serviceData" class="mt-8 bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="font-semibold text-lg">{{ getMeta(activeService).icon }} {{ getMeta(activeService).name }}</h2>
          <button @click="activeService = null; serviceData = null" class="text-gray-500 hover:text-white text-sm">✕ Close</button>
        </div>

        <!-- S3 Buckets -->
        <div v-if="activeService === 's3'">
          <div v-if="serviceData.buckets && serviceData.buckets.length" class="space-y-2">
            <div v-for="bucket in serviceData.buckets" :key="bucket.name" class="flex justify-between items-center bg-gray-800 rounded-lg px-4 py-3">
              <div class="flex items-center gap-2">
                <span class="text-lg">🪣</span>
                <span class="text-sm font-medium">{{ bucket.name }}</span>
              </div>
              <span class="text-xs text-gray-500">{{ formatDate(bucket.created) }}</span>
            </div>
          </div>
          <div v-else class="text-gray-500 text-sm">No buckets found</div>
        </div>

        <!-- Other services -->
        <div v-else class="text-gray-500 text-sm">Service inspection not yet available</div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { SERVICE_META, CATEGORIES } from './data/services.js'

const stacks = ref([])
const activeStack = ref(null)
const services = ref(null)
const activeCategory = ref(null)
const activeService = ref(null)
const serviceData = ref(null)
let pollInterval = null

async function fetchStacks() {
  try {
    const resp = await fetch('/api/stacks')
    if (resp.ok) stacks.value = await resp.json()
  } catch {}
}

async function selectStack(stack) {
  if (!stack.online) return
  activeStack.value = stack
  activeCategory.value = null
  try {
    const resp = await fetch(`/api/stacks/${stack.id}/services`)
    if (resp.ok) {
      const data = await resp.json()
      services.value = data.services || {}
    }
  } catch {
    services.value = null
  }
}

async function selectService(id) {
  if (activeService.value === id) {
    activeService.value = null
    serviceData.value = null
    return
  }
  activeService.value = id
  serviceData.value = null

  const stackId = activeStack.value.id
  const endpoints = { s3: `/api/stacks/${stackId}/s3/buckets` }
  const url = endpoints[id]
  if (!url) {
    serviceData.value = { unsupported: true }
    return
  }
  try {
    const resp = await fetch(url)
    if (resp.ok) serviceData.value = await resp.json()
  } catch {
    serviceData.value = { error: 'Failed to fetch' }
  }
}

function formatDate(iso) {
  if (!iso) return ''
  return iso.split('T')[0]
}

function getStatus(status) {
  if (typeof status === 'object') return status.status || 'unknown'
  return status
}

function getMeta(id) {
  return SERVICE_META[id] || { name: id, icon: '☁️', category: 'Other' }
}

function countByCategory(cat) {
  if (!services.value) return 0
  return Object.keys(services.value).filter(id => getMeta(id).category === cat).length
}

const categories = computed(() => {
  if (!services.value) return []
  const cats = new Set(Object.keys(services.value).map(id => getMeta(id).category))
  return CATEGORIES.filter(c => cats.has(c))
})

const filteredServices = computed(() => {
  if (!services.value) return []
  const entries = Object.entries(services.value)
  if (!activeCategory.value) return entries
  return entries.filter(([id]) => getMeta(id).category === activeCategory.value)
})

onMounted(() => {
  fetchStacks()
  pollInterval = setInterval(fetchStacks, 5000)
})

onUnmounted(() => {
  clearInterval(pollInterval)
})
</script>
