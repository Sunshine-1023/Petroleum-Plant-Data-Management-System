const currencyFormatter = new Intl.NumberFormat('zh-CN', {
  style: 'currency',
  currency: 'CNY',
  maximumFractionDigits: 2,
})

export function formatCurrency(value) {
  const num = Number(value)
  if (Number.isNaN(num)) return '-'
  return currencyFormatter.format(num)
}

export function formatNumber(value) {
  const num = Number(value)
  if (Number.isNaN(num)) return '-'
  return new Intl.NumberFormat('zh-CN').format(num)
}
