<template>
  <div class="restocking">
    <div class="page-header">
      <h2>{{ t('restocking.title') }}</h2>
      <p>{{ t('restocking.description') }}</p>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div v-if="submittedOrder" class="confirmation">
        <div class="confirmation-body">
          <div class="confirmation-title">{{ t('restocking.order.successTitle') }}</div>
          <p class="confirmation-message">
            {{ t('restocking.order.successMessage', { orderNumber: submittedOrder.order_number }) }}
          </p>
          <p class="confirmation-meta">
            {{ t('restocking.order.expectedDelivery') }}: {{ formatDate(submittedOrder.expected_delivery) }}
          </p>
        </div>
        <div class="confirmation-actions">
          <router-link to="/orders" class="btn-link">{{ t('restocking.order.viewOrders') }}</router-link>
          <button type="button" class="btn-quiet" @click="submittedOrder = null">
            {{ t('restocking.order.dismiss') }}
          </button>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('restocking.budget.title') }}</h3>
          <span class="budget-value">{{ formatMoney(budget) }}</span>
        </div>
        <p class="budget-hint">{{ t('restocking.budget.hint') }}</p>
        <input
          type="range"
          class="budget-slider"
          min="0"
          :max="sliderMax"
          step="100"
          v-model.number="budget"
          :aria-label="t('restocking.budget.label')"
        />
        <div class="budget-scale">
          <span>{{ formatMoney(0) }}</span>
          <span>{{ t('restocking.budget.max') }} {{ formatMoney(sliderMax) }}</span>
        </div>
        <div class="budget-remaining">
          {{ t('restocking.budget.unused') }}: <strong>{{ formatMoneyExact(unusedBudget) }}</strong>
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.summary.itemsSelected') }}</div>
          <div class="stat-value">{{ recommendations.length }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">{{ t('restocking.summary.totalUnits') }}</div>
          <div class="stat-value">{{ totalUnits.toLocaleString() }}</div>
        </div>
        <div class="stat-card success">
          <div class="stat-label">{{ t('restocking.summary.totalCost') }}</div>
          <div class="stat-value">{{ formatMoneyExact(totalCost) }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('restocking.summary.unusedBudget') }}</div>
          <div class="stat-value">{{ formatMoneyExact(unusedBudget) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">{{ t('restocking.summary.leadTime') }}</div>
          <div class="stat-value">{{ orderLeadTime }}</div>
          <div class="stat-note">{{ t('restocking.summary.leadTimeHint') }}</div>
          <div class="stat-note" v-if="expectedDelivery">
            {{ t('restocking.summary.expectedDelivery') }}: {{ formatDate(expectedDelivery) }}
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <div>
            <h3 class="card-title">{{ t('restocking.recommendations.title') }}</h3>
            <p class="card-subtitle">{{ t('restocking.recommendations.subtitle') }}</p>
          </div>
        </div>

        <div v-if="recommendations.length === 0" class="empty-state">
          {{ t('restocking.recommendations.empty') }}
        </div>

        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.supplier') }}</th>
                <th>{{ t('restocking.table.trend') }}</th>
                <th class="num">{{ t('restocking.table.currentDemand') }}</th>
                <th class="num">{{ t('restocking.table.forecastDemand') }}</th>
                <th class="num">{{ t('restocking.table.shortfall') }}</th>
                <th class="num">{{ t('restocking.table.quantity') }}</th>
                <th class="num">{{ t('restocking.table.unitCost') }}</th>
                <th class="num">{{ t('restocking.table.lineTotal') }}</th>
                <th class="num">{{ t('restocking.table.leadTime') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="line in recommendations" :key="line.sku">
                <td><strong>{{ line.sku }}</strong></td>
                <td>
                  {{ translateProductName(line.name) }}
                  <span v-if="line.partial" class="partial-badge" :title="t('restocking.recommendations.partialHint')">
                    {{ t('restocking.recommendations.partial') }}
                  </span>
                </td>
                <td>{{ line.supplier }}</td>
                <td>
                  <span class="trend" :style="{ color: trendColor(line.trend) }">
                    <svg
                      class="trend-mark"
                      viewBox="0 0 10 10"
                      width="10"
                      height="10"
                      aria-hidden="true"
                      focusable="false"
                    >
                      <polygon v-if="line.trend === 'increasing'" points="5,1 9,9 1,9" fill="currentColor" />
                      <polygon v-else-if="line.trend === 'decreasing'" points="5,9 1,1 9,1" fill="currentColor" />
                      <rect v-else x="1" y="4" width="8" height="2" fill="currentColor" />
                    </svg>
                    {{ t(`trends.${line.trend}`) }}
                  </span>
                </td>
                <td class="num">{{ line.current_demand.toLocaleString() }}</td>
                <td class="num"><strong>{{ line.forecasted_demand.toLocaleString() }}</strong></td>
                <td class="num">{{ line.shortfall.toLocaleString() }}</td>
                <td class="num"><strong>{{ line.quantity.toLocaleString() }}</strong></td>
                <td class="num">{{ formatMoneyExact(line.unit_cost) }}</td>
                <td class="num">{{ formatMoneyExact(line.line_total) }}</td>
                <td class="num">{{ t('restocking.days', { count: line.lead_time_days }) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="order-actions">
          <button
            type="button"
            class="btn-primary"
            :disabled="recommendations.length === 0 || submitting"
            @click="placeOrder"
          >
            {{ submitting ? t('restocking.order.placing') : t('restocking.order.place') }}
          </button>
          <span v-if="recommendations.length === 0" class="disabled-reason">
            {{ t('restocking.order.disabledReason') }}
          </span>
        </div>

        <div v-if="submitError" class="error">{{ submitError }}</div>
      </div>

      <div class="card excluded-card">
        <div class="card-header">
          <div>
            <h3 class="card-title">{{ t('restocking.excluded.title') }}</h3>
            <p class="card-subtitle">{{ t('restocking.excluded.subtitle') }}</p>
          </div>
        </div>

        <div v-if="excludedItems.length === 0" class="empty-state">
          {{ t('restocking.excluded.empty') }}
        </div>

        <div v-else class="table-container">
          <table>
            <thead>
              <tr>
                <th>{{ t('restocking.table.sku') }}</th>
                <th>{{ t('restocking.table.itemName') }}</th>
                <th>{{ t('restocking.table.supplier') }}</th>
                <th class="num">{{ t('restocking.table.shortfall') }}</th>
                <th class="num">{{ t('restocking.table.unitCost') }}</th>
                <th>{{ t('restocking.excluded.reason') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in excludedItems" :key="item.sku">
                <td><strong>{{ item.sku }}</strong></td>
                <td>{{ translateProductName(item.name) }}</td>
                <td>{{ item.supplier }}</td>
                <td class="num">{{ item.shortfall.toLocaleString() }}</td>
                <td class="num">{{ formatMoneyExact(item.unit_cost) }}</td>
                <td>
                  <span class="reason-pill">{{ t(`restocking.excluded.${item.reasonKey}`) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import { useI18n } from '../composables/useI18n'
import { formatCurrency, formatCurrencyWithDecimals } from '../utils/currency'

export default {
  name: 'Restocking',
  setup() {
    const { t, currentCurrency, currentLocale, translateProductName } = useI18n()

    const forecasts = ref([])
    const loading = ref(true)
    const error = ref(null)
    const budget = ref(0)
    const submitting = ref(false)
    const submitError = ref(null)
    const submittedOrder = ref(null)

    // Forecast items worth restocking: demand is growing, so we are short.
    // Ranked by shortfall descending; unit_cost ascending breaks ties so the
    // ordering is deterministic (cheaper item wins an equal shortfall).
    const rankedShortfalls = computed(() => {
      return forecasts.value
        .map(f => ({
          sku: f.item_sku,
          name: f.item_name,
          supplier: f.supplier,
          trend: f.trend,
          current_demand: f.current_demand,
          forecasted_demand: f.forecasted_demand,
          unit_cost: f.unit_cost,
          lead_time_days: f.lead_time_days,
          shortfall: f.forecasted_demand - f.current_demand
        }))
        .filter(item => item.shortfall > 0)
        .sort((a, b) => b.shortfall - a.shortfall || a.unit_cost - b.unit_cost)
    })

    // Items with flat or falling demand never need restocking.
    const fallingDemandItems = computed(() => {
      return forecasts.value
        .map(f => ({
          sku: f.item_sku,
          name: f.item_name,
          supplier: f.supplier,
          unit_cost: f.unit_cost,
          shortfall: f.forecasted_demand - f.current_demand,
          reasonKey: 'demandFalling'
        }))
        .filter(item => item.shortfall <= 0)
    })

    // Slider ceiling: fully covering every shortfall, plus 25% headroom so the
    // user can overshoot, rounded up to a clean $1,000 step.
    const sliderMax = computed(() => {
      const fullCost = rankedShortfalls.value.reduce(
        (sum, item) => sum + item.shortfall * item.unit_cost,
        0
      )
      return Math.ceil((fullCost * 1.25) / 1000) * 1000
    })

    // Greedy allocation over the ranked list. Recomputed locally on every
    // slider move - the forecast data is fetched once on mount, never per tick.
    const allocation = computed(() => {
      const lines = []
      const skipped = []
      let remaining = budget.value

      for (let i = 0; i < rankedShortfalls.value.length; i++) {
        const item = rankedShortfalls.value[i]
        const fullLineTotal = item.shortfall * item.unit_cost

        if (fullLineTotal <= remaining) {
          lines.push({ ...item, quantity: item.shortfall, line_total: fullLineTotal, partial: false })
          remaining -= fullLineTotal
          continue
        }

        const partialQty = Math.floor(remaining / item.unit_cost)
        if (partialQty >= 1) {
          lines.push({
            ...item,
            quantity: partialQty,
            line_total: partialQty * item.unit_cost,
            partial: true
          })
          remaining -= partialQty * item.unit_cost
        }

        // WHY we stop here instead of continuing down the ranked list: once the
        // budget can no longer cover a whole line, any further iteration would
        // only buy 1-2 units of progressively cheaper items to scrape up the
        // last few dollars. Those trailing micro-lines are noise on a purchase
        // order - a real buyer would not raise a PO for two gaskets. Stopping
        // after the first partial line keeps the order to the items that
        // actually matter and leaves the remainder visible as unused budget.
        for (let j = i + (partialQty >= 1 ? 1 : 0); j < rankedShortfalls.value.length; j++) {
          skipped.push({ ...rankedShortfalls.value[j], reasonKey: 'overBudget' })
        }
        break
      }

      return { lines, skipped, remaining }
    })

    const recommendations = computed(() => allocation.value.lines)

    const excludedItems = computed(() => [
      ...allocation.value.skipped,
      ...fallingDemandItems.value
    ])

    const totalUnits = computed(() =>
      recommendations.value.reduce((sum, line) => sum + line.quantity, 0)
    )

    const totalCost = computed(() =>
      recommendations.value.reduce((sum, line) => sum + line.line_total, 0)
    )

    const unusedBudget = computed(() => Math.max(0, budget.value - totalCost.value))

    // A shipment is complete only when its slowest item lands, so the order
    // lead time is the MAX of the selected lead times, never the sum.
    const maxLeadTimeDays = computed(() => {
      if (recommendations.value.length === 0) return 0
      return Math.max(...recommendations.value.map(line => line.lead_time_days))
    })

    const orderLeadTime = computed(() =>
      t('restocking.days', { count: maxLeadTimeDays.value })
    )

    const expectedDelivery = computed(() => {
      if (recommendations.value.length === 0) return null
      const date = new Date()
      if (isNaN(date.getTime())) return null
      date.setDate(date.getDate() + maxLeadTimeDays.value)
      return date.toISOString()
    })

    const formatMoney = (amount) => formatCurrency(amount, currentCurrency.value)
    const formatMoneyExact = (amount) =>
      formatCurrencyWithDecimals(amount, currentCurrency.value, 2)

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return ''
      const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
      return date.toLocaleDateString(locale, { year: 'numeric', month: 'short', day: 'numeric' })
    }

    const trendColor = (trend) => {
      if (trend === 'increasing') return '#059669'
      if (trend === 'decreasing') return '#dc2626'
      return '#2563eb'
    }

    const loadForecasts = async () => {
      try {
        loading.value = true
        error.value = null
        forecasts.value = await api.getDemandForecasts()
        // Start at half the ceiling so the page opens on a partially funded order.
        budget.value = Math.round(sliderMax.value / 2 / 100) * 100
      } catch (err) {
        error.value = 'Failed to load demand forecasts: ' + err.message
        console.error('Load error:', err)
      } finally {
        loading.value = false
      }
    }

    const placeOrder = async () => {
      if (recommendations.value.length === 0) return
      try {
        submitting.value = true
        submitError.value = null
        submittedOrder.value = null

        const payload = {
          budget: budget.value,
          items: recommendations.value.map(line => ({
            sku: line.sku,
            name: line.name,
            quantity: line.quantity,
            unit_cost: line.unit_cost,
            supplier: line.supplier,
            lead_time_days: line.lead_time_days,
            line_total: line.line_total
          }))
        }

        submittedOrder.value = await api.createRestockOrder(payload)
      } catch (err) {
        // Surface the API's own explanation when it sends one.
        const detail = err.response && err.response.data && err.response.data.detail
        submitError.value = detail || `${t('restocking.order.failed')}: ${err.message}`
        console.error('Restock order error:', err)
      } finally {
        submitting.value = false
      }
    }

    onMounted(loadForecasts)

    return {
      t,
      translateProductName,
      loading,
      error,
      budget,
      sliderMax,
      recommendations,
      excludedItems,
      totalUnits,
      totalCost,
      unusedBudget,
      orderLeadTime,
      expectedDelivery,
      submitting,
      submitError,
      submittedOrder,
      formatMoney,
      formatMoneyExact,
      formatDate,
      trendColor,
      placeOrder
    }
  }
}
</script>

<style scoped>
.card-subtitle {
  font-size: 0.813rem;
  color: #64748b;
  margin-top: 0.25rem;
}

.budget-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.025em;
}

.budget-hint {
  font-size: 0.813rem;
  color: #64748b;
  margin-bottom: 0.875rem;
}

.budget-slider {
  width: 100%;
  appearance: none;
  -webkit-appearance: none;
  height: 6px;
  border-radius: 3px;
  background: #e2e8f0;
  outline: none;
}

.budget-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  border: 2px solid #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
  cursor: pointer;
}

.budget-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #2563eb;
  border: 2px solid #ffffff;
  cursor: pointer;
}

.budget-scale {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.5rem;
}

.budget-remaining {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #f1f5f9;
  font-size: 0.875rem;
  color: #64748b;
}

.budget-remaining strong {
  color: #0f172a;
}

.stat-note {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.375rem;
}

.stat-card .stat-value {
  font-size: 1.75rem;
}

td.num,
th.num {
  text-align: right;
}

.trend {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.813rem;
  font-weight: 600;
}

.trend-mark {
  flex-shrink: 0;
}

.partial-badge {
  display: inline-block;
  margin-left: 0.5rem;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #64748b;
  font-size: 0.688rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.reason-pill {
  display: inline-block;
  padding: 0.188rem 0.625rem;
  border-radius: 6px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 600;
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: #64748b;
  font-size: 0.875rem;
  background: #f8fafc;
  border: 1px dashed #e2e8f0;
  border-radius: 8px;
}

.order-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 1.25rem;
  padding-top: 1.25rem;
  border-top: 1px solid #f1f5f9;
}

.btn-primary {
  background: #2563eb;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  padding: 0.625rem 1.5rem;
  font-size: 0.938rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  background: #1d4ed8;
}

.btn-primary:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.disabled-reason {
  font-size: 0.875rem;
  color: #64748b;
}

.excluded-card {
  background: #fbfcfd;
}

.confirmation {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
  background: #ecfdf5;
  border: 1px solid #a7f3d0;
  border-radius: 10px;
  padding: 1.25rem;
  margin-bottom: 1.25rem;
}

.confirmation-title {
  font-size: 1rem;
  font-weight: 700;
  color: #065f46;
  margin-bottom: 0.375rem;
}

.confirmation-message,
.confirmation-meta {
  font-size: 0.875rem;
  color: #047857;
}

.confirmation-meta {
  margin-top: 0.25rem;
}

.confirmation-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-link {
  background: #059669;
  color: #ffffff;
  text-decoration: none;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.btn-link:hover {
  background: #047857;
}

.btn-quiet {
  background: transparent;
  border: 1px solid #a7f3d0;
  color: #047857;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-quiet:hover {
  background: #d1fae5;
}
</style>
