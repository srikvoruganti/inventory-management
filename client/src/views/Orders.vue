<template>
  <div class="orders">
    <div class="page-header">
      <h2>{{ t('orders.title') }}</h2>
      <p>{{ t('orders.description') }}</p>
    </div>

    <div class="card submitted-card">
      <div class="card-header">
        <div>
          <h3 class="card-title">{{ t('orders.submitted.title') }}</h3>
          <p class="card-subtitle">{{ t('orders.submitted.subtitle') }}</p>
        </div>
      </div>

      <div v-if="restockLoading" class="loading">{{ t('common.loading') }}</div>
      <div v-else-if="restockError" class="error">{{ restockError }}</div>
      <div v-else-if="restockOrders.length === 0" class="empty-state">
        {{ t('orders.submitted.empty') }}
      </div>
      <div v-else class="submitted-list">
        <div v-for="order in restockOrders" :key="order.id" class="submitted-order">
          <div class="submitted-summary">
            <div class="submitted-identity">
              <span class="submitted-number">{{ order.order_number }}</span>
              <span class="badge info">{{ t('orders.submitted.status') }}</span>
            </div>
            <div class="submitted-facts">
              <div class="fact">
                <span class="fact-label">{{ t('orders.submitted.submittedDate') }}</span>
                <span class="fact-value">{{ formatDate(order.submitted_date) }}</span>
              </div>
              <div class="fact">
                <span class="fact-label">{{ t('orders.submitted.itemCount') }}</span>
                <span class="fact-value">{{ order.item_count }}</span>
              </div>
              <div class="fact">
                <span class="fact-label">{{ t('orders.submitted.totalValue') }}</span>
                <span class="fact-value">{{ formatMoney(order.total_value) }}</span>
              </div>
              <div class="fact fact-lead">
                <span class="fact-label">{{ t('orders.submitted.leadTime') }}</span>
                <span class="fact-value lead-value">
                  {{ t('orders.submitted.days', { count: order.lead_time_days }) }}
                </span>
                <span class="fact-note">
                  {{ t('orders.submitted.expectedDelivery') }}: {{ formatDate(order.expected_delivery) }}
                </span>
              </div>
            </div>
            <button type="button" class="expand-toggle" @click="toggleRestockOrder(order.id)">
              {{ expandedRestockId === order.id ? t('orders.submitted.hideItems') : t('orders.submitted.viewItems') }}
            </button>
          </div>

          <div v-if="expandedRestockId === order.id" class="submitted-items">
            <table>
              <thead>
                <tr>
                  <th>{{ t('orders.submitted.lineItems.sku') }}</th>
                  <th>{{ t('orders.submitted.lineItems.name') }}</th>
                  <th>{{ t('orders.submitted.lineItems.supplier') }}</th>
                  <th class="num">{{ t('orders.submitted.lineItems.quantity') }}</th>
                  <th class="num">{{ t('orders.submitted.lineItems.unitCost') }}</th>
                  <th class="num">{{ t('orders.submitted.lineItems.leadTime') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in order.items" :key="`${order.id}-${item.sku}`">
                  <td><strong>{{ item.sku }}</strong></td>
                  <td>{{ translateProductName(item.name) }}</td>
                  <td>{{ item.supplier }}</td>
                  <td class="num">{{ item.quantity.toLocaleString() }}</td>
                  <td class="num">{{ formatMoney(item.unit_cost) }}</td>
                  <td class="num">{{ t('orders.submitted.days', { count: item.lead_time_days }) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
      <div class="stats-grid">
        <div class="stat-card success">
          <div class="stat-label">{{ t('status.delivered') }}</div>
          <div class="stat-value">{{ getOrdersByStatus('Delivered').length }}</div>
        </div>
        <div class="stat-card info">
          <div class="stat-label">{{ t('status.shipped') }}</div>
          <div class="stat-value">{{ getOrdersByStatus('Shipped').length }}</div>
        </div>
        <div class="stat-card warning">
          <div class="stat-label">{{ t('status.processing') }}</div>
          <div class="stat-value">{{ getOrdersByStatus('Processing').length }}</div>
        </div>
        <div class="stat-card danger">
          <div class="stat-label">{{ t('status.backordered') }}</div>
          <div class="stat-value">{{ getOrdersByStatus('Backordered').length }}</div>
        </div>
      </div>

      <div class="card">
        <div class="card-header">
          <h3 class="card-title">{{ t('orders.allOrders') }} ({{ orders.length }})</h3>
        </div>
        <div class="table-container">
          <table class="orders-table">
            <thead>
              <tr>
                <th class="col-order-number">{{ t('orders.table.orderNumber') }}</th>
                <th class="col-customer">{{ t('orders.table.customer') }}</th>
                <th class="col-items">{{ t('orders.table.items') }}</th>
                <th class="col-status">{{ t('orders.table.status') }}</th>
                <th class="col-date">{{ t('orders.table.orderDate') }}</th>
                <th class="col-date">{{ t('orders.table.expectedDelivery') }}</th>
                <th class="col-value">{{ t('orders.table.totalValue') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="order in orders" :key="order.id">
                <td class="col-order-number"><strong>{{ order.order_number }}</strong></td>
                <td class="col-customer">{{ translateCustomerName(order.customer) }}</td>
                <td class="col-items">
                  <details class="items-details">
                    <summary class="items-summary">
                      {{ t('orders.itemsCount', { count: order.items.length }) }}
                    </summary>
                    <div class="items-dropdown">
                      <div v-for="(item, idx) in order.items" :key="idx" class="item-entry">
                        <span class="item-name">{{ translateProductName(item.name) }}</span>
                        <span class="item-meta">{{ t('orders.quantity') }}: {{ item.quantity }} @ {{ currencySymbol }}{{ item.unit_price }}</span>
                      </div>
                    </div>
                  </details>
                </td>
                <td class="col-status">
                  <span :class="['badge', getOrderStatusClass(order.status)]">
                    {{ t(`status.${order.status.toLowerCase()}`) }}
                  </span>
                </td>
                <td class="col-date">{{ formatDate(order.order_date) }}</td>
                <td class="col-date">{{ formatDate(order.expected_delivery) }}</td>
                <td class="col-value"><strong>{{ currencySymbol }}{{ order.total_value.toLocaleString() }}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, computed } from 'vue'
import { api } from '../api'
import { useFilters } from '../composables/useFilters'
import { useI18n } from '../composables/useI18n'
import { formatCurrencyWithDecimals } from '../utils/currency'

export default {
  name: 'Orders',
  setup() {
    const { t, currentCurrency, translateProductName, translateCustomerName } = useI18n()

    const currencySymbol = computed(() => {
      return currentCurrency.value === 'JPY' ? '¥' : '$'
    })
    const loading = ref(true)
    const error = ref(null)
    const orders = ref([])

    // Restock orders submitted from the Restocking view. Loaded separately so a
    // failure here never blocks the customer orders table below.
    const restockOrders = ref([])
    const restockLoading = ref(true)
    const restockError = ref(null)
    const expandedRestockId = ref(null)

    // Use shared filters
    const {
      selectedPeriod,
      selectedLocation,
      selectedCategory,
      selectedStatus,
      getCurrentFilters
    } = useFilters()

    const loadOrders = async () => {
      try {
        loading.value = true
        const filters = getCurrentFilters()
        const fetchedOrders = await api.getOrders(filters)

        // Sort orders by order_date (earliest first)
        orders.value = fetchedOrders.sort((a, b) => {
          const dateA = new Date(a.order_date)
          const dateB = new Date(b.order_date)
          return dateA - dateB
        })
      } catch (err) {
        error.value = 'Failed to load orders: ' + err.message
      } finally {
        loading.value = false
      }
    }

    // Watch for filter changes and reload data
    watch([selectedPeriod, selectedLocation, selectedCategory, selectedStatus], () => {
      loadOrders()
    })

    const getOrdersByStatus = (status) => {
      return orders.value.filter(order => order.status === status)
    }

    const getOrderStatusClass = (status) => {
      const statusMap = {
        'Delivered': 'success',
        'Shipped': 'info',
        'Processing': 'warning',
        'Backordered': 'danger'
      }
      return statusMap[status] || 'info'
    }

    const formatDate = (dateString) => {
      const { currentLocale } = useI18n()
      const locale = currentLocale.value === 'ja' ? 'ja-JP' : 'en-US'
      return new Date(dateString).toLocaleDateString(locale, {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const formatMoney = (amount) =>
      formatCurrencyWithDecimals(amount, currentCurrency.value, 2)

    const loadRestockOrders = async () => {
      try {
        restockLoading.value = true
        restockError.value = null
        // API already returns these newest-first, so no client-side sorting.
        restockOrders.value = await api.getRestockOrders()
      } catch (err) {
        restockError.value = `${t('orders.submitted.loadError')}: ${err.message}`
        console.error('Restock orders load error:', err)
      } finally {
        restockLoading.value = false
      }
    }

    const toggleRestockOrder = (orderId) => {
      expandedRestockId.value = expandedRestockId.value === orderId ? null : orderId
    }

    onMounted(() => {
      loadOrders()
      loadRestockOrders()
    })

    return {
      t,
      loading,
      error,
      orders,
      restockOrders,
      restockLoading,
      restockError,
      expandedRestockId,
      toggleRestockOrder,
      getOrdersByStatus,
      getOrderStatusClass,
      formatDate,
      formatMoney,
      currencySymbol,
      translateProductName,
      translateCustomerName
    }
  }
}
</script>

<style scoped>
/* Submitted restock orders */
.card-subtitle {
  font-size: 0.813rem;
  color: #64748b;
  margin-top: 0.25rem;
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

.submitted-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.submitted-order {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.submitted-summary {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
  padding: 1rem 1.25rem;
  background: #ffffff;
}

.submitted-identity {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 220px;
}

.submitted-number {
  font-size: 0.938rem;
  font-weight: 700;
  color: #0f172a;
}

.submitted-facts {
  display: flex;
  align-items: flex-start;
  gap: 2rem;
  flex-wrap: wrap;
  flex: 1;
}

.fact {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.fact-label {
  font-size: 0.688rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.fact-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #0f172a;
}

.fact-lead .lead-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2563eb;
}

.fact-note {
  font-size: 0.75rem;
  color: #64748b;
}

.expand-toggle {
  background: transparent;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 0.438rem 0.875rem;
  font-size: 0.813rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s ease;
}

.expand-toggle:hover {
  border-color: #cbd5e1;
  background: #f8fafc;
  color: #0f172a;
}

.submitted-items {
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
  overflow-x: auto;
}

.submitted-items td.num,
.submitted-items th.num {
  text-align: right;
}

/* Fixed table layout to prevent column shifting */
.orders-table {
  table-layout: fixed;
  width: 100%;
}

/* Column widths */
.col-order-number {
  width: 130px;
}

.col-customer {
  width: 180px;
}

.col-items {
  width: 200px;
}

.col-status {
  width: 130px;
}

.col-date {
  width: 140px;
}

.col-value {
  width: 120px;
}

/* Items details styling */
.items-details {
  position: relative;
}

.items-summary {
  cursor: pointer;
  color: #3b82f6;
  font-weight: 500;
  list-style: none;
  user-select: none;
  display: inline-block;
}

.items-summary::-webkit-details-marker {
  display: none;
}

.items-summary::before {
  content: '▶';
  display: inline-block;
  margin-right: 0.375rem;
  font-size: 0.75rem;
  transition: transform 0.2s;
}

.items-details[open] .items-summary::before {
  transform: rotate(90deg);
}

.items-summary:hover {
  color: #2563eb;
  text-decoration: underline;
}

/* Dropdown container */
.items-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 0.5rem;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  padding: 0.75rem;
  z-index: 10;
  min-width: 300px;
  max-width: 400px;
}

.item-entry {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.5rem;
  border-bottom: 1px solid #f1f5f9;
}

.item-entry:last-child {
  border-bottom: none;
}

.item-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #0f172a;
}

.item-meta {
  font-size: 0.813rem;
  color: #64748b;
}
</style>
