export function formatPrice(value: string | number) {
  return Number(value).toLocaleString("en-US", { maximumFractionDigits: 6 })
}

export function formatSpread(value: string | number | null) {
  return value === null ? "0.00%" : `${Number(value).toFixed(3)}%`
}

export function formatDate(value: string | null) {
  if (!value) return "Never"
  return new Date(value).toLocaleString(undefined, {
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  })
}
